# app/auth/routes.py
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from app.extensions import db, limiter
from app.model import User
from .utils import role_required, send_welcome_email
from .forms import RegistrationForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from .utils import role_required, send_welcome_email, \
                   generate_reset_token, verify_reset_token, send_reset_email
import logging
security_log = logging.getLogger('security')


@auth_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit('5 per hour')     # max 5 registrations per IP per hour
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    
    form = RegistrationForm()

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not username or not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/register.html', form=form)
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'warning')
            return render_template('auth/register.html', form=form)
        
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data.lower(),  
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        security_log.warning(
            'REGISTER_SUCCESS user_id=%s email=%s ip=%s',
            user.id, user.email, request.remote_addr,
        )
        try:
            send_welcome_email(user)
        except Exception as e:
            # Log the failure but do not crash the request
            from flask import current_app
            current_app.logger.error(
                'Welcome email failed for %s: %s', user.email, str(e)
            ) 
        flash('Account created! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)


@auth_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit('10 per minute')  # max 10 login attempts per IP per minute
@limiter.limit('50 per hour')    # and max 50 per hour (stacked)
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))
    form = LoginForm()    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        if not email or not password:
            flash('All fields are required.', 'danger')
            return render_template('auth/login.html', form=form)
        
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            security_log.warning(
                'LOGIN_SUCCESS user_id=%s email=%s ip=%s',
                user.id, user.email, request.remote_addr,
            )
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('dashboard.index'))

        security_log.warning(
            'LOGIN_FAILED email=%s ip=%s',
            form.email.data.strip().lower(),
            request.remote_addr,
        )
        flash('Invalid email or password.', 'danger')
    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
@limiter.exempt   # never block logout
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
@limiter.limit('3 per hour')   # max 3 reset requests per IP per hour
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    form = ForgotPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(
            email=form.email.data.strip().lower()
        ).first()

        if user:
            try:
                token = generate_reset_token(user.email)
                send_reset_email(user, token)
            except Exception as e:
                from flask import current_app
                current_app.logger.error(
                    'Reset email failed for %s: %s', user.email, str(e)
                )

        # ALWAYS show the same message whether the email exists or not.
        # Showing "email not found" tells attackers which emails are registered.
        flash(
            'If that email is registered, a reset link has been sent.',
            'info'
        )
        return redirect(url_for('auth.login'))

    return render_template('auth/forgot_password.html', form=form)


@auth_bp.route('/reset/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    # Verify token before showing the form
    email = verify_reset_token(token)
    if not email:
        # Token is expired or tampered — show error and send them back
        flash('That reset link is invalid or has expired.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    form = ResetPasswordForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()
        if not user:
            flash('User not found.', 'danger')
            return redirect(url_for('auth.forgot_password'))

        user.set_password(form.password.data)
        db.session.commit()

        flash('Your password has been updated. Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form, token=token)
