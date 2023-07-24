import asyncio

from tgbot.kernel.echo import router as echo_router
from tgbot.kernel.admin.handlers.main_block import router as admin_main_router
from tgbot.kernel.admin.handlers.accounts_block import router as admin_accounts_router
from tgbot.kernel.moderator.handlers.main_block import router as moderator_main_router
from tgbot.kernel.worker.handlers.main_block import router as worker_main_router
from tgbot.kernel.worker.handlers.settings_block import router as worker_settings_router
from tgbot.kernel.worker.handlers.order_block import router as worker_order_router
from tgbot.kernel.client.handlers.main_block import router as client_main_router
from tgbot.kernel.client.handlers.order_block import router as client_order_router
# from tgbot.services.scheduler import scheduler_jobs
from tgbot.models.redis_connector import RedisConnector as rds

from create_bot import bot, dp, scheduler, logger, register_global_middlewares, config
from tgbot.services.scheduler import Functions, CreateTask

admin_router = [
    admin_main_router,
    admin_accounts_router
]
moderator_router = [
    moderator_main_router
]
worker_router = [
    worker_main_router,
    worker_settings_router,
    worker_order_router
]
client_router = [
    client_main_router,
    client_order_router
]


async def main():
    logger.info("Starting bot")
    await Functions.update_jwt()
    await CreateTask.update_jwt()
    # scheduler_jobs()
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
        # await bot.delete_webhook(drop_pending_updates=True)
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
