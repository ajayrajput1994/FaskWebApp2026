from app.extensions import db
from datetime import datetime


class Invoice(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    # Every resource MUST have org_id — this is what isolates tenants
    organisation_id = db.Column(db.Integer,
                                db.ForeignKey('organisations.id'),
                                nullable=False)
    # ... your fields ...
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    organisation = db.relationship('Organisation')
    