import functools
import inspect
from typing import Any, Callable

from barramento_de_mensagens.base.barramento import (
    Comando,
    Evento,
    BarramentoDeMensagens,
    logger,
)
from barramento_de_mensagens.base.unidade_de_trabalho import UnidadeDeTrabalhoAbstrata
from barramento_de_mensagens.manipuladores import (
    ManipuladoresDeEventos,
    ManipuladoresDeComandos,
)


def bootstrap_abstrato(
    uow: UnidadeDeTrabalhoAbstrata,
    command_handlers: ManipuladoresDeComandos,
    event_handlers: ManipuladoresDeEventos,
    subir_erros_de_eventos: bool = False,
    permitir_execucoes_assincronas: bool = True,
) -> BarramentoDeMensagens:
    dependencies = {"uow": uow, "unidade_de_trabalho": uow}

    injected_event_handlers = {
        event_type: [
            inject_dependencies(handler, dependencies) for handler in event_handlers
        ]
        for event_type, event_handlers in event_handlers.items()
    }
    injected_command_handlers = {
        command_type: inject_dependencies(handler, dependencies)
        for command_type, handler in command_handlers.items()
    }

    return BarramentoDeMensagens(
        uow=uow,
        event_handlers=injected_event_handlers,
        command_handlers=injected_command_handlers,
        subir_erros_de_eventos=subir_erros_de_eventos,
        permitir_execucoes_assincronas=permitir_execucoes_assincronas,
    )


def inject_dependencies(handler: Callable, dependencies: dict) -> Callable:
    params = inspect.signature(handler).parameters
    deps = {
        name: dependency for name, dependency in dependencies.items() if name in params
    }

    @functools.wraps(handler)
    async def async_wrapper(message: Comando | Evento) -> Any:
        try:
            return await handler(message, **deps)
        finally:
            logger.info(f"Handling async message {message} finished")

    return async_wrapper
