from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode

from ..tokens import account_activation_token


def activate(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        User = get_user_model()
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if not user:
        return HttpResponse('Activation link is invalid!')
    elif user.is_active:
        return HttpResponse('The account is already active. Please login your account.')
    elif not account_activation_token.check_token(user, token):
        return HttpResponse('Activation link is invalid!')

    user.is_active = True
    user.save()
    return HttpResponse('Thank you for your email confirmation. Now you can login your account.')
