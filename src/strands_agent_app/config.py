import os
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = ROOT_DIR / ".env"
if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)


class Settings:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "").strip()
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash").strip()
    GEMINI_ENDPOINT: str = os.getenv("GEMINI_ENDPOINT", "https://generativelanguage.googleapis.com/v1beta").strip()
    GEMINI_METHOD: str = os.getenv("GEMINI_METHOD", "generateContent").strip()
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.7"))
    AMAZON_COUNTRY_CODE: str = os.getenv("AMAZON_COUNTRY_CODE", "in").strip().lower()
    AMAZON_MAX_REVIEW_PAGES: int = int(os.getenv("AMAZON_MAX_REVIEW_PAGES", "1"))
    AMAZON_REQUEST_TIMEOUT: int = int(os.getenv("AMAZON_REQUEST_TIMEOUT", "15"))
    AMAZON_USER_AGENT: str = os.getenv(
        "AMAZON_USER_AGENT",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    ).strip()

    @property
    def gemini_url(self) -> str:
        endpoint = self.GEMINI_ENDPOINT.rstrip("/")
        if ":" in endpoint.split("/")[-1]:
            return endpoint
        if endpoint.endswith("/models"):
            return f"{endpoint}/{self.GEMINI_MODEL}:{self.GEMINI_METHOD}"
        if endpoint.endswith(self.GEMINI_MODEL):
            return f"{endpoint}:{self.GEMINI_METHOD}"
        return f"{endpoint}/models/{self.GEMINI_MODEL}:{self.GEMINI_METHOD}"


settings = Settings()
