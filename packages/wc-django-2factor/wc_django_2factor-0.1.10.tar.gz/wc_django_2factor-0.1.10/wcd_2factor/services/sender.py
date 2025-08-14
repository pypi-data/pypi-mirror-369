from typing import Optional
from ..conf import settings
from ..sender import resolve_backend_from_config, SenderBackend
from ..models import ConfirmationState


def get_sender_backend(
    sender_name: Optional[str] = None, **kwargs
) -> SenderBackend:
    name: str = sender_name or settings.DEFAULT_SENDER
    config = settings.SENDERS[name]

    return resolve_backend_from_config(name, config, kwargs)


def send(way: Optional[str], token: str, state: ConfirmationState, context: dict = {}):
    sender = get_sender_backend(way)

    return sender(token=token, state=state, context=context)
