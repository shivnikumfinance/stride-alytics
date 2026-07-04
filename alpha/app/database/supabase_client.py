from supabase import create_client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError(
        "SUPABASE_URL and SUPABASE_KEY must be set in environment or .env file"
    )

supabase = create_client(url, key)