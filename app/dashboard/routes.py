# app/dashboard/routes.py
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.model import User
from . import dashboard_bp
from app.auth import role_required
from app.extensions import db
import logging
from flask import current_app
security_log = logging.getLogger('security')


@dashboard_bp.route('/')
@login_required
def index():
    """Main dashboard — stats visible to admin only, welcome card for all."""
    stats = None
    if current_user.has_role('admin'):
        stats = {
            'total':      User.query.count(),
            'admins':     User.count_by_role('admin'),
            'editors':    User.count_by_role('editor'),
            'viewers':    User.count_by_role('viewer'),
            'new_week':   User.new_this_week(),
        }
    return render_template('dashboard/index.html', stats=stats)


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
@role_required('admin')            
def admin_panel():
    """Admin user management table with optional search."""
    search = request.args.get('q', '').strip().lower()
    query = User.query.order_by(User.created_at.desc())
    if search:
        query = query.filter(
            db.or_(
                User.username.ilike(f'%{search}%'),
                User.email.ilike(f'%{search}%'),
            )
        )
    users = query.all()
    return render_template('dashboard/admin.html',
                           users=users, search=search)



@dashboard_bp.route('/admin/change-role/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def change_role(user_id):
    """Changes a user's role. Cannot demote yourself."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot change your own role.', 'warning')
        return redirect(url_for('dashboard.admin_panel'))
    new_role = request.form.get('role')
    if new_role not in ('admin', 'editor', 'viewer'):
        flash('Invalid role.', 'danger')
        return redirect(url_for('dashboard.admin_panel'))
    old_role = user.role
    user.role = new_role
    db.session.commit()
    security_log.warning(
        'ROLE_CHANGE admin_id=%s target_user_id=%s %s→%s ip=%s',
        current_user.id, user.id, old_role, new_role,
        request.remote_addr,
    )
    flash(f'{user.username} is now {new_role}.', 'success')
    return redirect(url_for('dashboard.admin_panel'))


@dashboard_bp.route('/admin/delete/<int:user_id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_user(user_id):
    """Deletes a user. Cannot delete yourself."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash('You cannot delete your own account here.', 'warning')
        return redirect(url_for('dashboard.admin_panel'))
    email = user.email
    db.session.delete(user)
    db.session.commit()
    security_log.warning(
        'USER_DELETED admin_id=%s deleted_email=%s ip=%s',
        current_user.id, email, request.remote_addr,
    )
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('dashboard.admin_panel'))


@dashboard_bp.route('/users')
@login_required
def users():
    if not current_user.is_admin():
        abort(403)               
    all_users = User.query.all()
    return render_template('dashboard/users.html', users=all_users)
