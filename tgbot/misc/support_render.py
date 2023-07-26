from typing import List

from aiogram.types import Message

from create_bot import bot
from tgbot.kernel.moderator.inline import ModeratorOrderInlineKeyboard

inline = ModeratorOrderInlineKeyboard()


async def support_render(title: str, album: List[Message], message: Message, target_id: str, sender_id: str | int):
    if album:
        media_list = []
        for msg in album:
            if msg.photo:
                file_id = msg.photo[-1].file_id
            else:
                obj_dict = msg.dict()
                file_id = obj_dict[msg.content_type]['file_id']
            type_obj = msg.content_type
            media_dict = dict(type=type_obj,  media=file_id)
            media_list.append(media_dict)
        text = f"{title}\n{'-' * 15}\n{album[0].caption}"
        await bot.send_media_group(chat_id=target_id, media=media_list)
    elif message.text:
        text = f"{title}\n{'-' * 15}\n{message.html_text}"
    else:
        if message.photo:
            file_id = message.photo[-1].file_id
            await bot.send_photo(chat_id=target_id, photo=file_id)
        elif message.video:
            await bot.send_video(chat_id=target_id, video=message.video.file_id)
        elif message.document:
            await bot.send_document(chat_id=target_id, document=message.document.file_id)
        text = f"{title}\n{'-' * 15}\n{message.caption}"
    kb = inline.answer_kb(sender_id=sender_id)
    await bot.send_message(chat_id=target_id, text=text, reply_markup=kb)
