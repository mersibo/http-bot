from apscheduler.schedulers.asyncio import AsyncIOScheduler
import json
import os
from aiogram import Bot
from services.github_client import GitHubClient
from services.stackoverflow_client import StackOverflowClient
from services.api_client import send_update

DATA_FILE = "data/tracked_links.json"

async def check_updates(bot: Bot):
    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    github_client = GitHubClient()
    so_client = StackOverflowClient()

    for chat_id, links in data.items():
        for link in links:
            if "github.com" in link:
                parts = link.split("/")
                repo_owner, repo_name = parts[-2], parts[-1]
                repo_data = await github_client.fetch_repo(repo_owner, repo_name)
                if repo_data:
                    await send_update(chat_id, link, f"Обновления в {repo_name}: {repo_data['updated_at']}")
                    await bot.send_message(chat_id, f"Обновления в {repo_name}: {repo_data['updated_at']}")

            elif "stackoverflow.com" in link:
                question_id = link.split("/")[-1]
                question_data = await so_client.fetch_question(int(question_id))
                if question_data:
                    await bot.send_message(chat_id, f"Обновления в вопросе: {question_data['items'][0]['last_activity_date']}")

def setup_scheduler(bot: Bot):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(check_updates, "interval", minutes=5, args=[bot])
    scheduler.start()
