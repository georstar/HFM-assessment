from django.test import SimpleTestCase
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from accounts.validators import (
    NumberValidator,
    SymbolValidator,
    UppercaseValidator,
    validate_name,
)


class ValidateNameTests(SimpleTestCase):
    def test_accepts_name_with_four_characters(self):
        validate_name("John")

    def test_rejects_name_with_three_characters(self):
        with self.assertRaises(ValidationError) as cm:
            validate_name("Joe")
        self.assertEqual(cm.exception.code, "name_too_short")

    def test_rejects_short_name_padded_with_spaces(self):
        with self.assertRaises(ValidationError) as cm:
            validate_name("  Ali  ")
        self.assertEqual(cm.exception.code, "name_too_short")

    def test_accepts_name_with_apostrophe(self):
        validate_name("O'Connor")

    def test_accepts_name_with_hyphen(self):
        validate_name("Mary-Jane")

    def test_accepts_name_with_spaces(self):
        validate_name("Mary Jane")

    def test_accepts_non_english_characters(self):
        validate_name("Γεώργιος")

    def test_rejects_name_with_numbers(self):
        with self.assertRaises(ValidationError) as cm:
            validate_name("John123")
        self.assertEqual(cm.exception.code, "name_invalid_characters")

    def test_rejects_markup_characters(self):
        with self.assertRaises(ValidationError) as cm:
            validate_name("<script>alert('XSS')</script>")
        self.assertEqual(cm.exception.code, "name_invalid_characters")


class UppercaseValidatorTests(SimpleTestCase):
    def setUp(self):
        self.validator = UppercaseValidator()

    def test_accepts_password_with_uppercase_letter(self):
        self.validator.validate("Abcdef1!")

    def test_rejects_password_without_uppercase_letter(self):
        with self.assertRaises(ValidationError) as cm:
            self.validator.validate("abcdef1!")
        self.assertEqual(cm.exception.code, "password_no_upper")


class NumberValidatorTests(SimpleTestCase):
    def setUp(self):
        self.validator = NumberValidator()

    def test_accepts_password_with_number(self):
        self.validator.validate("Abcdef1!")

    def test_rejects_password_without_number(self):
        with self.assertRaises(ValidationError) as cm:
            self.validator.validate("Abcdef!")
        self.assertEqual(cm.exception.code, "password_no_number")


class SymbolValidatorTests(SimpleTestCase):
    def setUp(self):
        self.validator = SymbolValidator()

    def test_accepts_password_with_symbol(self):
        self.validator.validate("Abcdef1!")

    def test_rejects_password_without_symbol(self):
        with self.assertRaises(ValidationError) as cm:
            self.validator.validate("Abcdef1")
        self.assertEqual(cm.exception.code, "password_no_symbol")

    def test_whitespace_does_not_count_as_symbol(self):
        with self.assertRaises(ValidationError) as cm:
            self.validator.validate("Abcdef1  ")
        self.assertEqual(cm.exception.code, "password_no_symbol")


class PasswordSettingsTests(SimpleTestCase):
    def test_custom_validators_are_registered(self):
        with self.assertRaises(ValidationError) as cm:
            validate_password("longlowercaseword")

        codes = {error.code for error in cm.exception.error_list}
        expected = {"password_no_upper", "password_no_symbol", "password_no_number"}
        self.assertLessEqual(expected, codes)