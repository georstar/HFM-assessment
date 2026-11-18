import re
from django.core.exceptions import ValidationError
from . import error_messages


NAME_MIN_LENGTH = 4

# One run of letters (any alphabet), then optional groups of
# a single separator (space, apostrophe, hyphen) followed by more letters.
NAME_PATTERN = re.compile(r"[^\W\d_]+(?:[ '\-][^\W\d_]+)*")

UPPERCASE_PATTERN = re.compile(r"[A-Z]")
NUMBER_PATTERN = re.compile(r"[0-9]")
SYMBOL_PATTERN = re.compile(r"[^A-Za-z0-9\s]")

def validate_name(value):
    val = value.strip()
    if len(val) < NAME_MIN_LENGTH:
        raise ValidationError(
            message=error_messages.NAME_TOO_SHORT,
            code="name_too_short",
            params={"min_length": NAME_MIN_LENGTH},
        )
    if not NAME_PATTERN.fullmatch(val):
        raise ValidationError(
            message=error_messages.NAME_INVALID_CHARACTERS,
            code="name_invalid_characters",
        )


class UppercaseValidator:
    def validate(self, password, user=None):
        if not UPPERCASE_PATTERN.search(password):
            raise ValidationError(
                message=error_messages.PASSWORD_NO_UPPER,
                code="password_no_upper",
            )

    def get_help_text(self):
        return error_messages.PASSWORD_NO_UPPER


class NumberValidator:
    def validate(self, password, user=None):
        if not NUMBER_PATTERN.search(password):
            raise ValidationError(
                message=error_messages.PASSWORD_NO_NUMBER,
                code="password_no_number",
            )

    def get_help_text(self):
        return error_messages.PASSWORD_NO_NUMBER


class SymbolValidator:
    def validate(self, password, user=None):
        if not SYMBOL_PATTERN.search(password):
            raise ValidationError(
                message=error_messages.PASSWORD_NO_SYMBOL,
                code="password_no_symbol",
            )

    def get_help_text(self):
        return error_messages.PASSWORD_NO_SYMBOL