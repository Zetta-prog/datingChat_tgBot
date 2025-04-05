from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram.fsm.context import FSMContext

from typing import Callable, Any, Awaitable, Dict


class StateMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]):
        
        return await handler(event, data)