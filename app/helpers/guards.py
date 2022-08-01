from dataclasses import dataclass
from enum import Enum
from typing import List

import requests
from aiogram import types


class ViolationLevel(Enum):
    NOTHING = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3


@dataclass
class ViolationReport:
    has_violations: bool
    violation_level: ViolationLevel
    has_urls: bool
    urls: List[str]
    has_user_mentions: bool
    user_mentions: List[str]
    has_channel_mentions: bool
    channel_mentions: List[str]


def inspect_message_content(message: types.Message) -> ViolationReport:
    violation_report_builder = {
        "has_violations": False,
        "violation_level": ViolationLevel.NOTHING,
        "has_urls": False,
        "urls": [],
        "has_user_mentions": False,
        "user_mentions": [],
        "has_channel_mentions": False,
        "channel_mentions": [],
    }

    violation_report = ViolationReport(**violation_report_builder)

    if not message.entities:
        return violation_report

    for entity in message.entities:
        if entity.type not in ["url", "mention", "text_link", "text_mention"]:
            continue

        if entity.type == "text_link":
            if not violation_report.has_violations:
                violation_report.has_violations = True
            if not violation_report.has_urls:
                violation_report.has_urls = True
            violation_report.urls.append(entity.url)
        elif entity.type == "text_mention":
            if not violation_report.has_user_mentions:
                violation_report.has_user_mentions = True
            violation_report.user_mentions.append(
                entity.user.first_name + entity.user.last_name
            )
        elif entity.type == "url":
            if not violation_report.has_violations:
                violation_report.has_violations = True
            if not violation_report.has_urls:
                violation_report.has_urls = True

            link = message.text[entity.offset : entity.offset + entity.length]
            violation_report.urls.append(link)
        else:
            mention = message.text[entity.offset : entity.offset + entity.length]
            link = f"https://t.me/{mention.replace('@', '')}"
            response = requests.get(link)

            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                print("can't get t.me: " + e)

            if "View in Telegram" in response.text:
                if not violation_report.has_violations:
                    violation_report.has_violations = True
                if not violation_report.has_channel_mentions:
                    violation_report.has_channel_mentions = True
                violation_report.channel_mentions.append(link)
            else:
                if not violation_report.has_user_mentions:
                    violation_report.has_user_mentions = True
                violation_report.user_mentions.append(mention)

    if (
        violation_report.has_urls or violation_report.has_channel_mentions
    ) and violation_report.has_user_mentions:
        violation_report.violation_level = ViolationLevel.HIGH
    elif violation_report.has_channel_mentions:
        violation_report.violation_level = ViolationLevel.MEDIUM
    elif violation_report.has_urls:
        violation_report.violation_level = ViolationLevel.LOW

    return violation_report
