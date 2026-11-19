# HFM Back-end Exercise: Registration and Login

A Django implementation of the HF Markets landing-page exercise: a registration
form and a login page, with validation on both the server and the browser,
backed by SQLite.

- **Back end:** Python, Django 5.2 (LTS), SQLite
- **Front end:** Django templates, plain CSS and vanilla JavaScript (no build step)
- **Tests:** 54 automated tests (validators, forms and views)

## Running the project

No configuration is needed for local use: without a `.env` file the project
runs with development settings.

**Python version:** the uv instructions require Python 3.14, as set in
`pyproject.toml`. On Python 3.10 to 3.13, use the pip instructions instead:
`requirements.txt` has no Python version limit, and Django 5.2 supports
Python 3.10 and later.

### With uv

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

### With pip

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

Then open <http://127.0.0.1:8000/>.

To browse stored users in the admin, create an account with
`python manage.py createsuperuser` and open <http://127.0.0.1:8000/admin/>.

### Running the tests

```bash
uv run python manage.py test accounts    # or: python manage.py test accounts
```

## Pages

| URL | Page |
|---|---|
| `/` | Registration form (landing page) |
| `/signup/done/` | Thank-you message after a successful registration |
| `/login/` | Login form |
| `/dashboard/` | Account details, for logged-in users only |
| `/logout/` | Logs out (POST only, from the header button) |
| `/admin/` | Django admin |

## How the requirements are met

| Requirement | Implementation |
|---|---|
| Server-side validation in Python | Django forms and model validators (`accounts/forms.py`, `accounts/validators.py`) |
| SQLite with validation and security | Django ORM on SQLite; database-level unique constraint on email; see [Security](#security) |
| First and last name: length > 3 | `validate_name`: at least 4 characters after trimming spaces |
| Country code numeric | Digits only, and must match the selected country |
| Email format | Django's email validator, with a custom message |
| Password: 1 capital, 1 number, 1 symbol | Three custom password validators registered in `AUTH_PASSWORD_VALIDATORS` |
| Clear, specific error messages | Each rule has its own message and error code (`accounts/error_messages.py`); all failing password rules are shown at once |
| Thank-you message after sign-up | `/signup/done/`: "Thank you for signing up, {first name}!" |
| Email validation on login | `EmailLoginForm` checks the format before checking credentials |
| Country selection fills the phone code | `static/js/signup.js`, using three sample countries: Cyprus (+357), Greece (+30), United Kingdom (+44) |
| Front-end validation with the same rules | `static/js/signup.js`, using the same messages as the server |
| Responsive form | Mobile-first CSS; checked at 375 px and desktop widths |

## Validation rules

| Field | Rule | Browser | Server |
|---|---|---|---|
| First / last name | At least 4 characters; letters in any alphabet, with single spaces, hyphens or apostrophes between them | ✓ | ✓ |
| Country | One of the listed countries | ✓ | ✓ |
| Country code | 1–4 digits, matching the selected country | ✓ | ✓ |
| Phone | 6–15 digits | ✓ | ✓ |
| Email | Valid format | ✓ (basic) | ✓ (full) |
| Email | Not already registered (case-insensitive) | | ✓ |
| Password | At least 8 characters, one uppercase letter (A–Z), one number, one symbol | ✓ | ✓ |
| Password | Not a common password, not too similar to the user's details | | ✓ |
| Terms | Must be accepted; the acceptance time is stored | ✓ | ✓ |

The server is the source of truth. Browser checks give quick feedback, but every
rule is enforced again on the server, so disabling JavaScript or sending
requests directly cannot bypass them. With JavaScript disabled, the form still
works and shows the server's messages in the same places.

## How it is built

- **Custom user model** (`accounts/models.py`) that logs in with email instead of
  a username, created before the first migration. Its manager lowercases emails
  and always hashes passwords.
- **Validators** are attached to the model fields, so they apply everywhere the
  model is edited, including the admin. The password rules are registered as Django password validators, so they also apply to `createsuperuser` and `changepassword`.
- **`SignupForm`** is a `ModelForm` that adds the password and terms fields,
  checks that the country code matches the country, and validates the password
  against the user's other details.
- **`EmailLoginForm`** follows the interface of Django's `AuthenticationForm`,
  so it plugs into Django's built-in `LoginView`.
- **Single sources of truth:** the country list (`accounts/countries.py`) feeds
  the model choices, the server-side check and the autofill. The error messages
  (`accounts/error_messages.py`) and the minimum password length are passed to
  the browser with Django's `json_script`, so both sides show the same text.
- **Views** use Django's generic views. Registration follows POST-redirect-GET,
  so refreshing the thank-you page cannot resubmit the form.
- **Progressive enhancement:** the code box only becomes read-only, and the
  show-password button only appears, when JavaScript is running.

## Security

- **SQL injection:** all queries go through the Django ORM, which uses
  parameterised queries.
- **Passwords** are hashed with Django's PBKDF2 hasher and never stored or
  re-displayed in plain text.
- **CSRF protection** on every form, including logout, which only accepts POST.
- **XSS:** template output is auto-escaped, the JavaScript inserts messages as
  text (`textContent`), and data is passed to scripts with `json_script`. Names
  are also restricted to letters and a few separators.
- **Duplicate accounts:** emails are stored lowercase, and a database unique
  constraint is the final guard. If two registrations with the same email
  arrive at the same moment, the second gets the normal "already exists"
  message instead of a server error.
- **Login:** a wrong password, an unknown email and a deactivated account all
  give the same message, so the login page does not reveal which emails are
  registered.
- **Django defaults** also protect against clickjacking (`X-Frame-Options: DENY`)
  and MIME-type sniffing.

### Settings left at development values

The project is configured for running locally:

- `DEBUG` is on unless `DJANGO_DEBUG=False` is set.
- Without `DJANGO_SECRET_KEY`, a development key from the source code is used.
- HTTPS-only cookies, HTTPS redirects and HSTS are not enabled, and
  `ALLOWED_HOSTS` is fixed to `localhost` and `127.0.0.1`.

A production deployment would require the secret key from the environment,
read `ALLOWED_HOSTS` from the environment, and enable the HTTPS settings when
`DEBUG` is off. `python manage.py check --deploy` lists what remains.

## Assumptions and limitations

- **"Length > 3"** is read literally: names need at least 4 characters. It is
  one constant (`NAME_MIN_LENGTH`) if a different reading is intended.
- **Uppercase and symbol rules** use A–Z, so the browser and server match
  exactly. A capital letter from another alphabet (such as Greek `Γ`) counts
  as a symbol, not as the required uppercase letter.
- **Email in the browser** is a basic format check; the server's stricter check
  decides.
- **Privacy Policy and Terms links** are placeholders (`#`), as there are no
  policy pages.

## Project layout

```
config/                 Settings and root URLs
accounts/
  models.py             Custom user model
  managers.py           User creation by email
  countries.py          Sample countries and dialling codes
  validators.py         Name and password rules
  error_messages.py     All validation messages
  forms.py              Registration and login forms
  views.py              Registration, thank-you, login and dashboard views
  urls.py
  tests/                Validator, form and view tests
templates/              Page templates and shared field fragments
static/
  css/main.css          Styles
  js/signup.js          Registration validation and country autofill
  js/password-toggle.js Show/hide password button
  img/                  Logo and background image
```

## Environment variables

All optional for local use. Copy `.env.example` to `.env` to set them.

| Variable | Default | Purpose |
|---|---|---|
| `DJANGO_SECRET_KEY` | development key | Signs sessions and CSRF tokens |
| `DJANGO_DEBUG` | `True` | Debug mode |

Developed and tested on Python 3.14 with Django 5.2.