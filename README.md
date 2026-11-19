# SecureGate — Secure Login System

SecureGate is a small, server-rendered login application built with Flask, SQLite, and bcrypt. It is designed as a cybersecurity learning project: the authentication flow is short enough to follow, and the tests show what each important control is expected to do.

## What the application includes

- Account registration and login.
- bcrypt password hashing with a work factor of 12; plaintext passwords are not saved.
- Username validation and password rules, including bcrypt's 72-byte input limit.
- Parameterized SQL statements rather than building queries from user input.
- A per-session CSRF token on every form that changes data.
- A protected dashboard and POST-only logout.
- Session contents are cleared and rebuilt after successful login.
- `HttpOnly`, `SameSite=Lax`, optional `Secure` session cookies, and basic browser security headers.
- Automated tests for registration, hashing, login, logout, CSRF checks, and protected pages.

## Requirements

- Python 3.10 or newer
- pip

## Run on Windows

Open PowerShell in the extracted project directory:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py app.py
```

If PowerShell does not allow virtual-environment activation, run the environment's Python directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

Visit **http://127.0.0.1:5000** in your browser.

## Run the tests

Stop the web server first, then run:

```powershell
py -m unittest discover -s tests -v
```

The tests use a temporary database, so they do not modify your normal `users.db` file.

## How to demonstrate it

1. Register a username such as `student_demo` with a password that meets the displayed rules.
2. Open the database with a SQLite viewer and inspect the `users` table. The password column contains a bcrypt hash, not the password you typed.
3. Log in and confirm that the dashboard displays your username.
4. Log out and try opening `/dashboard` directly; the app should send you to the login page.
5. Try a wrong password, a duplicate username, and a weak password.
6. Submit a POST request without its CSRF token using the test suite; it should be rejected.
7. Run the automated tests and explain what each test verifies.

## Project structure

```text
secure_login_system/
├── app.py                 # Routes, validation, database, and session logic
├── requirements.txt       # Python dependencies
├── users.db               # Created automatically on first run
├── templates/             # Jinja HTML pages
├── static/style.css       # Application styling
└── tests/test_app.py      # Automated regression tests
```

## Configuration

The default secret key is intentionally marked for local development only. Before deployment, set a long random key. Example for PowerShell:

```powershell
$env:SECRET_KEY = "replace-with-a-long-random-secret"
$env:COOKIE_SECURE = "1"
py app.py
```

Set `COOKIE_SECURE=1` only when the site is served over HTTPS; otherwise the browser will not send the session cookie over local plain HTTP. You can set `DATABASE_PATH` to choose another SQLite file.

## Security notes and current limitations

This is an educational starter application, not a production identity service. It does not currently provide multi-factor authentication, password reset, email verification, persistent login throttling, or an audit trail. The in-process Flask development server must not be exposed as a production server. A real deployment needs HTTPS, a production WSGI server, a strong secret stored outside source control, rate limiting, monitoring, backups, dependency updates, and a security review. The built-in browser headers are a useful baseline, not a complete security policy.

## Understanding and presenting the project

Be ready to explain these design choices in your own words:

- **bcrypt:** slows down password guessing and stores a salted password hash.
- **Parameterized SQL:** keeps submitted values separate from SQL syntax.
- **CSRF token:** helps ensure a form submission came from a page issued to that browser session.
- **Session protection:** limits access to the dashboard and clears the login state on logout.
- **Validation:** rejects malformed usernames and passwords before saving an account.
- **Automated tests:** check both successful flows and common invalid requests.

If you extend the project, add one feature at a time, write a test for it, and record what you changed and why.
