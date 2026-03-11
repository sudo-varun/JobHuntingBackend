
import os
from dotenv import load_dotenv

load_dotenv()

def get_sqlite_uri():
    return os.environ.get("SQLALCHEMY_DATABASE_URI", "sqlite:///job_hunting.db")

def get_openai_api_key():
    return os.environ.get("OPENAI_API_KEY", "")

def get_tavily_api_key():
    return os.environ.get("TAVILY_API_KEY", "")