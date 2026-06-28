# app/models/organisation.py 

from app.extensions import db
from datetime import datetime


class Organisation(db.Model):
    __tablename__ = 'organisations'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    slug = db.Column(db.String(120), unique=True, nullable=False)
    # Stripe customer ID — set when they subscribe
    stripe_customer_id = db.Column(db.String(120), nullable=True)
    stripe_subscription_id = db.Column(db.String(120), nullable=True)
    plan = db.Column(db.String(20), default='free')
    # free | starter | pro
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    members = db.relationship('Membership', back_populates='organisation',
                                  cascade='all, delete-orphan')

    def is_on_paid_plan(self):
        return self.plan in ('starter', 'pro')


class Membership(db.Model):
    """Links a User to an Organisation with a role."""
    __tablename__ = 'memberships'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                                nullable=False)
    organisation_id = db.Column(db.Integer,
                                db.ForeignKey('organisations.id'),
                                nullable=False)
    # owner | admin | member
    role = db.Column(db.String(20), default='member', nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='memberships')
    organisation = db.relationship('Organisation', back_populates='members')
    