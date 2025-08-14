from typing import Callable

from sqlalchemy.orm import DeclarativeBase

from barramento_de_mensagens.base.barramento import BarramentoDeMensagens
from barramento_de_mensagens.base.bootstrap import bootstrap_abstrato
from barramento_de_mensagens.base.entidades import UsuarioBase
from barramento_de_mensagens.base.unidade_de_trabalho import UnidadeDeTrabalhoAbstrata
from barramento_de_mensagens.manipuladores import (
    ManipuladoresDeEventos,
    ManipuladoresDeComandos,
)
from barramento_de_mensagens.unidade_de_trabalho import UnidadeDeTrabalhoBase


def bootstrap_base(
    session_factory: Callable | None = None,
    engine_factory: Callable | None = None,
    base: type[DeclarativeBase] | None = None,
    uow: UnidadeDeTrabalhoAbstrata | None = None,
    usuario: UsuarioBase | None = None,
    schema: str | None = None,
    event_handlers: ManipuladoresDeEventos | None = None,
    command_handlers: ManipuladoresDeComandos | None = None,
    subir_erros_de_eventos: bool = False,
    permitir_execucoes_assincronas: bool = True,
    somente_leitura: bool = False,
    criar_schema: bool = False,
) -> BarramentoDeMensagens:
    if uow is None:
        uow = UnidadeDeTrabalhoBase(
            session_factory=session_factory,
            engine_factory=engine_factory,
            base=base,
            usuario=usuario,
            schema=schema,
            somente_leitura=somente_leitura,
            criar_schema=criar_schema,
        )

    return bootstrap_abstrato(
        uow=uow,
        command_handlers=command_handlers,
        event_handlers=event_handlers,
        subir_erros_de_eventos=subir_erros_de_eventos,
        permitir_execucoes_assincronas=permitir_execucoes_assincronas,
    )
