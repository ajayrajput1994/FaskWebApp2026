# app/models/tag.py
from app.extensions import db

# Step 1: Define the association table (NOT a model — just a Table)
post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'),
              primary_key=True),
    db.Column('tag_id',  db.Integer, db.ForeignKey('tags.id'),
              primary_key=True)
    # Both columns together form a composite primary key —
    # prevents the same post-tag pair appearing twice.
)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer,    primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)

    # Relationship back to Post (defined on Post side)
    # posts is available here via backref