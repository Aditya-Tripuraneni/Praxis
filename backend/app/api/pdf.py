"""PDF download endpoint.

Uses async + dedicated thread pool so Tectonic compilation (up to 30s)
does not starve the main FastAPI thread pool that serves fast endpoints.
"""

import asyncio
import io
import logging
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from cachetools import TTLCache
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from starlette.requests import Request

from app.api.dependencies import AuthenticatedUser, require_active_subscription
from app.rate_limiter import limiter
from app.services.generation_service import generation_service
from app.services.pdf_service import PdfService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/tests", tags=["pdf"])

# PDFs expire after 30 minutes, max 64 cached
_pdf_cache: TTLCache[str, bytes] = TTLCache(maxsize=64, ttl=1800)
_pdf_cache_lock = threading.Lock()
_pdf_service = PdfService()

# Dedicated pool for PDF generation — isolates heavy Tectonic work
# from the default thread pool that handles fast endpoints.
_pdf_executor = ThreadPoolExecutor(max_workers=4, thread_name_prefix="pdf")


def _cache_key(
    test_id: str,
    include_answers: bool,
    include_solutions: bool,
    include_topics: bool,
) -> str:
    return f"{test_id}:{include_answers}:{include_solutions}:{include_topics}"


def _generate_pdf_sync(
    questions: list[dict[str, Any]],
    config: dict[str, Any],
    test_id: str,
    include_answers: bool,
    include_solutions: bool,
    include_topics: bool,
) -> bytes:
    """Synchronous PDF generation — runs in the dedicated thread pool."""
    buf = _pdf_service.generate(
        questions,
        config,
        test_id,
        include_answers,
        include_solutions,
        include_topics,
    )
    return buf.read()


@router.get("/{test_id}/pdf")
@limiter.limit("10/minute")
async def download_pdf(
    request: Request,
    test_id: str,
    include_answers: bool = True,
    include_solutions: bool = False,
    include_topics: bool = False,
    auth: AuthenticatedUser = Depends(require_active_subscription),
):
    test = generation_service.get_test_for_user(test_id, auth.profile.id)
    if test is None:
        raise HTTPException(status_code=404, detail="Test not found")

    key = _cache_key(test_id, include_answers, include_solutions, include_topics)

    with _pdf_cache_lock:
        cached = _pdf_cache.get(key)

    if cached is None:
        try:
            loop = asyncio.get_running_loop()
            cached = await loop.run_in_executor(
                _pdf_executor,
                _generate_pdf_sync,
                [q.model_dump() for q in test.questions],
                test.config.model_dump(),
                test.test_id,
                include_answers,
                include_solutions,
                include_topics,
            )
        except Exception:
            logger.exception("PDF generation failed for test_id=%s", test_id)
            raise HTTPException(status_code=500, detail="PDF generation failed")

        with _pdf_cache_lock:
            _pdf_cache[key] = cached

    return StreamingResponse(
        io.BytesIO(cached),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="test_{test_id}.pdf"',
            "Content-Length": str(len(cached)),
        },
    )
