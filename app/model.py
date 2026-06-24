# app/models.py
from app.extensions import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import bcrypt


class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    age = db.Column(db.Integer,  nullable=True)
    salary = db.Column(db.Float,    nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=True)
    is_active = db.Column(db.Boolean, default=True,  nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    role = db.Column(db.String(20), default='viewer', index=True)
    preferences = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow,
                           onupdate=datetime.utcnow)
    profile = db.relationship('Profile', back_populates='user',
                              uselist=False,      # returns object, not list
                              cascade='all, delete-orphan')
    posts = db.relationship('Post', back_populates='author',
                            lazy='dynamic',
                            cascade='all, delete-orphan')
    comments = db.relationship('Comment', back_populates='author',
                            lazy='dynamic',
                            cascade='all, delete-orphan')

    def set_password(self, raw):
        self.password = bcrypt.hashpw(
            raw.encode(), bcrypt.gensalt()
        ).decode()

    def check_password(self, raw):
        return bcrypt.checkpw(raw.encode(), self.password.encode())

    def user_is_admin(self):
        return self.role == 'admin'

    def __repr__(self):
        return f'<User {self.username}>'

    def check_password(self, raw):
        return bcrypt.checkpw(raw.encode(), self.password.encode())

    def has_role(self, *roles):
        """
        Returns True if the user's role matches ANY of the given role names.
        Usage: user.has_role('admin')
              user.has_role('admin', 'editor')
        """
        return self.role in roles

    @classmethod
    def count_by_role(cls, role):
        """Returns total users with the given role. Used by dashboard stats."""
        return cls.query.filter_by(role=role).count()

    @classmethod
    def new_this_week(cls):
        """Returns count of users registered in the last 7 days."""
        from datetime import datetime, timedelta
        cutoff = datetime.utcnow() - timedelta(days=7)
        return cls.query.filter(cls.created_at >= cutoff).count()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))