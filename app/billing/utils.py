# app/billing/utils.py  ← CREATE

from functools import wraps
from flask import redirect, url_for, flash
from flask import g


def requires_paid_plan(f):
    """
    Blocks access to a route if the current org is on the free plan.
    Use after @require_org so g.org is already set.
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        if not g.org.is_on_paid_plan():
            flash('This feature requires a paid plan.', 'warning')
            return redirect(url_for('billing.pricing'))
        return f(*args, **kwargs)
    return decorated
