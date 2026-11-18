from django.contrib.auth import SESSION_KEY
from django.test import Client, TestCase
from django.urls import reverse

from accounts import error_messages
from accounts.models import User
from accounts.tests.test_forms import valid_data
from accounts.forms import SignupForm
from unittest import mock


def create_john():
    return User.objects.create_user(
        email="john@example.com",
        password="Secret12!",
        first_name="John",
        last_name="Smith",
    )


class SignupViewTests(TestCase):
    def setUp(self):
        self.url = reverse("accounts:signup")

    def test_get_shows_signup_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/signup.html")

    def test_valid_post_creates_user_and_redirects(self):
        response = self.client.post(self.url, valid_data())
        self.assertRedirects(response, reverse("accounts:signup_done"))
        self.assertTrue(User.objects.filter(email="john@example.com").exists())

    def test_thank_you_page_names_the_user(self):
        response = self.client.post(self.url, valid_data(), follow=True)
        self.assertContains(response, "Thank you for signing up, John!")

    def test_invalid_post_shows_specific_errors_and_creates_nothing(self):
        response = self.client.post(self.url, valid_data(first_name="Joe", email="john@"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, error_messages.NAME_TOO_SHORT % {"min_length": 4})
        self.assertContains(response, error_messages.EMAIL_INVALID)
        self.assertEqual(User.objects.count(), 0)

    def test_entered_values_are_kept_after_error(self):
        response = self.client.post(self.url, valid_data(first_name="Joe"))
        self.assertContains(response, 'value="Smith"')

    def test_password_is_not_sent_back_after_error(self):
        response = self.client.post(self.url, valid_data(first_name="Joe"))
        self.assertNotContains(response, "Secret12!")

    def test_thank_you_page_without_signup_redirects_to_form(self):
        response = self.client.get(reverse("accounts:signup_done"))
        self.assertRedirects(response, self.url)

    def test_post_without_csrf_token_is_rejected(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(self.url, valid_data())
        self.assertEqual(response.status_code, 403)
        self.assertEqual(User.objects.count(), 0)

    def test_duplicate_email_race_shows_error_instead_of_crashing(self):
        create_john()
        # Simulate the race: both of the form’s duplicate checks see no existing user,
        # so only the database's unique constraint can stop the second insert.
        with (
            mock.patch.object(
                SignupForm, "clean_email", lambda form: form.cleaned_data["email"].lower()
            ),
            mock.patch.object(SignupForm, "validate_unique", lambda form: None),
        ):
            response = self.client.post(self.url, valid_data())

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, error_messages.EMAIL_TAKEN)
        self.assertEqual(User.objects.count(), 1)


class LoginViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_john()

    def setUp(self):
        self.url = reverse("accounts:login")

    def test_get_shows_login_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "accounts/login.html")

    def test_valid_login_redirects_to_dashboard(self):
        response = self.client.post(self.url, {"email": "john@example.com", "password": "Secret12!"})
        self.assertRedirects(response, reverse("accounts:dashboard"))
        self.assertEqual(self.client.session[SESSION_KEY], str(self.user.pk))

    def test_invalid_email_format_shows_message(self):
        response = self.client.post(self.url, {"email": "john@", "password": "Secret12!"})
        self.assertContains(response, error_messages.EMAIL_INVALID)
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_wrong_password_shows_message(self):
        response = self.client.post(self.url, {"email": "john@example.com", "password": "Wrong12!"})
        self.assertContains(response, error_messages.LOGIN_FAILED)
        self.assertNotIn(SESSION_KEY, self.client.session)


class DashboardViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_john()

    def test_requires_login(self):
        url = reverse("accounts:dashboard")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_shows_user_first_name(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:dashboard"))
        self.assertContains(response, "John")


class LogoutViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = create_john()

    def test_post_logs_out_and_redirects_to_login(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("accounts:login"))
        self.assertNotIn(SESSION_KEY, self.client.session)

    def test_get_is_not_allowed(self):
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 405)