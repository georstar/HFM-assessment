from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.core.validators import RegexValidator
from .countries import COUNTRY_CHOICES
from .managers import UserManager
from .validators import validate_name
from . import error_messages


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, validators=[validate_name])
    last_name = models.CharField(max_length=50, validators=[validate_name])
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    phone_country_code = models.CharField(
        max_length=4,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{1,4}$",
                message=error_messages.CODE_NOT_NUMERIC,
                code="code_not_numeric",
            )
        ],
    )
    phone_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r"^[0-9]{6,15}$",
                message=error_messages.PHONE_INVALID,
                code="phone_invalid",
            )
        ],
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    terms_accepted_at = models.DateTimeField(null=True, blank=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    def __str__(self):
        return self.email
