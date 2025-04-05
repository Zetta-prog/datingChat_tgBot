import asyncio

import logging

from components.handlers.user_handlers import user_router
from components.handlers.admin_handlers import admin_router
from components.middlewares import StateMiddleware
from core.init_bot import bot, dp
from database.init_database import init_db


async def main():
    logging.basicConfig(level=logging.INFO)
    
    dp.update.middleware(StateMiddleware())
    dp.include_routers(admin_router, user_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(init_db())
    try: asyncio.run(main())
    except KeyboardInterrupt: pass