# 🔐 SecureGate – Secure Login System

## About the Project

SecureGate is a web-based authentication system developed using Python Flask and SQLite. The project focuses on making user login and registration safer by implementing password hashing, input validation, and secure session management.

The main idea behind SecureGate is to understand how authentication works in real-world applications and how basic security practices can help protect user accounts from unauthorized access.

## 🚀 Features

- **User Registration:** Create a new account with basic input validation.
- **Secure Login:** Authenticate users using their registered credentials.
- **Password Hashing:** Uses bcrypt to store passwords securely instead of plain text.
- **SQL Injection Protection:** Uses parameterized SQL queries.
- **Session Management:** Maintains authenticated user sessions.
- **Logout Functionality:** Securely ends the active session.
- **CSRF Protection:** Validates form submissions to prevent cross-site request forgery.
- **Dashboard:** Provides a protected page accessible only after login.

## 🛠️ Technologies Used

- Python
- Flask
- SQLite
- Bcrypt
- HTML5
- CSS3

## ⚙️ Installation and Setup

**1. Clone the repository**

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

**2. Open the project folder**

```bash
cd SecureGate
```

**3. Create a virtual environment**

```bash
python -m venv .venv
```

**4. Activate the environment (Windows)**

```bash
.venv\Scripts\activate
```

**5. Install dependencies**

```bash
pip install -r requirements.txt
```

**6. Run the application**

```bash
python app.py
```

**7. Open in your browser**

```text
http://127.0.0.1:5000
```

## 🎯 Project Objective

The objective of SecureGate is to build a simple authentication system while learning practical cybersecurity concepts such as password security, database protection, input validation, and session handling.

## 🔮 Future Improvements

- Two-Factor Authentication (2FA)
- Password reset functionality
- Email verification
- Login attempt limiting
- Security activity logs

## 👨‍💻 Project Status

Developed as a practical cybersecurity and web development project to explore secure authentication techniques.

**Note:** This is an educational project. Additional security testing and production hardening are required before real-world deployment.
