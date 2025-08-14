from __future__ import annotations

from typing import Generic, TypeVar, Callable

from sqlalchemy.orm import DeclarativeBase

from barramento_de_mensagens.aplicacoes.banco_de_dados import (
    criar_schema_completo_dentro_de_uma_transacao,
)
from barramento_de_mensagens.base.entidades import (
    RepositorioDominioBase,
    RepositorioConsultaBase,
    UsuarioBase,
)
from barramento_de_mensagens.base.unidade_de_trabalho import UnidadeDeTrabalhoAbstrata

REPO_LEITURA = TypeVar("REPO_LEITURA")
REPO_ESCRITA = TypeVar("REPO_ESCRITA")


class UnidadeDeTrabalhoBase(
    UnidadeDeTrabalhoAbstrata, Generic[REPO_ESCRITA, REPO_LEITURA]
):
    domain_repo: RepositorioDominioBase
    view_repo: RepositorioConsultaBase

    def __init__(
        self,
        session_factory: Callable,
        engine_factory: Callable,
        base: type[DeclarativeBase],
        usuario: UsuarioBase | None = None,
        schema: str | None = None,
        somente_leitura: bool = False,
        criar_schema: bool = False,
    ):
        self.somente_leitura = somente_leitura
        self.engine_factory = engine_factory
        self.base = base

        super().__init__(
            session_factory=session_factory,
            usuario=usuario,
            schema=schema,
            criar_schema=criar_schema,
        )

    async def __aenter__(self) -> UnidadeDeTrabalhoBase:
        self.commited = False

        if self.criar_schema:  # type: ignore[has-type]
            self.session = await criar_schema_completo_dentro_de_uma_transacao(
                engine_factory=self.engine_factory,
                base=self.base,
                schema_id=self.schema,
                session_factory=self.sql_session_factory,
            )
            self.criar_schema = False
        else:
            self.session = await self.sql_session_factory(
                somente_leitura=False,
                schema=self.schema,
            )
        self.session_leitura = await self.sql_session_factory(
            somente_leitura=True, schema=self.schema
        )

        if not self.somente_leitura and self.domain_repo_class:
            self.domain_repo = self.domain_repo_class(self.session)

        if self.view_repo_class:
            self.view_repo = self.view_repo_class(self.session_leitura)

        return await super().__aenter__()  # type: ignore[return-value]

    async def __aexit__(  # type: ignore[override]
        self, *args: tuple[type[Exception], Exception, Exception]
    ) -> None:
        await super().__aexit__(*args)
