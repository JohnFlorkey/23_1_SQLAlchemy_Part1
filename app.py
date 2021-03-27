from flask import Flask, render_template, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = 'notmuchofasecret'
debug = DebugToolbarExtension(app)


@app.route('/')
def home():
    return redirect('/users')


@app.route('/users')
def get_users():
    users = User.query.all()
    return render_template('users.html', users=users)


@app.route('/users/new', methods=['GET'])
def show_add_user_form():
    return render_template('add_user.html')


@app.route('/users/new', methods=['POST'])
def create_user():
    first_name = request.form.get('first-name')
    last_name = request.form.get('last-name')
    image_url = request.form.get('image-url')

    user = User(first_name=first_name, last_name=last_name, image_url=image_url)

    db.session.add(user)
    db.session.commit()

    return redirect('/users')


@app.route('/users/<int:user_id>')
def get_user_detail(user_id):
    user = User.query.get(user_id)
    return render_template('user_detail.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['GET'])
def show_user_detail_form(user_id):
    user = User.query.get(user_id)
    return render_template('edit_user_detail.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['POST'])
def update_user_detail(user_id):
    # first_name = request.form.get('first-name')
    # last_name = request.form.get('last-name')
    # image_url = request.form.get('image-url')

    # user = User(id=user_id, first_name=first_name, last_name=last_name, image_url=image_url)
    user = User.query.get(user_id)

    user.first_name = request.form.get('first-name')
    user.last_name = request.form.get('last-name')
    user.image_url = image_url = request.form.get('image-url')

    db.session.add(user)
    db.session.commit()

    return redirect('/users')


@app.route('/users/<int:user_id>/delete', methods=['POST'])
def delete_user(user_id):
    User.query.filter_by(id=user_id).delete()

    db.session.commit()

    return redirect('/users')