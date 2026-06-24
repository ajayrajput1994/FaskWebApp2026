from flask import jsonify
from flask_login import login_required, current_user
from app.model import User
from . import api_bp


@api_bp.route('/status')
def status():
    """Public health-check endpoint."""
    return jsonify({'status': 'ok', 'version': '1.0'})


@api_bp.route('/me')
@login_required
def me():
    """Returns the logged-in user as JSON."""
    return jsonify({
        'id':       current_user.id,
        'username': current_user.username,
        'email':    current_user.email,
        'role':     current_user.role,
    })


@api_bp.route('/users')
@login_required
def list_users():
    if not current_user.is_admin():
        return jsonify({'error': 'Forbidden'}), 403
    users = User.query.all()
    return jsonify([
        {'id': u.id, 'username': u.username, 'email': u.email}
        for u in users
    ])