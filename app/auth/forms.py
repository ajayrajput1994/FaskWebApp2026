# app/auth/forms.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import (
    DataRequired,     # field cannot be empty
    Email,            # must be a valid email format
    Length,           # min/max character count
    EqualTo,          # must match another field's value
    ValidationError   # raised by custom validators
)
from app.model import User


class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[
        DataRequired(message='Username is required.'),
        Length(min=3, max=80,
               message='Username must be between 3 and 80 characters.'),
    ])

    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.'),
        Length(max=120),
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=8, message='Password must be at least 8 characters.'),
    ])

    confirm = PasswordField('Confirm password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords do not match.'),
        # EqualTo('password') means: this field's value must equal
        # the value of the field named 'password' in the same form.
    ])

    submit = SubmitField('Create account')

    # ── Custom cross-field validators ──────────────────────────────
    # Any method named validate_<fieldname> is called automatically
    # by form.validate_on_submit(). Raise ValidationError to fail.

    def validate_email(self, field):
        """Reject the form if this email is already registered."""
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError(
                'That email is already registered. Please log in instead.'
            )

    def validate_username(self, field):
        """Reject if username is already taken."""
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('That username is already taken.')


class LoginForm(FlaskForm):

    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Please enter a valid email address.'),
    ])

    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.'),
    ])

    remember = BooleanField('Keep me logged in')

    submit = SubmitField('Log in')


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(message='Email is required.'),
        Email(message='Enter a valid email address.'),
    ])
    submit = SubmitField('Send reset link')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New password', validators=[
        DataRequired(message='Password is required.'),
        Length(min=8, message='Password must be at least 8 characters.'),
    ])
    confirm = PasswordField('Confirm new password', validators=[
        DataRequired(message='Please confirm your password.'),
        EqualTo('password', message='Passwords do not match.'),
    ])
    submit = SubmitField('Set new password')
