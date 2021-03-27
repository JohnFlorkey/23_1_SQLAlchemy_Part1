"""Models for Blogly."""
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()


def connect_db(app):
    db.app = app
    db.init_app(app)


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
                          nullable=True)

    @classmethod
    def get_all_users(cls):
        return User.query.order_by(cls.last_name, cls.first_name).all()

    def __init__(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    @hybrid_property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()
