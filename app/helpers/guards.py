from ctypes import Union
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, List

import requests
from aiogram import types
from bs4 import BeautifulSoup
import re

re_exp = r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s]{2,}|www\.[a-zA-Z0-9]+\.[^\s]{2,})"


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
    reason: str


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
        "reason": "",
    }

    violation_report = ViolationReport(**violation_report_builder)

    if message.caption and not message.text:
        message_entities = message.caption_entities
        message_text = message.caption
    else:
        message_entities = message.entities
        message_text = message.text

    if not message_entities:
        return violation_report

    for entity in message_entities:
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
            violation_report.user_mentions.append(entity.user.full_name)
        elif entity.type == "url":
            if not violation_report.has_violations:
                violation_report.has_violations = True
            if not violation_report.has_urls:
                violation_report.has_urls = True

            link = message_text[entity.offset : entity.offset + entity.length]
            violation_report.urls.append(link)
        else:
            mention = message_text[entity.offset : entity.offset + entity.length]
            link = f"https://t.me/{mention.replace('@', '')}"
            response = requests.get(link)

            try:
                response.raise_for_status()
            except requests.HTTPError as e:
                print(f"can't get t.me: {e}")

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

    if violation_report.has_violations is False:
        profile_links = inspect_user_profile(message.from_user)
        
        if profile_links is not None:
            violation_report.has_violations = True
            violation_report.urls = profile_links
            violation_report.reason = "URL(s)"
            violation_report.violation_level = ViolationLevel.MEDIUM

    if (
        violation_report.has_urls or violation_report.has_channel_mentions
    ) and violation_report.has_user_mentions:
        violation_report.violation_level = ViolationLevel.HIGH
        violation_report.reason = "URL(s) and channel mention(s)"
    elif violation_report.has_channel_mentions:
        violation_report.violation_level = ViolationLevel.MEDIUM
        violation_report.reason = "Channel mention(s)"
    elif violation_report.has_urls:
        violation_report.violation_level = ViolationLevel.LOW
        violation_report.reason = "URL(s)"

    return violation_report


def inspect_user_profile(user: types.User) -> Optional[List[str]]:
    response = requests.get(f"https://t.me/{user.username}")

    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print(f"can't get t.me: {e}")

    soup = BeautifulSoup(response.text, "html.parser")
    description = soup.find("div", class_="tgme_page_description")

    if description is None:
        return None

    urls = re.findall(re_exp, description.text)

    if urls is None:
        return None
    return urls
