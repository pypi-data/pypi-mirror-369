from typing import Any, Callable, Dict, Optional
from django.utils.text import camel_case_to_spaces

from ..models import ConfirmationState


__all__ = 'SenderBackend', 'FunctionalSenderBackend',


SenderOptions = Dict[str, Any]


class SenderBackend:
    name: str
    options: SenderOptions
    verbose_name: str

    def __init__(
        self,
        name: str,
        options: Optional[SenderOptions] = None,
        verbose_name: Optional[str] = None,
        **kwargs
    ) -> None:
        self.name = name
        self.options = options or {}
        self.verbose_name = (
            verbose_name or camel_case_to_spaces(self.__class__.__name__)
        )
        self.kwargs = kwargs

    def send(
        self,
        token: str,
        state: ConfirmationState,
        context: dict = {}
    ): # pragma: no cover
        raise NotImplementedError(
            'You should implement `send` method in your sender backend'
        )

    def __call__(self, *args, **kwargs):
        return self.send(*args, **kwargs)


class FunctionalSenderBackend(SenderBackend):
    def __init__(self, func: Callable, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.functional_send = func

    def send(
        self,
        token: str,
        state: ConfirmationState,
        context: dict = {}
    ):
        return self.functional_send(
            token=token, state=state, context=context, name=self.name,
            options=self.options, **self.kwargs
        )

    @classmethod
    def from_callable(cls, func):
        def wrapper(*args, **kwargs):
            return cls(func, *args, **kwargs)

        return wrapper
