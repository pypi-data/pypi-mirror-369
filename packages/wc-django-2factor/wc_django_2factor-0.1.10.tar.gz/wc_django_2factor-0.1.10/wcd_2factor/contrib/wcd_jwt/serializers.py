from django.utils.translation import pgettext
from rest_framework.serializers import CharField
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from wcd_2factor.services import confirmer


class TwoFactorTokenObtainPairSerializer(TokenObtainPairSerializer):
    two_factor_id = CharField(required=True)

    def validate(self, attrs):
        data = super().validate(attrs)
        two_factor_id = attrs['two_factor_id']
        state, confirmed = confirmer.check(two_factor_id)

        if not confirmed:
            raise ValidationError({
                'two_factor_id': pgettext('wcd_2factor', 'Wrong confirmation.'),
            })

        confirmer.use(state)
        self.state = state

        return data
