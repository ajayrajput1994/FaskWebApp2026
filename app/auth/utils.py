# app/auth/utils.py  ← CREATE this new file
from flask import current_app, render_template, url_for
from flask_mail import Message
from app.extensions import mail
from functools import wraps
from flask import abort
from flask_login import current_user
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature


def role_required(*roles):
    """
    Decorator that restricts a route to users who have one of the given roles.

    Usage on a route:
        @dashboard_bp.route('/admin')
        @login_required        ← always put this FIRST
        @role_required('admin')
        def admin_panel():
            ...

        @dashboard_bp.route('/content')
        @login_required
        @role_required('admin', 'editor')  ← multiple roles allowed
        def content_page():
            ...

    What happens on failure:
        - Not logged in         → @login_required already redirects to login
        - Logged in, wrong role → abort(403) shows the 403 error page
    """
    def decorator(f):
        @wraps(f)          # preserves the original function name and docstring
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if not current_user.has_role(*roles):
                abort(403)  # Forbidden — logged in but wrong role
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def send_email(subject, recipients, html_body, text_body=None):
    """
    Central email sending function. All emails in the app go through here.

    subject    — email subject line (string)
    recipients — list of email addresses, e.g. ['user@example.com']
    html_body  — rendered HTML string (from render_template)
    text_body  — plain text fallback (optional but good practice)
    """
    msg = Message(
        subject=subject,
        recipients=recipients,         # list of strings
        html=html_body,
        body=text_body or 'Please view this email in an HTML-capable client.',
    )
    mail.send(msg)


def send_welcome_email(user):
    """Sends a welcome email after registration."""
    send_email(
        subject='Welcome to MyApp!',
        recipients=[user.email],
        html_body=render_template(
            'auth/email/welcome.html',
            username=user.username,
        ),
        text_body=f'Hi {user.username}, welcome to MyApp!',
    )


def generate_reset_token(email):
    """
    Creates a signed, time-stamped token encoding the user's email.
    itsdangerous signs it with SECRET_KEY so nobody can forge it.
    """
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return s.dumps(email, salt='password-reset-salt')


def verify_reset_token(token, expiry_seconds=1800):
    """
    Decodes and verifies a reset token.
    Returns the email address if valid, or None if expired / tampered.
    expiry_seconds=1800 means tokens expire after 30 minutes.
    """
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        email = s.loads(token, salt='password-reset-salt',
                        max_age=expiry_seconds)
    except (SignatureExpired, BadSignature):
        return None       # token is expired or was tampered with
    return email


def send_reset_email(user, token):
    """Sends the password reset email with the signed token link."""
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    # _external=True produces a full URL: http://127.0.0.1:5000/auth/reset/<token>
    send_email(
        subject='Reset your MyApp password',
        recipients=[user.email],
        html_body=render_template(
            'auth/email/reset_password.html',
            username=user.username,
            reset_url=reset_url,
        ),
        text_body=(
            f'Hi {user.username},\n\n'
            f'Click the link below to reset your password (valid 30 minutes):\n'
            f'{reset_url}\n\n'
            f'If you did not request this, ignore this email.'
        ),
    )
