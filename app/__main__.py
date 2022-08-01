from aiogram.utils.executor import start_polling

from app.entrypoints import ban, dispatcher, loop, on_message, on_startup, ping

dispatcher.register_message_handler(ping, commands=["ping"])
dispatcher.register_message_handler(ban, commands=["ban"])
dispatcher.register_message_handler(on_message)

start_polling(
    on_startup=on_startup,
    dispatcher=dispatcher,
    loop=loop,
)
