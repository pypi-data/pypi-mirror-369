from typing import Callable, NewType

from barramento_de_mensagens.base.barramento import Evento, Comando

ManipuladoresDeEventos = NewType(
    "ManipuladoresDeEventos", dict[type[Evento], list[Callable]]
)
ManipuladoresDeComandos = NewType(
    "ManipuladoresDeComandos", dict[type[Comando], Callable]
)
