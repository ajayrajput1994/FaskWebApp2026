# app/billing/routes.py

import stripe
from flask import Blueprint, redirect, url_for, request, \
    current_app, flash, render_template
from flask_login import login_required, current_user
from app.organisations.routes import require_org, get_current_org
from app.extensions import db

billing_bp = Blueprint('billing', __name__)


@billing_bp.route('/billing/checkout/<plan>')
@login_required
@require_org
def checkout(plan):
    """Redirects to Stripe Checkout to start a subscription."""
    from flask import g
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']

    price_map = {
        'starter': current_app.config['STRIPE_STARTER_PRICE_ID'],
        'pro':     current_app.config['STRIPE_PRO_PRICE_ID'],
    }
    price_id = price_map.get(plan)
    if not price_id:
        flash('Invalid plan.', 'danger')
        return redirect(url_for('billing.pricing'))

    org = g.org
    # Create Stripe customer if first time
    if not org.stripe_customer_id:
        customer = stripe.Customer.create(
            email=current_user.email,
            name=org.name,
            metadata={'org_id': org.id},
        )
        org.stripe_customer_id = customer.id
        db.session.commit()

    session = stripe.checkout.Session.create(
        customer=org.stripe_customer_id,
        mode='subscription',
        line_items=[{'price': price_id, 'quantity': 1}],
        success_url=url_for('billing.success', _external=True)
                    + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('billing.pricing', _external=True),
        metadata={'org_id': org.id, 'plan': plan},
    )
    return redirect(session.url, code=303)


@billing_bp.route('/billing/success')
@login_required
def success():
    flash('Subscription active! Welcome to the paid plan.', 'success')
    return redirect(url_for('dashboard.index'))


@billing_bp.route('/billing/portal')
@login_required
@require_org
def portal():
    """Redirects to Stripe's hosted customer portal for plan management."""
    from flask import g
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    org = g.org
    if not org.stripe_customer_id:
        flash('No active subscription found.', 'warning')
        return redirect(url_for('billing.pricing'))
    session = stripe.billing_portal.Session.create(
        customer=org.stripe_customer_id,
        return_url=url_for('dashboard.index', _external=True),
    )
    return redirect(session.url, code=303)


@billing_bp.route('/billing/webhook', methods=['POST'])
def webhook():
    """
    Stripe sends events here when payment succeeds, fails, or
    a subscription is cancelled. This is how your DB stays in sync.
    """
    stripe.api_key = current_app.config['STRIPE_SECRET_KEY']
    payload = request.get_data()
    sig     = request.headers.get('Stripe-Signature')
    secret  = current_app.config['STRIPE_WEBHOOK_SECRET']

    try:
        event = stripe.Webhook.construct_event(payload, sig, secret)
    except stripe.error.SignatureVerificationError:
        return 'Invalid signature', 400

    from app.models.organisation import Organisation

    if event['type'] == 'checkout.session.completed':
        data = event['data']['object']
        org_id = int(data['metadata']['org_id'])
        plan   = data['metadata']['plan']
        sub_id = data['subscription']
        org = Organisation.query.get(org_id)
        if org:
            org.plan = plan
            org.stripe_subscription_id = sub_id
            db.session.commit()

    elif event['type'] in ('customer.subscription.deleted',
                           'invoice.payment_failed'):
        sub = event['data']['object']
        org = Organisation.query.filter_by(
            stripe_subscription_id=sub['id']
        ).first()
        if org:
            org.plan = 'free'
            db.session.commit()

    return 'ok', 200


@billing_bp.route('/pricing')
def pricing():
    return render_template('billing/pricing.html')


