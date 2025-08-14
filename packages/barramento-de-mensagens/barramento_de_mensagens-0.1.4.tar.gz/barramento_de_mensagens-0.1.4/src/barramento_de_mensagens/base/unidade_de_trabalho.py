from __future__ import annotations
from abc import ABC
from typing import Callable, Any, Generator
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from barramento_de_mensagens.base.entidades import (
    RepositorioDominioBase,
    RepositorioConsultaBase,
    UsuarioBase,
)


class UnidadeDeTrabalhoSchemaComProblema(Exception):
    pass


class TentandoAbrirUOWContextoJaAberto(Exception):
    pass


class UnidadeDeTrabalhoAbstrata(ABC):
    domain_repo: RepositorioDominioBase
    view_repo: RepositorioConsultaBase
    domain_repo_class: type[RepositorioDominioBase]
    view_repo_class: type[RepositorioConsultaBase]
    seen: set
    commited: bool
    session: AsyncSession
    session_leitura: AsyncSession
    usuario: UsuarioBase | None
    schema: str | None = None
    criar_schema: bool = False

    eventos_fora_de_agregado: list["Evento"] = []  # noqa: F821

    def __init__(
        self,
        session_factory: Callable,
        usuario: UsuarioBase | None = None,  # noqa: F821
        schema: str | None = None,
        criar_schema: bool = False,
    ) -> None:
        self.sql_session_factory = session_factory  # type: ignore[truthy-function]
        self.usuario = usuario
        self.criar_schema = criar_schema

        if (
            all(
                [
                    schema,
                    usuario,
                    str(usuario.empresa) != str(schema),  # type: ignore[union-attr]
                ]
            )
            and not criar_schema
        ):
            raise UnidadeDeTrabalhoSchemaComProblema(
                "O usuário não pertence a esse schema."
            )

        if not self.usuario:
            raise UnidadeDeTrabalhoSchemaComProblema(  # todo melhorar
                "Toda unidade de trabalho deve ter um usuario. "
                "Passe um usuário para a UnidadeDeTrabalho"
            )

        self.schema = schema or str(self.usuario.empresa)

        self.__contexto_ativo = False
        self.eventos_fora_de_agregado = []

    def __call__(
        self,
        repo_por_dominio: "Dominio" = None,  # noqa: F821
    ) -> UnidadeDeTrabalhoAbstrata:
        if repo_por_dominio:
            self.domain_repo_class = repo_por_dominio.value[0]
            self.view_repo_class = repo_por_dominio.value[1]
            self._nome_dominio_atual = repo_por_dominio.name

        return self

    async def __aenter__(self) -> UnidadeDeTrabalhoAbstrata:
        self.commited = False

        if self.__contexto_ativo is True:
            raise TentandoAbrirUOWContextoJaAberto()

        self.__contexto_ativo = True

        return self

    async def __aexit__(self, *args: dict[str, Any]) -> None:
        self.__contexto_ativo = False

        if not self.commited:
            await self.rollback()

        if hasattr(self, "session"):
            await self.session.close()

    def adicionar_evento_fora_de_agregado(self, evento: "Evento") -> None:  # noqa: F821
        self.eventos_fora_de_agregado.append(evento)

    def collect_new_events(self) -> Generator[Any, None, None]:
        if hasattr(self, "domain_repo") and self.domain_repo:
            for agregado in getattr(self.domain_repo, "seen", set()):
                while getattr(agregado, "eventos", []):
                    yield agregado.eventos.pop(0)

        if hasattr(self, "eventos_fora_de_agregado"):
            while self.eventos_fora_de_agregado:
                yield self.eventos_fora_de_agregado.pop(0)

    async def commit(self) -> None:
        await self.session.commit()
        self.commited = True

    async def rollback(self) -> None:
        if hasattr(self, "session"):
            await self.session.close()

    @property
    def empresa(self) -> UUID:
        if self.usuario and self.usuario.empresa:
            return self.usuario.empresa

        raise ValueError("Id da empresa não foi encontrado")
