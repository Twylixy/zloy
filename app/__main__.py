from aiogram import types
from aiogram.utils.executor import start_polling

from app.entrypoints import (
    ban,
    dispatcher,
    loop,
    on_message,
    on_startup,
    ping,
    chats,
    send,
)

dispatcher.register_message_handler(
    ping,
    commands=["ping"],
    content_types=types.ContentType.TEXT,
)
dispatcher.register_message_handler(
    ban,
    commands=["ban"],
    content_types=types.ContentType.TEXT,
)
dispatcher.register_message_handler(
    on_message,
    content_types=types.ContentType.ANY,
)
dispatcher.register_message_handler(
    chats,
    content_types=types.ContentType.TEXT,
)
dispatcher.register_message_handler(
    send,
    content_types=types.ContentType.TEXT,
)

start_polling(
    on_startup=on_startup,
    dispatcher=dispatcher,
    loop=loop,
)
