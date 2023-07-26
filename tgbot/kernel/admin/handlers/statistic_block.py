from aiogram.types import CallbackQuery
from aiogram import F, Router

from create_bot import bot, config
from tgbot.kernel.admin.filters import AdminFilter
from tgbot.kernel.admin.inline import AdminInlineKeyboard
from tgbot.kernel.admin.render import week_statistic_render

router = Router()
router.message.filter(AdminFilter())
router.callback_query.filter(AdminFilter())

inline = AdminInlineKeyboard()

admin_ids = config.tg_bot.admin_ids


@router.callback_query(F.data == "statistic")
async def statistic_block(callback: CallbackQuery):
    await week_statistic_render(user_id=callback.from_user.id)
    await bot.answer_callback_query(callback.id)
