# src/db/pg_repositoryUser.py

import logging
from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from passlib.context import CryptContext # Для хеширования паролей

from sensory_data_client.db.users import UserORM
from sensory_data_client.db.base import get_session
from sensory_data_client.exceptions import DatabaseError

logger = logging.getLogger(__name__)

# Контекст для работы с паролями, лучше вынести в общий auth-модуль, но для простоты здесь
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    """Создает хеш из обычного пароля."""
    return pwd_context.hash(password)


class UserRepository:
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def create_user(self, email: str, plain_password: str) -> UserORM:
        """
        Создает нового пользователя с хешированным паролем.
        """
        hashed_password = get_password_hash(plain_password)
        new_user = UserORM(email=email, hashed_password=hashed_password)

        async for session in get_session(self._session_factory):
            try:
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                return new_user
            except IntegrityError as e:
                await session.rollback()
                # Перевыбрасываем как кастомное исключение, чтобы API мог его поймать
                raise DatabaseError(f"User with email {email} already exists.") from e
            except SQLAlchemyError as e:
                await session.rollback()
                raise DatabaseError(f"Failed to create user: {e}") from e

    async def get_by_id(self, user_id: UUID) -> Optional[UserORM]:
        """Находит пользователя по его UUID."""
        async for session in get_session(self._session_factory):
            result = await session.execute(select(UserORM).where(UserORM.id == user_id))
            return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[UserORM]:
        """Находит пользователя по email."""
        async for session in get_session(self._session_factory):
            result = await session.execute(select(UserORM).where(UserORM.email == email))
            return result.scalar_one_or_none()