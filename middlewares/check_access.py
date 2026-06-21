from typing import Callable, Dict, Any, Awaitable, Union
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from data.db_manager import check_user_is_allowed
from handlers.routes import add_user_message


class IsAllowedMiddleware(BaseMiddleware):
    PUBLIC_COMMANDS = [
        '/start',
        '/help',
        '/about',
        '/allow',
    ]

    async def __call__(
            self,
            handler: Callable[[Union[Message, CallbackQuery], Dict[str, Any]], Awaitable[Any]],
            event: Union[Message, CallbackQuery],
            data: Dict[str, Any]
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id
            text = event.text
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            text = event.data
        else:
            return await handler(event, data)

        if isinstance(event, Message) and text:
            for msg in self.PUBLIC_COMMANDS:
                if text.startswith(msg):
                    return await handler(event, data)

        if not check_user_is_allowed(user_id):
            if isinstance(event, Message):
                await event.answer(
                    f"🚫 Вы не можете пользоваться ботом.\nВаш ID: `{user_id}`\nСкопируйте этот ID и отправьте администратору.",
                parse_mode="Markdown"
                )
            elif isinstance(event, CallbackQuery):
                await event.message.answer(
                    f"🚫 Вы не можете пользоваться ботом.\nВаш ID: `{user_id}`\nСкопируйте этот ID и отправьте администратору.",
                parse_mode="Markdown"
                )
            return

        return await handler(event, data)