from typing import *
import warnings
from datetime import datetime
from uuid import uuid4
from django.db import models
from django.utils.translation import pgettext_lazy, pgettext
from django.utils import timezone

try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField

from .query import ConfirmationStateQuerySet


__all__ = 'ConfirmationState',


class ConfirmationState(models.Model):
    objects: models.Manager = (
        ConfirmationStateQuerySet.as_manager()
    )

    class Meta:
        verbose_name = pgettext_lazy('wcd_2factor', 'Confirmation state')
        verbose_name_plural = pgettext_lazy(
            'wcd_2factor', 'Confirmation states'
        )
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['-confirmed_at']),
            models.Index(fields=['-used_at']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['-updated_at']),
        ]

    id = models.UUIDField(
        primary_key=True, verbose_name=pgettext_lazy('wcd_2factor', 'ID'),
        default=uuid4
    )
    code = models.TextField(
        verbose_name=pgettext_lazy('wcd_2factor', 'Confirmation code'),
        blank=False, null=False,
    )

    meta = JSONField(
        verbose_name=pgettext_lazy('wcd_2factor', 'Metadata'),
        null=False, blank=True, default=dict,
    )

    confirmed_at = models.DateTimeField(
        verbose_name=pgettext_lazy('wcd_2factor', 'Confirmed at'),
        default=None, null=True, blank=True,
    )
    used_at = models.DateTimeField(
        verbose_name=pgettext_lazy('wcd_2factor', 'Used at'),
        default=None, null=True, blank=True,
    )

    created_at = models.DateTimeField(
        verbose_name=pgettext_lazy('wcd_2factor', 'Created at'),
        default=timezone.now, null=False, blank=False,
    )
    updated_at = models.DateTimeField(
        verbose_name=pgettext_lazy('wcd_2factor', 'Updated at'), auto_now=True,
    )

    def __str__(self):
        return (
            pgettext(
                'wcd_2factor',
                '#{code} confirmation: {confirmed}.',
            )
            .format(
                code=self.code,
                confirmed='+' if self.is_confirmed else '-',
            )
        )

    @property
    def is_confirmed(self):
        return self.confirmed_at is not None

    @is_confirmed.setter
    def is_confirmed(self, value: bool):
        if value and self.confirmed_at is None:
            self.confirmed_at = timezone.now()
        elif not value:
            self.confirmed_at = None

    @property
    def is_used(self):
        return self.used_at is not None

    @is_used.setter
    def is_used(self, value: bool):
        pass

    def confirm(self, now: Optional[datetime] = None):
        self.confirmed_at = now if now is not None else timezone.now()
        self.save(update_fields=('confirmed_at',))

    def use(self, now: Optional[datetime] = None):
        self.used_at = now if now is not None else timezone.now()
        self.save(update_fields=('used_at',))
