from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PayPrint Server"
    app_version: str = "2.1.0"
    environment: str = "development"

    host: str = "127.0.0.1"
    port: int = 8000

    database_url: str = ""

    razorpay_key_id: str = ""
    razorpay_key_secret: str

    jwt_secret: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


settings = Settings()
