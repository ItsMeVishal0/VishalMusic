from pyrogram import filters
from pyrogram.types import Message, CallbackQuery
from pyrogram.enums import ChatType, ChatMemberStatus
from VISHALMUSIC.misc import SUDOERS
from config import OWNER_ID


# ── Admin Check Functions ──

async def is_admin(message_or_cq) -> bool:
    if isinstance(message_or_cq, CallbackQuery):
        message = message_or_cq.message
    else:
        message = message_or_cq

    if not message.from_user:
        return False

    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.CHANNEL, ChatType.GROUP]:
        return False

    if message.from_user.id in [777000, 1087968824]:
        return True

    client = message._client
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]


async def is_group_owner(message_or_cq) -> bool:
    if isinstance(message_or_cq, CallbackQuery):
        message = message_or_cq.message
    else:
        message = message_or_cq

    if not message.from_user:
        return False

    if message.chat.type not in [ChatType.SUPERGROUP, ChatType.CHANNEL, ChatType.GROUP]:
        return False

    if message.from_user.id in [777000, 1087968824]:
        return True

    client = message._client
    member = await client.get_chat_member(message.chat.id, message.from_user.id)
    return member.status == ChatMemberStatus.OWNER


# ── Filters ──


def sudo_filter_func(_, __, obj: Message | CallbackQuery) -> bool:
    msg = obj.message if isinstance(obj, CallbackQuery) else obj
    return bool(
        (
            (msg.from_user and msg.from_user.id in SUDOERS)
            or (msg.sender_chat and msg.sender_chat.id in SUDOERS)
        )
        and not getattr(msg, "edit_date", False)
    )

sudo_filter = filters.create(func=sudo_filter_func, name="SudoUsersFilter")


async def admin_filter_func(_, __, obj: Message | CallbackQuery) -> bool:
    msg = obj.message if isinstance(obj, CallbackQuery) else obj
    if getattr(msg, "edit_date", False):
        return False
    return await is_admin(msg)

admin_filter = filters.create(func=admin_filter_func, name="AdminFilter")


async def group_owner_filter_func(_, __, obj: Message | CallbackQuery) -> bool:
    msg = obj.message if isinstance(obj, CallbackQuery) else obj
    if getattr(msg, "edit_date", False):
        return False
    return await is_group_owner(msg)

owner_filter = filters.create(func=group_owner_filter_func, name="GroupOwnerFilter")


def bot_owner_filter_func(_, __, obj: Message | CallbackQuery) -> bool:
    msg = obj.message if isinstance(obj, CallbackQuery) else obj
    return (
        msg.from_user
        and msg.from_user.id == OWNER_ID
        and not getattr(msg, "edit_date", False)
    )

dev_filter = filters.create(func=bot_owner_filter_func, name="BotOwnerFilter")
