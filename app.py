from flask import Flask, render_template, request, redirect
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Post, Tag, PostTag

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()

app.config['SECRET_KEY'] = 'notmuchofasecret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
debug = DebugToolbarExtension(app)


@app.route('/')
def home():
    top_posts = Post.get_top_posts()
    return render_template('home.html', posts=top_posts)


@app.route('/users')
def get_users():
    users = User.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/new', methods=['GET'])
def show_add_user_form():
    return render_template('add_user.html')


@app.route('/users/new', methods=['POST'])
def create_user():
    first_name = request.form.get('first-name')
    last_name = request.form.get('last-name')
    image_url = request.form.get('image-url')

    user = User(first_name=first_name, last_name=last_name)

    db.session.add(user)
    db.session.commit()

    return redirect('/users')


@app.route('/users/<int:user_id>')
def get_user_detail(user_id):
    user = User.query.get_or_404(user_id)
    # posts = Post.query.filter_by(user_id=user_id).all()
    return render_template('user_detail.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['GET'])
def show_user_detail_form(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('edit_user_detail.html', user=user)


@app.route('/users/<int:user_id>/edit', methods=['POST'])
def update_user_detail(user_id):
    user = User.query.get_or_404(user_id)

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


@app.route('/users/<int:user_id>/posts/new')
def show_create_post_form(user_id):
    user = User.query.get_or_404(user_id)
    return render_template('add_post.html', user=user)


@app.route('/users/<int:user_id>/posts/new', methods=['POST'])
def add_post(user_id):
    new_post = Post(request.form.get('title'),
                    request.form.get('content'),
                    user_id)

    db.session.add(new_post)
    db.session.commit()

    return redirect(f'/users/{user_id}')


@app.route('/posts/<int:post_id>')
def show_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('post_detail.html', post=post)


@app.route('/posts/<int:post_id>/edit')
def show_edit_post_form(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('edit_post_detail.html', post=post)


@app.route('/posts/<int:post_id>/edit', methods=['POST'])
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    post.title = request.form.get('title')
    post.content = request.form.get('content')

    db.session.add(post)
    db.session.commit()

    return redirect(f'/posts/{post_id}')


@app.route('/posts/<int:post_id>/delete', methods=['POST'])
def delete_post(post_id):
    user_id = db.session.query(Post.user_id).filter_by(id=post_id).one()
    Post.query.filter_by(id=post_id).delete()

    db.session.commit()

    return redirect(f'/users/{user_id[0]}')


@app.route('/tags')
def show_tags():
    tags = Tag.query.all()

    return render_template('tags.html', tags=tags)


@app.route('/tags/<int:tag_id>')
def show_tag_detail(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    return render_template('tag_detail.html', tag=tag)


@app.route('/tags/new')
def show_add_tag_form():
    return render_template('add_tag.html')


@app.route('/tags/new', methods=['POST'])
def add_tag():
    new_tag = Tag(name=request.form.get('name'))

    db.session.add(new_tag)

    db.session.commit()

    return redirect('/tags')


@app.route('/tags/<int:tag_id>/edit')
def show_edit_tag_form(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    return render_template('edit_tag_detail.html', tag=tag)


@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def edit_tag(tag_id):
    tag = Tag.query.get_or_404(tag_id)

    tag.name = request.form.get('name')

    db.session.add(tag)

    db.session.commit()

    return redirect('/tags')


@app.route('/tags/<int:tag_id>/edit', methods=['POST'])
def delete_tag(tag_id):
    Tag.query.filter_by(id=tag_id).delete()

    db.session.commit()

    return redirect('/tags')
