import asyncio

from tgbot.kernel.echo import router as echo_router

from tgbot.kernel.admin.handlers.main_block import router as admin_main_router
from tgbot.kernel.admin.handlers.accounts_block import router as admin_accounts_router
from tgbot.kernel.admin.handlers.workers_block import router as admin_workers_router
from tgbot.kernel.admin.handlers.statistic_block import router as admin_statistic_router

from tgbot.kernel.moderator.handlers.main_block import router as moderator_main_router
from tgbot.kernel.moderator.handlers.order_block import router as moderator_order_router
from tgbot.kernel.moderator.handlers.support_block import router as moderator_support_router

from tgbot.kernel.worker.handlers.main_block import router as worker_main_router
from tgbot.kernel.worker.handlers.settings_block import router as worker_settings_router
from tgbot.kernel.worker.handlers.order_block import router as worker_order_router
from tgbot.kernel.worker.handlers.statistic_block import router as worker_statistic_router
from tgbot.kernel.worker.handlers.support_block import router as worker_support_router

from tgbot.kernel.client.handlers.main_block import router as client_main_router
from tgbot.kernel.client.handlers.order_block import router as client_order_router
from tgbot.kernel.client.handlers.support_block import router as client_support_router

from tgbot.models.redis_connector import RedisConnector as rds

from create_bot import bot, dp, scheduler, logger, register_global_middlewares, config
from tgbot.services.scheduler import CreateTask

admin_router = [
    admin_main_router,
    admin_accounts_router,
    admin_workers_router,
    admin_statistic_router
]
moderator_router = [
    moderator_main_router,
    moderator_order_router,
    moderator_support_router
]
worker_router = [
    worker_main_router,
    worker_settings_router,
    worker_order_router,
    worker_statistic_router,
    worker_support_router
]
client_router = [
    client_main_router,
    client_order_router,
    client_support_router
]


async def main():
    logger.info("Starting bot")
    await CreateTask.start_scheduler()
    rds.redis_start()
    dp.include_routers(
        *admin_router,
        *moderator_router,
        *worker_router,
        *client_router,
        echo_router
    )

    try:
        scheduler.start()
        register_global_middlewares(dp, config)
        await dp.start_polling(bot)
    finally:
        await dp.storage.close()
        await bot.session.close()
        scheduler.shutdown(True)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.error("Bot stopped!")
