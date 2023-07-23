import aiohttp

from loguru import logger
from pydantic import UUID4

from .schemas import MessageRequest, MessageResponse


class Client:

    def __init__(self, url: str):
        self.__url = url
        self.__logger = logger.bind(classname=self.__class__.__name__)

    async def get_user_id(self, telegram_id: int) -> UUID4 | None:
        async with aiohttp.ClientSession(self.__url) as session:
            async with session.get("/users", params={"telegram_id": telegram_id}) as response:
                if response.status == 404:
                    self.__logger.info(f"Client '{telegram_id}' not found")
                    return None
                elif response.status == 500:
                    self.__logger.error(f"Receiving user '{telegram_id}' was failed on the server side")
                    return None
                data = await response.json()
                return data.get("user_id")

    async def create_user(self, telegram_id: int) -> UUID4 | None:
        async with aiohttp.ClientSession(self.__url) as session:
            async with session.post("/users", data={"telegram_id": telegram_id}) as response:
                if response.status == 500:
                    self.__logger.error(f"Creating user '{telegram_id}' was failed on the server side")
                    return None
                data = await response.json()
                return data.get("user_id")

    async def send_message(self, message: MessageRequest) -> MessageResponse | None:
        async with aiohttp.ClientSession(self.__url) as session:
            async with session.post("/message", data=message.dict()) as response:
                if response.status == 500:
                    self.__logger.error(f"Server didn't response to user '{message.user_id}' "
                                        f"on message '{message.input_text}'")
                    return None
                data = await response.json()
                return MessageResponse(**data)
