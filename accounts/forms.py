from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import authenticate

from . import error_messages
from .countries import COUNTRIES, COUNTRY_CHOICES
from .models import User


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(
            attrs={"placeholder": "Password", "autocomplete": "new-password"}
        ),
    )
    accept_terms = forms.BooleanField(
        error_messages={"required": error_messages.TERMS_REQUIRED},
    )

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "country",
            "phone_country_code", "phone_number", "email",
        ]
        widgets = {
            "first_name": forms.TextInput(
                attrs={"placeholder": "First Name", "autocomplete": "given-name"}
            ),
            "last_name": forms.TextInput(
                attrs={"placeholder": "Last Name", "autocomplete": "family-name"}
            ),
            "phone_country_code": forms.TextInput(
                attrs={"placeholder": "Code", "inputmode": "numeric"}
            ),
            "phone_number": forms.TextInput(
                attrs={"placeholder": "Phone", "inputmode": "numeric", "autocomplete": "tel-national"}
            ),
            "email": forms.EmailInput(
                attrs={"placeholder": "Email", "autocomplete": "email"}
            ),
        }
        error_messages = {
            "email": {"invalid": error_messages.EMAIL_INVALID},
        }

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError(error_messages.EMAIL_TAKEN, code="email_taken")
        return email

    def clean(self):
        cleaned_data = super().clean()
        country = cleaned_data.get("country")
        code = cleaned_data.get("phone_country_code")

        if country and code and code.isdigit():
            expected = COUNTRIES[country]["code"]
            if code != expected:
                self.add_error(
                    "phone_country_code",
                    ValidationError(
                        error_messages.CODE_MISMATCH,
                        code="code_mismatch",
                        params={
                            "country": COUNTRIES[country]["name"],
                            "code": expected,
                        },
                    ),
                )
        return cleaned_data

    # Validate the password after the instance is built, so
    # UserAttributeSimilarityValidator can compare it with the user's details.
    def _post_clean(self):
        super()._post_clean()
        password = self.cleaned_data.get("password")
        if password:
            try:
                validate_password(password, self.instance)
            except ValidationError as error:
                self.add_error("password", error)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.terms_accepted_at = timezone.now()
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["country"].choices = [("", "Country"), *COUNTRY_CHOICES]


class EmailLoginForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        error_messages={"invalid": error_messages.EMAIL_INVALID},
        widget=forms.EmailInput(attrs={"placeholder": "Email", "autocomplete": "email"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password", "autocomplete": "current-password"}),
        strip=False,
        )

    def __init__(self, *args, request=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request
        self.user = None

    def clean_email(self):
        return self.cleaned_data["email"].lower()

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")

        if email and password:
            self.user = authenticate(self.request, email=email, password=password)
            if self.user is None:
                raise ValidationError(error_messages.LOGIN_FAILED, code="invalid_login")
        return cleaned_data

    def get_user(self):
        return self.user