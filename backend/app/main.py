import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.auth import router as auth_router
from app.api.billing import router as billing_router
from app.api.pdf import router as pdf_router
from app.api.sample import router as sample_router
from app.api.saved_tests import router as saved_tests_router
from app.api.stats import router as stats_router
from app.api.tests import router as tests_router
from app.config import settings
from app.middleware import SecurityHeadersMiddleware, TimingMiddleware
from app.rate_limiter import limiter

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)

app = FastAPI(
    title="Praxis",
    version="0.1.0",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.include_router(tests_router)
app.include_router(pdf_router)
app.include_router(auth_router)
app.include_router(billing_router)
app.include_router(stats_router)
app.include_router(sample_router)
app.include_router(saved_tests_router)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(TimingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": app.version}
