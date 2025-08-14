# Barramento de mensagens

Desenvolvimento de um sistema de barramento de mesagens para ser utilizado em varios projetos.

## Arquitetura do sistema
- UnidadeDeTrabalho para gerenciamento de transações.
- Barramento de mensagens para comunicação entre comandos, eventos e executores.
- Bootstrap para inicialização do sistema do barramento.

## como manusear o projeto
- Manutenções:
    - Altere a tag no `pyproject.toml` para a versão que deseja publicar.
    - Buildar o pacote `make build`
    - Add e commite suas alteracoes
    - crie uma tag git: `git tag v0.1.0`  # <== sua tag, altere conforme o versionamento
    - publique a tag: `git push origin master --tags`
- Instalação:
    - Instalar a biblioteca `make instalar-barramento`
    - Atualizar a biblioteca `make atualizar-barramento`

## Como utilizar
- configuração do celery:
    - Necessário para executar tarefas assíncronas.
    - É necessário configurar no inicializador do celery e na api.
``` python
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, Any]:
    from barramento_de_mensagens.aplicacoes.celery import configurar_celery_app
    from infra.aplicacoes.celery import celery_app  # <= seu app celery
    
    configurar_celery_app(celery_app)
    yield
```

- inicialização do barramento:
    - Recomendação: Criar uma classe `UnidadeDeTrabalho` e herdar de `UnidadeDeTrabalhoBase`
``` python
from unidade_de_trabalho import UnidadeDeTrabalhoBase

class UnidadeDeTrabalho(UnidadeDeTrabalhoBase, Generic[REPO_ESCRITA, REPO_LEITURA]):
    domain_repo: RepositorioDominioBase
    view_repo: RepositorioConsultaBase
    
    def __init__(
       self,
       session_factory: Callable,  # <== defina um session factory padrão
       engine_factory: Callable,  # <== defina um engine factory padrão
       base: type[DeclarativeBase],  # <== defina um base padrão
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
         engine_factory=engine_factory,
         base=base,
         usuario=usuario,
         schema=schema,
         criar_schema=criar_schema,
       )
```

- Inicialização dos manipuladores:
    - Crie duas estruturas de dicionario para guardar manipuladores de eventos e de comandos.
```` python
EVENT_HANDLERS: ManipuladoresDeEventos = ManipuladoresDeEventos({
   # EventoTeste: [evento_teste],
   ...
})

COMMAND_HANDLERS: ManipuladoresDeComandos = ManipuladoresDeComandos({
   # ComandoTeste: comando_teste,
   ...
})
````

- Inicialização do bootstrap:
    - Recomendação: Criar uma funcao `bootstrap` que retorne a `bootstrap_base`
```` python
from bootstrap import bootstrap_base

def bootstrap(
   session_factory: Callable | None = None,  # <== defina um session factory padrão
   engine_factory: Callable | None = None,  # <== defina um engine factory padrão
   base: type[DeclarativeBase] | None = None,  # <== defina um base padrão
   event_handlers: ManipuladoresDeEventos | None = None,
   command_handlers: ManipuladoresDeComandos | None = None,
   uow: UnidadeDeTrabalhoBase | None = None,
   usuario: UsuarioBase | None = None,
   schema: str | None = None,
   subir_erros_de_eventos: bool = False,
   permitir_execucoes_assincronas: bool = True,
   somente_leitura: bool = False,
   criar_schema: bool = False,
) -> BarramentoDeMensagens:
   # importe seus manipuladores
   from origem.dos.maipuladores import EVENT_HANDLERS, COMMAND_HANDLERS
   
   # defina seus manipuladores         
   command_handlers = command_handlers or COMMAND_HANDLERS
   event_handlers = event_handlers or EVENT_HANDLERS
   
   return bootstrap_base(
      uow=uow,
      session_factory=session_factory,
      engine_factory=engine_factory,
      base=base,
      event_handlers=event_handlers,
      command_handlers=command_handlers,
      usuario=usuario,
      schema=schema,
      subir_erros_de_eventos=subir_erros_de_eventos,
      permitir_execucoes_assincronas=permitir_execucoes_assincronas,
      somente_leitura=somente_leitura,
      criar_schema=criar_schema,
   )
````

- Definicao dos Dominios
    - Crie uma classe `Dominio` que herde de `DominioBase`. Ela sera usada para definir os repositorios de dominio e de consulta.
```` python
from dominio import DominioBase

class Dominio(DominioBase):
   # usuario = (UsuarioRepoDominio, UsuarioRepoConsulta)
   ...
````

- IMPORTANTE!
- O projeto depende de duas variaveis de ambiente:
    - `TEST_ENV`: deve ser setada com `true` ao rodar testes. Isso faz eventos darem raise ao quebrar.
    - `ENV_CONFIG`: caso seja um abiente de `alpha` ou `production`, vai enviar o erro para o sentry.