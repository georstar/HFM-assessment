from django.test import TestCase
from django.core.exceptions import NON_FIELD_ERRORS

from accounts.forms import EmailLoginForm, SignupForm
from accounts.models import User


def valid_data(**overrides):
    data = {
        "first_name": "John",
        "last_name": "Smith",
        "country": "CY",
        "phone_country_code": "357",
        "phone_number": "99123456",
        "email": "john@example.com",
        "password": "Secret12!",
        "accept_terms": "on",
    }
    data.update(overrides)
    return data


class SignupFormTests(TestCase):
    def test_valid_data_is_accepted(self):
        form = SignupForm(data=valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_save_hashes_password_and_records_terms(self):
        form = SignupForm(data=valid_data())
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()

        self.assertNotEqual(user.password, "Secret12!")
        self.assertTrue(user.check_password("Secret12!"))
        self.assertIsNotNone(user.terms_accepted_at)

    def test_rejects_short_first_name(self):
        form = SignupForm(data=valid_data(first_name="Joe"))
        self.assertTrue(form.has_error("first_name", code="name_too_short"))

    def test_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user(
            email="john@example.com",
            password="Secret12!",
            first_name="John",
            last_name="Smith",
        )
        form = SignupForm(data=valid_data(email="JOHN@example.com"))
        self.assertTrue(form.has_error("email", code="email_taken"))

    def test_rejects_unticked_terms(self):
        data = valid_data()
        del data["accept_terms"]
        form = SignupForm(data=data)
        self.assertTrue(form.has_error("accept_terms", code="required"))

    def test_lowercases_email(self):
        form = SignupForm(data=valid_data(email="John@Example.COM"))
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.email, "john@example.com")

    def test_rejects_invalid_last_name(self):
        form = SignupForm(data=valid_data(last_name="Sm1th"))
        self.assertTrue(form.has_error("last_name", code="name_invalid_characters"))

    def test_rejects_invalid_email(self):
        form = SignupForm(data=valid_data(email="john@"))
        self.assertTrue(form.has_error("email", code="invalid"))

    def test_rejects_non_numeric_country_code(self):
        form = SignupForm(data=valid_data(phone_country_code="35a"))
        self.assertTrue(form.has_error("phone_country_code", code="code_not_numeric"))

    def test_rejects_code_not_matching_country(self):
        form = SignupForm(data=valid_data(country="GR"))
        self.assertTrue(form.has_error("phone_country_code", code="code_mismatch"))

    def test_rejects_invalid_phone_number(self):
        form = SignupForm(data=valid_data(phone_number="12ab"))
        self.assertTrue(form.has_error("phone_number", code="phone_invalid"))

    def test_rejects_weak_password(self):
        form = SignupForm(data=valid_data(password="secret12!"))
        self.assertTrue(form.has_error("password", code="password_no_upper"))


class EmailLoginFormTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            email="john@example.com",
            password="Secret12!",
            first_name="John",
            last_name="Smith",
        )

    def test_valid_credentials_log_in(self):
        form = EmailLoginForm(data={"email": "john@example.com", "password": "Secret12!"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.get_user(), self.user)

    def test_email_is_case_insensitive(self):
        form = EmailLoginForm(data={"email": "JOHN@Example.com", "password": "Secret12!"})
        self.assertTrue(form.is_valid(), form.errors)

    def test_rejects_invalid_email_format(self):
        form = EmailLoginForm(data={"email": "john@", "password": "Secret12!"})
        self.assertTrue(form.has_error("email", code="invalid"))

    def test_rejects_missing_password(self):
        form = EmailLoginForm(data={"email": "john@example.com"})
        self.assertTrue(form.has_error("password", code="required"))

    def test_rejects_wrong_password(self):
        form = EmailLoginForm(data={"email": "john@example.com", "password": "Wrong12!"})
        self.assertTrue(form.has_error(NON_FIELD_ERRORS, code="invalid_login"))

    def test_rejects_inactive_user(self):
        self.user.is_active = False
        self.user.save()
        form = EmailLoginForm(data={"email": "john@example.com", "password": "Secret12!"})
        self.assertTrue(form.has_error(NON_FIELD_ERRORS, code="invalid_login"))

    def test_unknown_email_gives_same_error_as_wrong_password(self):
        wrong_password = EmailLoginForm(
            data={"email": "john@example.com", "password": "Wrong12!"}
        )
        unknown_email = EmailLoginForm(
            data={"email": "nobody@example.com", "password": "Wrong12!"}
        )
        self.assertFalse(wrong_password.is_valid())
        self.assertFalse(unknown_email.is_valid())
        self.assertEqual(wrong_password.non_field_errors(), unknown_email.non_field_errors())