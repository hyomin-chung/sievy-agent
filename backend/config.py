import os
from dotenv import load_dotenv

load_dotenv()


class AppConfig:
    # Google / Firebase
    GOOGLE_APPLICATION_CREDENTIALS: str = os.getenv(
        "GOOGLE_APPLICATION_CREDENTIALS", "./service-account.json"
    )
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID")

    # Gemini
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

    # Elasticsearch
    ENV: str = os.getenv("ENV", "development")
    ELASTIC_URL: str = (
        os.getenv("ELASTIC_CLOUD_URL")
        if os.getenv("ENV") == "production"
        else os.getenv("ELASTIC_URL")
    )
    ELASTIC_API_KEY: str = os.getenv("ELASTIC_API_KEY")
    ELASTIC_INDEX_NAME: str = os.getenv("ELASTIC_INDEX_NAME", "sievy_posts")

    # Firecrawl
    FIRECRAWL_API_KEY: str = os.getenv("FIRECRAWL_API_KEY")

    # Feed
    MAX_PAGES: int = int(os.getenv("MAX_PAGES", "3"))
    LISTING_LIMIT: int = int(os.getenv("LISTING_LIMIT", "25"))

    # App
    BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:5173")


config = AppConfig()
