from django.db import models


__all__ = 'ConfirmationStateQuerySet',


class ConfirmationStateQuerySet(models.QuerySet):
    def with_confirmation_state(self):
        return self.annotate(
            is_confirmed=models.ExpressionWrapper(
                models.Q(confirmed_at__isnull=False),
                output_field=models.BooleanField(),
            ),
        )

    def with_usage_state(self):
        return self.annotate(
            is_used=models.ExpressionWrapper(
                models.Q(used_at__isnull=False),
                output_field=models.BooleanField(),
            ),
        )
