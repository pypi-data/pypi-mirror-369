from typing import Any, Dict, Optional, TypedDict

from .backend import SenderOptions


__all__ = 'SenderConfig',


class SenderConfig(TypedDict):
    backend: str
    options: Optional[SenderOptions]
    verbose_name: Optional[str]
