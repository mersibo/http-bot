import aiohttp
import os

SCRAPPER_URL = os.getenv("SCRAPPER_URL", "http://localhost:8000")

async def send_update(chat_id: int, link: str, update_text: str):
    async with aiohttp.ClientSession() as session:
        payload = {
            "chat_id": chat_id,
            "link": link,
            "update_text": update_text
        }
        async with session.post(f"{SCRAPPER_URL}/api/v1/updates", json=payload) as response:
            return await response.json()
