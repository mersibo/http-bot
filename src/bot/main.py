from telethon import TelegramClient, events
import json
import os
import asyncio
import time
from services.github_client import GitHubClient
from services.stackoverflow_client import StackOverflowClient

API_ID = os.getenv("BOT_API_ID")  
API_HASH = os.getenv("BOT_API_HASH")  
BOT_TOKEN = os.getenv("BOT_TOKEN")  

bot = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

DATA_FILE = "data/tracked_links.json"

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, "w") as f:
        json.dump({}, f)

def load_data():
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

user_states = {}

@bot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.respond("Привет! Я бот для отслеживания ссылок.\nИспользуйте /help, чтобы узнать команды.")

@bot.on(events.NewMessage(pattern="/help"))
async def help(event):
    await event.respond(
        "Доступные команды:\n"
        "/track - начать отслеживание ссылки\n"
        "/untrack - прекратить отслеживание\n"
        "/list - показать список отслеживаемых ссылок"
    )

@bot.on(events.NewMessage(pattern="/track"))
async def track(event):
    user_states[event.chat_id] = "waiting_link"
    await event.respond("Введите ссылку для отслеживания:")

@bot.on(events.NewMessage)
async def handle_track(event):
    chat_id = event.chat_id
    state = user_states.get(chat_id)

    if state == "waiting_link":
        link = event.text.strip()
        data = load_data()

        if chat_id not in data:
            data[chat_id] = []

        if link in data[chat_id]:
            await event.respond("Ссылка уже отслеживается!")
        else:
            data[chat_id].append(link)
            save_data(data)
            await event.respond(f"Ссылка {link} добавлена в отслеживаемые.")

        user_states.pop(chat_id)

@bot.on(events.NewMessage(pattern="/untrack"))
async def untrack(event):
    data = load_data()
    chat_id = event.chat_id

    if chat_id not in data or not data[chat_id]:
        await event.respond("Вы пока не отслеживаете ссылки.")
        return

    user_states[chat_id] = "waiting_untrack"
    await event.respond("Введите ссылку, которую хотите удалить из отслеживаемых:")

@bot.on(events.NewMessage)
async def handle_untrack(event):
    chat_id = event.chat_id
    state = user_states.get(chat_id)

    if state == "waiting_untrack":
        link = event.text.strip()
        data = load_data()

        if link in data.get(chat_id, []):
            data[chat_id].remove(link)
            save_data(data)
            await event.respond(f"Ссылка {link} больше не отслеживается.")
        else:
            await event.respond("Этой ссылки нет в списке.")

        user_states.pop(chat_id)

@bot.on(events.NewMessage(pattern="/list"))
async def list_links(event):
    data = load_data()
    chat_id = event.chat_id

    if chat_id not in data or not data[chat_id]:
        await event.respond("Вы пока не отслеживаете ссылки.")
    else:
        links = "\n".join(data[chat_id])
        await event.respond(f"Ваши отслеживаемые ссылки:\n{links}")

last_updates = {}

async def check_updates():
    while True:
        data = load_data()

        for chat_id, links in data.items():
            for link in links:
                new_update = None

                if "github.com" in link:
                    new_update = GitHubClient.get_last_update(link)
                elif "stackoverflow.com" in link:
                    question_id = link.split("/")[-1] 
                    new_update = StackOverflowClient.get_last_update(question_id)

                if new_update:
                    last_update_time = last_updates.get(link)

                    if not last_update_time or new_update > last_update_time:
                        last_updates[link] = new_update
                        await bot.send_message(chat_id, f"🔔 Обновление по ссылке: {link}")

        await asyncio.sleep(3600)  
async def main():
    asyncio.create_task(check_updates()) 
    await bot.run_until_disconnected()

if __name__ == "__main__":
    bot.loop.run_until_complete(main())
