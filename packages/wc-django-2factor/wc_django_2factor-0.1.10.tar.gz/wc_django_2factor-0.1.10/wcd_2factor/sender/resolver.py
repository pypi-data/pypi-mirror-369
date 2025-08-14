from typing import Type
from .config import SenderConfig
from .backend import SenderBackend
from ..utils import cached_import_string


__all__ = 'resolve_backend_from_config',


def resolve_backend_from_config(name: str, config: SenderConfig, kwargs: dict = {}):
    BackendClass: Type[SenderBackend] = cached_import_string(config['backend'])

    return BackendClass(
        name,
        options=config.get('options'),
        verbose_name=config.get('verbose_name'),
        **kwargs
    )
