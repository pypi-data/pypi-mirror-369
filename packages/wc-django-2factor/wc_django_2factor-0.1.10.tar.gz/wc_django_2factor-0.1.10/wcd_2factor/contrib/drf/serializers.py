from rest_framework.exceptions import ValidationError
from django.utils.translation import pgettext
from rest_framework.serializers import Serializer, CharField, ChoiceField
from django.utils.functional import SimpleLazyObject

from wcd_2factor.conf import settings
from wcd_2factor.services import confirmer, sender


class RequestConfirmationSerializer(Serializer):
    token = CharField(required=True)
    way = ChoiceField(
        choices=SimpleLazyObject(lambda: settings.get_sender_choices()),
        required=False,
    )

    def commit(self):
        state = confirmer.make_confirmation(meta={
            'token': self.validated_data['token'],
        })

        sender.send(
            self.validated_data.get('way'),
            self.validated_data['token'],
            state,
            context={'request': self.context['request']},
        )

        return state


class ConfirmSerializer(Serializer):
    id = CharField(required=True)
    code = CharField(required=True)

    def validate_id(self, value):
        state, confirmed = confirmer.check(value)

        if state is None:
            raise ValidationError(
                pgettext('wcd_2factor', 'Wrong confirmation id.')
            )

        if confirmed:
            raise ValidationError(
                pgettext('wcd_2factor', 'Confirmation is already confirmed.')
            )

        return state

    def validate(self, data):
        data = super().validate(data)

        if data['id'].code != data['code']:
            raise ValidationError({
                'code': pgettext('wcd_2factor', 'Wrong confirmation code.'),
            })

        return data

    def commit(self):
        state = self.validated_data['id']
        state.confirm()

        return state
