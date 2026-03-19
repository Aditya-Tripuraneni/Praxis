.PHONY: dev test-backend test-frontend lint

dev:
	docker compose up --build

test-backend:
	cd backend && python -m pytest -v

test-frontend:
	cd frontend && npm test

lint:
	cd backend && ruff check . && ruff format --check .
	cd frontend && npx tsc --noEmit
