# app/models/post.py
from app.extensions import db
from datetime import datetime
from app.models.tag import post_tags, Tag


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer,     primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    body = db.Column(db.Text,        nullable=False)
    created_at = db.Column(db.DateTime,    default=datetime.utcnow)
    # Foreign key on the "many" side
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    # Relationship back to User
    author = db.relationship('User',    back_populates='posts')
    # Relationship forward to Comment
    comments = db.relationship('Comment', back_populates='post',
                               cascade='all, delete-orphan',
                               lazy='dynamic')
    # tags = db.relationship('Tag', secondary=post_tags, backref='posts')
    tags = db.relationship('Tag', secondary=post_tags,  # the association table
                            backref=db.backref('posts', lazy='dynamic'),
                            lazy='dynamic')
    # lazy='dynamic': comments is a query object, not a loaded list.
    # Use when a post might have thousands of comments.
    # post.comments.filter_by(user_id=1).all()  ← runs a SQL query
    # post.comments.count()                      ← efficient COUNT query