from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    cors_origins: list[str] = ["http://localhost:5173"]
    log_level: str = "info"
    enable_docs: bool = False

    # Supabase
    supabase_url: str = ""
    supabase_anon_key: str = ""
    supabase_service_role_key: str = ""
    supabase_jwt_secret: str = ""

    # Stripe
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_student_price_id: str = ""
    stripe_tutor_price_id: str = ""

    # Frontend URL (for Stripe redirect URLs)
    frontend_url: str = "http://localhost:5173"

    # HIBP breached password check
    hibp_timeout_seconds: int = 3
    hibp_enabled: bool = True

    # Proxy trust: number of trusted reverse proxies in front of the app.
    # Render.com = 1, Render + Cloudflare = 2. Controls which X-Forwarded-For
    # entry is treated as the real client IP.
    trusted_proxy_count: int = 1

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
