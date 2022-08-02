from aiogram.utils.executor import start_polling

from aiogram import types
from app.entrypoints import ban, dispatcher, loop, on_message, on_startup, ping

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

start_polling(
    on_startup=on_startup,
    dispatcher=dispatcher,
    loop=loop,
)
