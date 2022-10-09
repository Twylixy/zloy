import os
from typing import Optional

from aiogram import Bot, types

from app.helpers.guards import inspect_message_content
from app.repositories.violations import ViolationRepository


async def handle_on_message(message: types.Message, zloy: Bot) -> None:
    member = await zloy.get_chat_member(message.chat.id, message.from_id)
    violation_report = inspect_message_content(message)
    violations_level_count = 0
    message_text = message.text or message.caption

    if violation_report.has_violations is False:
        if (("#v_" in message_text) or ("#b_" in message_text)) and (
            member.status != "creator"
        ):
            await zloy.send_message(
                message.chat.id,
                text=f'❗️ <b><a href="tg://user?id={message.from_id}">{message.from_user.full_name}</a>, вы не можете использовать в сообщении Meta-теги (#b_ или #v_).</b>',
                reply_to_message_id=message.message_id,
            )
            await message.delete()
        return

    if member.status == "creator" or member.status == "administrator":
        return

    ViolationRepository.create(
        telegram_id=message.from_id,
        admin_telegram_id=os.getenv("BOT_TELEGRAM_ID"),
        violation_level=violation_report.violation_level.value,
        has_urls=violation_report.has_urls,
        urls=" ".join(violation_report.urls),
        has_user_mentions=violation_report.has_user_mentions,
        user_mentions=" ".join(violation_report.user_mentions),
        has_channel_mentions=violation_report.has_channel_mentions,
        channel_mentions=" ".join(violation_report.channel_mentions),
        reason=violation_report.reason,
    )

    violations: Optional[ViolationRepository] = ViolationRepository.select().where(
        ViolationRepository.telegram_id == message.from_id,
    )

    if violations is not None:
        for violation in violations:  # type: ignore
            violations_level_count += violation.violation_level

    issue_ban = violations_level_count >= int(os.getenv("VIOLATIONS_LIMIT", 15))

    if not message.sender_chat is None:
        ban_message = f"""
🚫 <b>Блокировка</b>

🌐 <i>Источник</i>: <b>{message.sender_chat.title}</b>
🛡 <i>Администратор</i>: <b><a href="tg://user?id={os.getenv('BOT_TELEGRAM_ID')}">🔥 Zloy</a></b>
📜 <i>Причина</i>: <code>{violation_report.reason}</code>

<i>Блокировка являяется вечной, не подлежит снятию.</i>

meta #b_{message.sender_chat.title.replace(' ', '_')} #b_{message.sender_chat.id}
        """

        violation_message = f"""
⚠️ <b>Нарушение ({violations_level_count}/{os.getenv("VIOLATIONS_LIMIT")})</b>

🌐 <i>Источник</i>: <b>{message.sender_chat.title}</b>
🛡 <i>Администратор</i>: <b><a href="tg://user?id={os.getenv('BOT_TELEGRAM_ID')}">🔥 Zloy</a></b>
📜 <i>Причина</i>: <code>{violation_report.reason}</code>

📌 <b><a href="{os.getenv("RULES_LINK")}">Правила</a></b>

<i>Последующие нарушения приведут к блокировке</i>

meta #v_{message.sender_chat.title.replace(' ', '_')} #v_{message.sender_chat.id}
        """

        await zloy.send_message(
            message.chat.id,
            text=violation_message,
            reply_to_message_id=message.message_id,
            disable_web_page_preview=True,
        )

        if issue_ban:
            await zloy.ban_chat_sender_chat(message.chat.id, message.sender_chat.id)
            await zloy.send_message(
                message.chat.id,
                text=ban_message,
                reply_to_message_id=message.message_id,
            )
    else:
        ban_message = f"""
🚫 <b>Блокировка</b>

👤 <i>Пользователь</i>: <b><a href="tg://user?id={message.from_id}">{message.from_user.full_name}</a></b>
🛡 <i>Администратор</i>: <b><a href="tg://user?id={os.getenv('BOT_TELEGRAM_ID')}">🔥 Zloy</a></b>
📜 <i>Причина</i>: <code>{violation_report.reason}</code>

<i>Блокировка являяется вечной, не подлежит снятию</i>

meta #b_{message.from_user.full_name.replace(' ', '_')} #b_{message.from_id}
        """

        violation_message = f"""
⚠️ <b>Нарушение ({violations_level_count}/{os.getenv("VIOLATIONS_LIMIT")})</b>

👤 <i>Пользователь</i>: <b><a href="tg://user?id={message.from_id}">{message.from_user.full_name}</a></b>
🛡 <i>Администратор</i>: <b><a href="tg://user?id={os.getenv('BOT_TELEGRAM_ID')}">🔥 Zloy</a></b>
📜 <i>Причина</i>: <code>{violation_report.reason}</code>

📌 <b><a href="{os.getenv("RULES_LINK")}">Правила</a></b>

<i>Последующие нарушения приведут к блокировке</i>

meta #v_{message.from_user.full_name.replace(' ', '_')} #v_{message.from_id} {violation_report.violation_level.value}
        """

        await zloy.send_message(
            message.chat.id,
            text=violation_message,
            reply_to_message_id=message.message_id,
            disable_web_page_preview=True,
        )

        if issue_ban:
            await zloy.ban_chat_member(message.chat.id, message.from_id)
            await zloy.send_message(
                message.chat.id,
                text=ban_message,
                reply_to_message_id=message.message_id,
            )

    await message.delete()
    return
