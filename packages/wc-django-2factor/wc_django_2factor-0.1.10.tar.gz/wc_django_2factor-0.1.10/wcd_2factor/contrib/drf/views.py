from django.urls import path
from rest_framework.generics import GenericAPIView
from rest_framework import status
from rest_framework.response import Response
from django.db import transaction

from wcd_2factor.conf import settings
from .serializers import RequestConfirmationSerializer, ConfirmSerializer


__all__ = (
    'RequestConfirmationView', 'ConfirmView',
    'request_confirmation_view', 'confirm_view', 'make_urlpatterns',
)


class SerializerCommitterMixin:
    def collect_response(self, request, state, **kwargs):
        response = {'id': state.id}

        if settings.DEBUG_CODE_RESPONSE:
            response['code'] = state.code

        return response

    @transaction.atomic()
    def post(self, request, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        state = serializer.commit()

        return Response(
            self.collect_response(request, serializer=serializer, state=state),
            status=status.HTTP_200_OK,
        )


class RequestConfirmationView(SerializerCommitterMixin, GenericAPIView):
    serializer_class = RequestConfirmationSerializer


class ConfirmView(SerializerCommitterMixin, GenericAPIView):
    serializer_class = ConfirmSerializer


request_confirmation_view = RequestConfirmationView.as_view()
confirm_view = ConfirmView.as_view()


def make_urlpatterns(
    request_confirmation_view=request_confirmation_view,
    confirm_view=confirm_view,
):
    return [
        path('request-confirmation/', request_confirmation_view, name='request-confirmation'),
        path('confirm/', confirm_view, name='confirm'),
    ]
