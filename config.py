import os
from dotenv import load_dotenv

load_dotenv()                      # reads .env into environment variables

GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN")
SERPER_API_KEY = os.getenv("SERPER_API_KEY")

if not GITHUB_TOKEN or not SERPER_API_KEY:
    raise RuntimeError("Missing API keys ‑ check your .env file")
