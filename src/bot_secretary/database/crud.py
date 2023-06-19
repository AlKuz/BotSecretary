from enum import Enum
from pydantic import EmailStr
from sqlalchemy import func, select, insert, update
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine

from .models import User, Role, Message, MessageType


class RoleMap(str, Enum):
    admin = "admin"
    user = "user"


class MessageTypeMap(str, Enum):
    human = "human"
    assistant = "bot"


class CRUD:

    def __init__(self, database: str | AsyncEngine):
        engine = create_async_engine(database) if isinstance(database, str) else database
        self.__session = AsyncSession(engine)

    @staticmethod
    async def __get_or_create_role(session: AsyncSession, role: RoleMap) -> int:
        if not Role(name=role.value).is_exist:
            await session.execute(insert(Role).values(name=role.value))
        response = await session.execute(select(Role.id).where(Role.name == role.value))
        return await response.scalars().first()

    @staticmethod
    async def __get_or_create_message_type(session: AsyncSession, message_type: MessageTypeMap) -> int:
        if not MessageType(type=message_type.value).is_exist:
            await session.execute(insert(MessageType).values(type=message_type.value))
        response = await session.execute(select(MessageType.id).where(MessageType.type == message_type.value))
        return await response.scalars().first()

    async def create_user(self, telegram_id: int, role: RoleMap = RoleMap.user):
        async with self.__session:
            role_id = self.__get_or_create_role(self.__session, role)
            self.__session.add(User(telegram_id=telegram_id, role_id=role_id))
            await self.__session.commit()

    async def is_user_exist(self, telegram_id) -> bool:
        async with self.__session:
            response = await self.__session.execute(select(User.id).where(User.telegram_id == telegram_id))
            user_id = await response.scalars().first()
            return user_id is not None

    async def count_users(self) -> int:
        async with self.__session:
            query = self.__session.query(func.count(User))
            result = await self.__session.execute(query)
            return result.scalars().first()

    async def create_message(self,
                             content: str,
                             telegram_id: int,
                             message_type: MessageTypeMap,
                             responding_to: int | None = None) -> int:
        async with self.__session:
            user = User(telegram_id=telegram_id)
            await self.__session.refresh(user)
            message_type_id = self.__get_or_create_message_type(self.__session, message_type)
            new_message = Message(
                content=content,
                user_id=user.id,
                message_type_id=message_type_id,
                responding_to=responding_to)
            self.__session.add(new_message)
            await self.__session.commit()
            await self.__session.refresh(new_message)
            return new_message.id

    async def add_user_email(self, telegram_id: int, email: EmailStr):
        async with self.__session:
            await self.__session.execute(update(User).values(email=email).where(User.telegram_id == telegram_id))
