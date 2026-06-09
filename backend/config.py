import os
from dotenv import load_dotenv

load_dotenv()

# Google / Firebase
GOOGLE_APPLICATION_CREDENTIALS = os.getenv(
    "GOOGLE_APPLICATION_CREDENTIALS", "./service-account.json"
)
FIREBASE_PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")

# Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")

# Elasticsearch
ENV = os.getenv("ENV", "development")
ELASTIC_URL = os.getenv("ELASTIC_CLOUD_URL") or os.getenv(
    "ELASTIC_URL", "http://localhost:9200"
)
ELASTIC_API_KEY = os.getenv("ELASTIC_API_KEY")
ELASTIC_MCP_API_KEY = os.getenv("ELASTIC_MCP_API_KEY", "")
ELASTIC_INDEX_NAME = os.getenv("ELASTIC_INDEX_NAME", "sievy_posts")
ELASTIC_MCP_URL = os.getenv("ELASTIC_MCP_URL")

# Firecrawl
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")

# App
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
