from aiogram import Bot, types


async def handle_ban(message: types.Message, zloy: Bot) -> None:
    if message.reply_to_message is None:
        await message.reply("Target message is required")
        return

    reason = message.text.replace("/ban", "")[1:] or "Not provided"
    target_user = message.reply_to_message.from_user
    target_user_message = message.reply_to_message

    if target_user is None or target_user_message is None:
        await message.reply("Can't fetch target")
        return

    if not target_user_message.sender_chat is None:
        await zloy.ban_chat_sender_chat(
            message.chat.id,
            target_user_message.sender_chat.id,
        )
        await zloy.send_message(
            message.chat.id,
            f"""
🚫 <b>Блокировка</b>
🌐 <i>Источник</i>: <b><a href="tg://user?id={target_user_message.sender_chat.id}">{target_user_message.sender_chat.title}</a></b>
🛡 <i>Администратор</i>: <b><a href="tg://user?id={message.from_id}">{message.from_user.full_name}</a></b>
📜 <i>Причина</i>: <code>{reason}</code>

<i>Блокировка являяется вечной, не подлежит снятию.</i>

meta #b_{target_user_message.sender_chat.title} #b_{target_user_message.sender_chat.id}
            """,
            reply_to_message_id=target_user_message.message_id,
        )
    else:
        await zloy.ban_chat_member(message.chat.id, target_user.id)
        await zloy.send_message(
            message.chat.id,
            f"""
🚫 <b>Блокировка</b>
👤 <i>Пользователь</i>: <b><a href="tg://user?id={target_user.id}">{target_user.full_name}</a></b>
🛡 <i>Администратор</i>: <b><a href="tg://user?id={message.from_id}">{message.from_user.full_name}</a></b>
📜 <i>Причина</i>: <code>{reason}</code>

<i>Блокировка являяется вечной, не подлежит снятию.</i>

meta #b_{target_user.first_name} #b_{target_user.id}
            """,
            reply_to_message_id=target_user_message.message_id,
        )

    try:
        await target_user_message.delete()
    except:
        pass
    await message.delete()
