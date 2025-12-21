# simulator/event_sender.py
import httpx
import os
from dotenv import load_dotenv

load_dotenv()

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/events")

async def send_event(event: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            BACKEND_URL,
            json=event,
            headers={"Content-Type": "application/json"}
        )
        response.raise_for_status()
        return response