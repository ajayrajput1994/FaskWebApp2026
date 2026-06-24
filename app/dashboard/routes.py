# app/dashboard/routes.py
from flask import render_template, abort
from flask_login import login_required, current_user
from app.model import User
from . import dashboard_bp
from app.auth import role_required

@dashboard_bp.route('/')
@login_required                  # redirects to auth.login if not logged in
def index():
    return render_template('dashboard/index.html')


@dashboard_bp.route('/profile')
@login_required
def profile():
    return render_template('dashboard/profile.html', user=current_user)



@dashboard_bp.route('/editor')
@login_required
@role_required('admin', 'editor')  
def editor_page():
    return render_template('dashboard/editor.html')

@dashboard_bp.route('/admin')
@login_required
@role_required('admin')            # ONLY admin can access
def admin_panel():
    all_users = User.query.all()
    return render_template('dashboard/admin.html', users=all_users)

@dashboard_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin():
        abort(403)                  
    all_users = User.query.all()
    return render_template('dashboard/users.html', users=all_users)