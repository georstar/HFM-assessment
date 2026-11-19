from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django import forms
from django.contrib.auth.password_validation import (
    MinimumLengthValidator,
    get_default_password_validators,
)

from .countries import COUNTRIES
from .validators import NAME_MIN_LENGTH

from . import error_messages
from .forms import EmailLoginForm, SignupForm

# Session entry that carries the new user's first name to the thank-you page.
SIGNUP_NAME_SESSION_KEY = "signup_first_name"

def signup_client_config():
    """Rules and messages for the sign-up page's JavaScript validation.

    Built from the same sources the server uses, so both sides show
    identical messages and the browser never needs its own copy.
    """
    min_length = next(
        validator
        for validator in get_default_password_validators()
        if isinstance(validator, MinimumLengthValidator)
    )
    return {
        "countries": COUNTRIES,
        "nameMinLength": NAME_MIN_LENGTH,
        "passwordMinLength": min_length.min_length,
        "messages": {
            "required": str(forms.Field.default_error_messages["required"]),
            "nameTooShort": str(error_messages.NAME_TOO_SHORT % {"min_length": NAME_MIN_LENGTH}),
            "nameInvalid": str(error_messages.NAME_INVALID_CHARACTERS),
            "emailInvalid": str(error_messages.EMAIL_INVALID),
            "codeNotNumeric": str(error_messages.CODE_NOT_NUMERIC),
            "codeMismatch": str(error_messages.CODE_MISMATCH),
            "phoneInvalid": str(error_messages.PHONE_INVALID),
            "passwordTooShort": str(min_length.get_help_text()),
            "passwordNoUpper": str(error_messages.PASSWORD_NO_UPPER),
            "passwordNoNumber": str(error_messages.PASSWORD_NO_NUMBER),
            "passwordNoSymbol": str(error_messages.PASSWORD_NO_SYMBOL),
            "termsRequired": str(error_messages.TERMS_REQUIRED),
        },
    }


class SignupView(CreateView):
    form_class = SignupForm
    template_name = "accounts/signup.html"
    success_url = reverse_lazy("accounts:signup_done")

    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
        except IntegrityError:
            form.add_error(
                "email",
                ValidationError(error_messages.EMAIL_TAKEN, code="email_taken"),
            )
            return self.form_invalid(form)

        self.request.session[SIGNUP_NAME_SESSION_KEY] = self.object.first_name
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["signup_config"] = signup_client_config()
        return context


class SignupDoneView(TemplateView):
    template_name = "accounts/signup_done.html"

    def get(self, request, *args, **kwargs):
        first_name = request.session.pop(SIGNUP_NAME_SESSION_KEY, None)
        if first_name is None:
            return redirect("accounts:signup")
        context = self.get_context_data(first_name=first_name)
        return self.render_to_response(context)


class EmailLoginView(LoginView):
    form_class = EmailLoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/dashboard.html"
