from typing import Any
from celery import Celery
from celery.local import PromiseProxy


_celery_app: Celery | None = None


def configurar_celery_app(celery_app: Celery) -> None:
    global _celery_app
    _celery_app = celery_app


def obter_celery_app() -> Celery:
    if _celery_app is None:
        raise RuntimeError(
            "O celery_app ainda não foi configurado. Chame 'configurar_celery_app(celery_app)' antes de usar as tasks."
        )
    return _celery_app


def tarefa_celery(*args: dict[str, Any], **kwargs: dict[str, Any]) -> PromiseProxy:
    celery_app = obter_celery_app()

    max_retries = kwargs.pop("max_retries", 1)
    kwargs["bind"] = True
    kwargs["trail"] = True
    retry_backoff = kwargs.pop("retry_backoff", 5)
    retry_backoff_max = kwargs.pop("retry_backoff_max", 700)
    retry_jitter = kwargs.pop("retry_jitter", False)
    return celery_app.task(
        *args,
        autoretry_for=(Exception,),
        retry_kwargs={"max_retries": max_retries},
        max_retries=max_retries,
        retry_backoff=retry_backoff,
        retry_backoff_max=retry_backoff_max,
        retry_jitter=retry_jitter,
        **kwargs,
    )
