"""Models for Blogly."""
from time import strftime

from flask_sqlalchemy import SQLAlchemy
import datetime

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


DEFAULT_IMAGE_URL = 'https://picsum.photos/200'


class User(db.Model):
    """Users model"""

    __tablename__ = 'users'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    first_name = db.Column(db.String(50),
                           nullable=False)
    last_name = db.Column(db.String(50),
                          nullable=True)
    image_url = db.Column(db.String(2048),
                          nullable=True,
                          default=DEFAULT_IMAGE_URL)

    @classmethod
    def get_all_users(cls):
        return User.query.order_by(cls.last_name, cls.first_name).all()

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def __repr__(self):
        return f"<User {self.id}, {self.first_name} {self.last_name} {self.image_url}>"

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()


class Post(db.Model):
    """Blog post"""

    __tablename__ = 'posts'

    id = db.Column(db.Integer,
                   primary_key=True,
                   autoincrement=True)
    title = db.Column(db.Text,
                      nullable=False)
    content = db.Column(db.Text,
                        nullable=False)
    created_at = db.Column(db.DateTime,
                           nullable=False,
                           default=datetime.datetime.now())
    user_id = db.Column(db.Integer,
                        db.ForeignKey('users.id', ondelete='CASCADE'),
                        nullable=False)

    user = db.relationship('User', backref='posts')

    def __init__(self, title, content, user_id):
        self.title = title,
        self.content = content,
        self.user_id = user_id

    def __repr__(self):
        return f"<Post {self.id} {self.title} {self.content} {self.created_at} {self.user_id}>"

    @classmethod
    def get_top_posts(cls):
        return db.session.query(Post).order_by(Post.created_at.desc()).limit(5)
