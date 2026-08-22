from django.contrib.auth.backends import ModelBackend


class AllowInactiveModelBackend(ModelBackend):
    """
    Lets authenticate() succeed for unverified (is_active=False) users so
    AuthenticationForm.confirm_login_allowed() can reject them with our
    "verify your email" message instead of Django's generic invalid-login
    error, which is what happens when authenticate() itself filters them out.
    """

    def user_can_authenticate(self, user):
        return True
