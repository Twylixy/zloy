import asyncio
import os

import peewee
import requests
from aiogram import Bot, Dispatcher, types

from app.handlers.ban_handler import handle_ban
from app.handlers.on_message_handler import handle_on_message
from app.helpers.builders import init_database

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

chats_ids = []


async def on_startup(*args, **kwargs):
    if os.getenv("BOT_TELEGRAM_ID") is None:
        os.environ["BOT_TELEGRAM_ID"] = str((await zloy_instance.get_me()).id)
    init_database()


async def on_message(message: types.Message) -> None:
    if message.chat.id == message.from_id:
        return

    if message.chat.id not in chats_ids:
        chats_ids.append(message.chat.id)

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
        database = peewee.PostgresqlDatabase(
            host=os.getenv("DATABASE_HOST", "database"),
            port=os.getenv("DATABASE_PORT", 5432),
            user=os.getenv("DATABASE_USER", "postgres"),
            password=os.getenv("DATABASE_PASSWORD", "postgres"),
            database=os.getenv("DATABASE_NAME", "postgres"),
        )
        database.connect()
    except Exception:
        result += "Database is unreachable\n"
    finally:
        database.close()

    try:
        requests.get("https://t.me/").raise_for_status()
    except Exception:
        result += "HTTP ratelimit"

    result = result or "I'm online"

    await message.delete()
    await zloy_instance.send_message(message.from_id, result)


async def ban(message: types.Message) -> None:
    if message.chat.id == message.from_id:
        return

    member = await zloy_instance.get_chat_member(message.chat.id, message.from_id)

    if member.status != "administrator" and member.status != "creator":
        await message.delete()
        return

    await handle_ban(message, zloy_instance)


async def chats(message: types.Message) -> None:
    if message.chat.id != message.from_id:
        return

    if message.from_id != os.getenv("OWNER_ID"):
        return

    result = ""
    for num, chat_id in enumerate(chats_ids):
        chat = await zloy_instance.get_chat(chat_id)

        if chat:
            result += f"<b>{num + 1}</b> <i>{chat.title}</i> <pre>({chat.id})</pre>"
        else:
            chats_ids.pop(chat_id)

    await zloy_instance.send_message(message.from_id, result)


async def send(message: types.Message) -> None:
    if message.chat.id != message.from_id:
        return

    if message.from_id != os.getenv("OWNER_ID"):
        return

    chat_id = message.get_args()

    if not chat_id:
        return

    chat_id = chat_id.split(' ')[0]

    if int(chat_id) not in chats_ids:
        return

    text = message.text.split("\n", 1)[1]
    await zloy_instance.send_message(chat_id, text)
