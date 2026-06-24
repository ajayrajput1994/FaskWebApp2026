# app/models/profile.py
from app.extensions import db


class Profile(db.Model):
    __tablename__ = 'profiles'

    id = db.Column(db.Integer, primary_key=True)
    bio = db.Column(db.Text,       nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)

    # Foreign key — links this row to a user
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                        unique=True,   # unique=True enforces one-to-one
                        nullable=False)

    # Back-reference to the User object
    user = db.relationship('User', back_populates='profile')