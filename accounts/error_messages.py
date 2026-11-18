"""All user-facing validation messages, in one place.

Each is wrapped in gettext_lazy so it can be translated later.
"""
from django.utils.translation import gettext_lazy as _

# --- Names (first name, last name) ---
NAME_TOO_SHORT = _("Must be at least %(min_length)s characters.")
NAME_INVALID_CHARACTERS = _("May contain only letters, spaces, hyphens and apostrophes.")

# --- Password ---
PASSWORD_NO_UPPER = _("Must contain at least one uppercase letter (A-Z).")
PASSWORD_NO_NUMBER = _("Must contain at least one number (0-9).")
PASSWORD_NO_SYMBOL = _("Must contain at least one symbol, e.g. ! @ # $ %.")

# --- PHONE ---
CODE_NOT_NUMERIC = _("Country code must contain digits only, e.g. 357.")
PHONE_INVALID = _("Phone number must be 6 to 15 digits, with no spaces or symbols.")

# --- Email ---
EMAIL_INVALID = _("Enter a valid email address, e.g. name@example.com.")
EMAIL_TAKEN = _("An account with this email address already exists.")

# --- Country / code consistency ---
CODE_MISMATCH = _("The country code for %(country)s is %(code)s.")

# --- Terms ---
TERMS_REQUIRED = _("You must accept the Privacy Policy and Terms and Conditions to register.")

# --- Login ---
LOGIN_FAILED = _("Incorrect email or password.")