from abc import ABC
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession


@dataclass
class UsuarioBase(ABC):
    empresa: UUID


class RepositorioDominioBase(ABC):
    def __init__(
        self,
        session: AsyncSession | None = None,
    ) -> None:
        if session is not None:
            self.session = session


class RepositorioConsultaBase(ABC):
    def __init__(
        self,
        session: AsyncSession | None = None,
    ) -> None:
        if session is not None:
            self.session = session
