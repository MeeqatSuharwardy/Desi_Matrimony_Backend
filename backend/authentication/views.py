from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenViewBase

from backend.authentication.exceptions import OTPEmailFailed
from backend.authentication.models import OTP
from backend.authentication.serializers import AuthenticationSerializer, CustomTokenObtainPairSerializer


class OTPEmailAPIView(GenericAPIView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = AuthenticationSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data['token']
        user = serializer.validated_data['user']

        self.email_otp(user, otp)
        OTP.objects.create(user=user, token=otp)

        response = {
            'message': 'OTP sent to the registered email account'
        }
        return Response(response, status=status.HTTP_200_OK)

    def email_otp(self, user, otp):
        mail_subject = 'Matrimony App OTP'
        message = render_to_string('otp_email.html', {
            'user': user,
            'token': otp
        })
        to_email = user.email
        email = EmailMessage(
            mail_subject, message, to=[to_email]
        )
        try:
            email.send()
        except:
            raise OTPEmailFailed()


class CustomTokenObtainPairView(TokenViewBase):
    """
    Takes a set of user credentials and returns an access and refresh JSON web
    token pair to prove the authentication of those credentials.
    """
    serializer_class = CustomTokenObtainPairSerializer
