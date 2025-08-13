from __future__ import annotations
from typing import Callable, Awaitable, Optional
from aiohttp import web
from functools import wraps
from rubigram.types import Update, InlineMessage
from rubigram.method import Method
import asyncio
import logging

logger = logging.getLogger(__name__)


class Client(Method):
    def __init__(
        self,
        token: str,
        endpoint: Optional[str] = None,
        host: str = "0.0.0.0",
        port: int = 8000
    ):
        self.token = token
        self.port = port
        self.host = host
        self.endpoint = endpoint
        self.messages_handler: list[Callable[[Client, Update], Awaitable]] = []
        self.inlines_handler: list[Callable[[Client, InlineMessage], Awaitable]] = []
        self.routes = web.RouteTableDef()
        super().__init__(token)

    def on_message(self, *filters: Callable[[Update], bool]):
        def decorator(func: Callable[[Client, Update], Awaitable]):
            @wraps(func)
            async def wrapper(client: Client, update: Update):
                try:
                    if all(f(update) for f in filters):
                        await func(client, update)
                except Exception as e:
                    logger.exception(f"Error in message handler {func.__name__}: {e}")
            self.messages_handler.append(wrapper)
            return func
        return decorator

    def on_inline_message(self, *filters: Callable[[InlineMessage], bool]):
        def decorator(func: Callable[[Client, InlineMessage], Awaitable]):
            @wraps(func)
            async def wrapper(client: Client, update: InlineMessage):
                try:
                    if all(f(update) for f in filters):
                        await func(client, update)
                except Exception as e:
                    logger.exception(f"Error in inline handler {func.__name__}: {e}")
            self.inlines_handler.append(wrapper)
            return func
        return decorator

    async def handle_update(self, data: dict):
        if "inline_message" in data:
            event = InlineMessage.read(data["inline_message"])
            await asyncio.gather(*(h(self, event) for h in self.inlines_handler))
        elif "update" in data:
            event = Update.read(data["update"], self)
            await asyncio.gather(*(h(self, event) for h in self.messages_handler))

    async def set_endpoints(self):
        if not self.endpoint:
            return
        await self.update_bot_endpoint(f"{self.endpoint}/ReceiveUpdate", "ReceiveUpdate")
        await self.update_bot_endpoint(f"{self.endpoint}/ReceiveInlineMessage", "ReceiveInlineMessage")

    def run(self):
        @self.routes.post("/ReceiveUpdate")
        async def receive_update(request: web.Request):
            data = await request.json()
            await self.handle_update(data)
            return web.json_response({"status": "OK"})

        @self.routes.post("/ReceiveInlineMessage")
        async def receive_inline_message(request: web.Request):
            data = await request.json()
            await self.handle_update(data)
            return web.json_response({"status": "OK"})

        app = web.Application()
        app.add_routes(self.routes)

        async def on_startup(_):
            await self.set_endpoints()

        app.on_startup.append(on_startup)
        web.run_app(app, host=self.host, port=self.port)