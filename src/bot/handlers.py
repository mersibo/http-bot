from aiogram import Router, types, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
import json
import os

router = Router()
DATA_FILE = "data/tracked_links.json"

class TrackState(StatesGroup):
    waiting_for_link = State()
    waiting_for_tags = State()
    waiting_for_filters = State()

@router.message(Command("track"))
async def cmd_track(message: types.Message, state: FSMContext):
    await message.answer("Введите ссылку для отслеживания:")
    await state.set_state(TrackState.waiting_for_link)

@router.message(TrackState.waiting_for_link)
async def process_link(message: types.Message, state: FSMContext):
    await state.update_data(link=message.text.strip())
    await message.answer("Введите теги (разделяйте пробелами) или отправьте `-`, если не нужны:")
    await state.set_state(TrackState.waiting_for_tags)

@router.message(TrackState.waiting_for_tags)
async def process_tags(message: types.Message, state: FSMContext):
    tags = message.text.strip()
    if tags == "-":
        tags = []

    await state.update_data(tags=tags.split())

    await message.answer("Введите фильтры (пример: `user:dummy type:comment`) или `-`, если не нужны:")
    await state.set_state(TrackState.waiting_for_filters)

@router.message(TrackState.waiting_for_filters)
async def process_filters(message: types.Message, state: FSMContext):
    filters = message.text.strip()
    if filters == "-":
        filters = ""

    user_data = await state.get_data()
    link = user_data["link"]
    tags = user_data["tags"]

    if not os.path.exists(DATA_FILE):
        os.makedirs("data", exist_ok=True)
        with open(DATA_FILE, "w") as f:
            json.dump({}, f)

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    chat_id = str(message.chat.id)
    if chat_id not in data:
        data[chat_id] = []

    if link in data[chat_id]:
        await message.answer("Ссылка уже отслеживается!")
    else:
        data[chat_id].append({"link": link, "tags": tags, "filters": filters})
        with open(DATA_FILE, "w") as f:
            json.dump(data, f)
        await message.answer(f"Ссылка {link} добавлена в отслеживание с тегами {tags} и фильтрами `{filters}`.")

    await state.clear()
