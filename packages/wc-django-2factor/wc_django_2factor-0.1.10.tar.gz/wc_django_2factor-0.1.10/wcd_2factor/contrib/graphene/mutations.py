import graphene
from django.utils.translation import get_language
from django.utils.translation import pgettext_lazy
from wcd_graphene.exceptions import StatefulError
from postie.shortcuts import send_mail

from wcd_2factor.cases import confirmer


__all__ = 'RequestConfirmation', 'Confirm',

# TODO: Everything wrong here. Rewrite and do not document for now.
class RequestConfirmation(graphene.Mutation):
    id = graphene.String()
    # FIXME: Remove code from here in future, after test perhaps.
    code = graphene.String()

    class Arguments:
        token = graphene.String(required=True)
        way = graphene.String(required=True)

    def mutate(root, info, token: str, way: str):
        state = confirmer.make_confirmation()

        if way == 'email':
            send_mail(
                event='confirm_email',
                recipients=[token],
                context={'code': state.code},
                language=get_language()
            )
        if way == 'phone':
            # FIXME: Blocked for a while
            # from apps.staff.tasks import send_phone_confirmation
            # send_phone_confirmation.delay(phone=token, code=state.code)
            pass

        return RequestConfirmation(id=str(state.id), code=state.code)


class Confirm(graphene.Mutation):
    id = graphene.String()

    class Arguments:
        id = graphene.String(required=True)
        code = graphene.String(required=True)

    def mutate(root, info, id: str, code: str):
        confirmed, state = confirmer.confirm(id, code)

        if not confirmed:
            raise StatefulError(
                message=pgettext_lazy('staff', 'Wrong code'),
                extend_path=['code']
            )

        return Confirm(id=id)
