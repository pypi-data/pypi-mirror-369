from typing import *
from datetime import datetime
import random
from uuid import UUID
import logging

from django.utils import timezone

from ..conf import settings
from ..models import ConfirmationState
from ..utils import cached_import_string


logger = logging.getLogger(__name__)


def make_confirmation_code() -> str:
    items = ['1', '2', '3', '4', '5', '6', '7', '8', '9'] * 3
    random.shuffle(items)

    return ''.join(items[:6])


def make_confirmation(
    is_confirmed: bool = False,
    meta: Optional[dict] = None,
    now: Optional[datetime] = None,
) -> ConfirmationState:
    code = cached_import_string(settings.CONFIRM_CODE_GENERATOR)()
    now = now if now is not None else timezone.now()

    logger.debug(f'2Factor confirmation code: {code}')

    return ConfirmationState.objects.create(
        code=code, confirmed_at=now if is_confirmed else None, meta=meta or {}
    )


def confirm(id: UUID, code: str) -> Tuple[Optional[ConfirmationState], bool]:
    state: Optional[ConfirmationState] = (
        ConfirmationState.objects
        .with_usage_state()
        .filter(id=id, code=code, is_used=False)
        .first()
    )

    if state is None:
        return None, False

    state.confirm()

    return state, state.is_confirmed


def check(id: UUID) -> Tuple[Optional[ConfirmationState], bool]:
    state = (
        ConfirmationState.objects
        .with_usage_state()
        .filter(id=id, is_used=False)
        .first()
    )

    return state, state.is_confirmed if state is not None else False


def use(state: ConfirmationState) -> bool:
    if not state.is_confirmed:
        return False

    state.use()

    return True
