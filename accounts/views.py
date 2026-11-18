from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from . import error_messages
from .forms import EmailLoginForm, SignupForm

# Session entry that carries the new user's first name to the thank-you page.
SIGNUP_NAME_SESSION_KEY = "signup_first_name"


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
