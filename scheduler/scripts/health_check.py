"""
Perform health checks on all services.
Scheduled: Every 5 minutes
"""
import os
import httpx
from dotenv import load_dotenv

load_dotenv()


def main():
    api_url = os.getenv("API_URL", "http://localhost:8000")

    try:
        r = httpx.get(f"{api_url}/api/v1/health", timeout=10)
        r.raise_for_status()
        print(f"✓ API health check passed: {r.json()}")
    except Exception as e:
        print(f"✗ API health check failed: {e}")
        exit(1)

    print("✓ All health checks passed")


if __name__ == "__main__":
    main()