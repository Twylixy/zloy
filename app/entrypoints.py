import asyncio
import os

import requests
from aiogram import Bot, Dispatcher, types

from app.handlers.ban_handler import handle_ban
from app.handlers.on_message_handler import handle_on_message
from app.helpers.builders import init_database
from app.repositories.base import BaseRepository

loop = asyncio.get_event_loop()

zloy_instance = Bot(
    token=os.getenv("TOKEN"),
    parse_mode="HTML",
    loop=loop,
)
dispatcher = Dispatcher(
    zloy_instance,
    loop=loop,
)


async def on_startup(*args, **kwargs):
    if os.getenv("BOT_TELEGRAM_ID") is None:
        os.environ["BOT_TELEGRAM_ID"] = str((await zloy_instance.get_me()).id)
    init_database()


async def on_message(message: types.Message) -> None:
    if message.chat.id == message.from_id:
        return

    await handle_on_message(message, zloy_instance)


async def ping(message: types.Message) -> None:
    if message.chat.id == message.from_id:
        return

    member = await zloy_instance.get_chat_member(message.chat.id, message.from_id)

    if member.status != "creator":
        await message.delete()
        return

    result = ""

    try:
        BaseRepository.Meta.database.connect()
    except Exception:
        result += "Database is unreachable\n"
    finally:
        BaseRepository.Meta.database.close()

    try:
        requests.get("https://t.me/").raise_for_status()
    except Exception:
        result += "HTTP ratelimit"

    result = result or "I'm online"
    await zloy_instance.send_message(message.from_id, result)


async def ban(message: types.Message) -> None:
    if message.chat.id == message.from_id:
        return

    member = await zloy_instance.get_chat_member(message.chat.id, message.from_id)

    if member.status != "administrator" or member.status != "creator":
        await message.delete()
        return

    await handle_ban(message, zloy_instance)
