# app/organisations/routes.py

from flask import Blueprint, session, redirect, url_for, g
from flask_login import login_required, current_user
from app.models.organisation import Organisation, Membership
from app.extensions import db
import re

org_bp = Blueprint('org', __name__)


def get_current_org():
    """Returns the active Organisation for this session, or None."""
    org_id = session.get('active_org_id')
    if not org_id:
        return None
    return Organisation.query.get(org_id)


def require_org(f):
    """Decorator: ensures a valid org is in session before the view runs."""
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        org = get_current_org()
        if not org:
            return redirect(url_for('org.select'))
        # Verify current user is actually a member
        member = Membership.query.filter_by(
            user_id=current_user.id,
            organisation_id=org.id
        ).first()
        if not member:
            session.pop('active_org_id', None)
            return redirect(url_for('org.select'))
        g.org = org
        g.membership = member
        return f(*args, **kwargs)
    return decorated


@org_bp.route('/organisations/create', methods=['GET', 'POST'])
@login_required
def create():
    from flask import request, render_template, flash
    from .forms import CreateOrgForm
    form = CreateOrgForm()
    if form.validate_on_submit():
        slug = re.sub(r'[^a-z0-9]+', '-',
                      form.name.data.lower()).strip('-')
        org = Organisation(name=form.name.data, slug=slug)
        db.session.add(org)
        db.session.flush()   # get org.id before commit
        membership = Membership(user_id=current_user.id,
                                organisation_id=org.id,
                                role='owner')
        db.session.add(membership)
        db.session.commit()
        session['active_org_id'] = org.id
        flash(f'Organisation "{org.name}" created.', 'success')
        return redirect(url_for('dashboard.index'))
    return render_template('org/create.html', form=form)


@org_bp.route('/organisations/select')
@login_required
def select():
    from flask import render_template
    orgs = current_user.get_organisations()
    if len(orgs) == 1:
        session['active_org_id'] = orgs[0].id
        return redirect(url_for('dashboard.index'))
    return render_template('org/select.html', orgs=orgs)


@org_bp.route('/organisations/switch/<int:org_id>')
@login_required
def switch(org_id):
    membership = Membership.query.filter_by(
        user_id=current_user.id, organisation_id=org_id
    ).first_or_404()
    session['active_org_id'] = org_id
    return redirect(url_for('dashboard.index'))
