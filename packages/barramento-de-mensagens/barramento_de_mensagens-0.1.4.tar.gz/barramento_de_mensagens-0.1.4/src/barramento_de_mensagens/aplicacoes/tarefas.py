from barramento_de_mensagens.base.barramento import Evento, BarramentoDeMensagens
from barramento_de_mensagens.base.entidades import UsuarioBase
from barramento_de_mensagens.aplicacoes.celery import tarefa_celery


def tratar_evento_asyncrono(  # type: ignore[no-untyped-def]
    self,
    evento: Evento,
    usuario: UsuarioBase | None = None,
) -> None:
    from barramento_de_mensagens.bootstrap import bootstrap_base
    import sentry_sdk
    import asyncio

    async def executar(barramento: BarramentoDeMensagens, evento: Evento) -> None:
        await barramento.handle(evento)

    nome = f"Tratando evento asyncrono [{evento.__class__.__name__}]"

    contexto = sentry_sdk.start_transaction(
        name="Tratando evento asyncrono",
        op="task",
        description=nome,
        sampled=True,
    )
    with contexto as span:
        span.set_tag("name", nome)
        try:
            # A execução assíncrona começou, super importante alterar a flag do evento
            # para não ser executado de forma assíncrona novamente,
            # caso contrário o celery entrará num loop infinito de tasks
            evento.executar_de_forma_assincrona = False

            bus = bootstrap_base(usuario=usuario, subir_erros_de_eventos=True)

            # isso deve rodar dentro do asyncio.run devido a estrutura de funcoes async
            asyncio.run(executar(bus, evento))

        except Exception as erro:
            span.set_tag("houve_erro", True)
            span.set_tag("error", str(erro))
            raise erro


task_tratar_evento_asyncrono = tarefa_celery()(tratar_evento_asyncrono)
