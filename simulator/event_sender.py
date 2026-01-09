import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv(
    "BACKEND_URL",
    "http://localhost:8000/api/events"
)


async def send_event(event: dict):
    """
    Send normalized skill event to backend via HTTP.
    """
    async with httpx.AsyncClient(timeout=10) as client:
        response = await client.post(
            BACKEND_URL,
            json=event
        )
        response.raise_for_status()
        return response.json()
