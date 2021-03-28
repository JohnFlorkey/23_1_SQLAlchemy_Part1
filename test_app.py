from unittest import TestCase
from app import app
from models import User, db, Post

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class AppTests(TestCase):

    def setUp(self):
        # remove any existing data before setting up test data
        Post.query.delete()         # remove anything in the posts table
        User.query.delete()         # remove anything in the users table

        """Add a test user"""
        user = User(first_name='Test', last_name='Person')
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id

        """Add a test post"""
        post = Post('First Post', 'Testing. Testing. 1,2,3', self.user_id)
        db.session.add(post)
        db.session.commit()

        self.post_id = post.id

    def tearDown(self):
        """Clean up any open transactions"""

        db.session.rollback()

    def test_root_redirect(self):
        """Root route should redirect to /users"""
        with app.test_client() as client:
            resp = client.get('/')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

    def test_get_users(self):
        """The test user defined in setUp() should be on /users"""
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)           # the users page was returned
            self.assertIn('Test Person', html)              # our test user is on the page

    def test_get_users_new(self):
        """The new user form should be presented"""
        with app.test_client() as client:
            resp = client.get('/users/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Create A User</h1>', html)   # the add_user page was rendered

    def test_post_users_new(self):
        """Test the add new user view"""
        data = {'first-name': 'Peter',
                'last-name': 'Parker'}
        with app.test_client() as client:
            resp = client.post('/users/new', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)           # the users pages was returned
            self.assertIn('Peter Parker', html)             # the new user is on the page

    def test_get_user_detail(self):
        """Test the user detail view"""
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('User Detail', html)              # the user detail page was returned
            self.assertIn('Test Person', html)              # the test user is on the page

    def test_get_user_edit(self):
        """Test the get edit user view"""
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Edit User</h1>', html)       # the edit user page was returned
            self.assertIn('value="Test"', html)             # the form is populated with the test user values

    def test_post_user_edit(self):
        """Test the post edit user view"""
        data = {'first-name': 'Peter',
                'last-name': 'Parker',
                'image-url': 'http://notaurl.com'}
        with app.test_client() as client:
            resp = client.post(f'/users/{self.user_id}/edit', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)           # the users pages was returned
            self.assertIn('Peter Parker', html)             # the updated user data is on the page

    def test_post_user_delete(self):
        """Test the delete user view"""
        with app.test_client() as client:
            resp = client.post(f'/users/{self.user_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)           # the users pages was returned
            self.assertNotIn('Test Person', html)           # the test user is not on the page

    def test_show_create_post_form(self):
        """Test the create new post view"""
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}/posts/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Add Post for Test Person</h1>', html)       # the add post form was rendered

    def test_add_post(self):
        """Test the creation of a new post"""
        data = {'title': 'Test Post',
                'content': 'This is test content.'}
        with app.test_client() as client:
            resp = client.post(f'/users/{self.user_id}/posts/new', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('User Detail', html)          # the user detail page was returned
            self.assertIn('Test Post', html)            # the new post is on the page

    def test_show_post(self):
        """Test the show post detail view"""
        with app.test_client() as client:
            resp = client.get(f'/posts/{self.post_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Post Detail', html)          # the post detail page was rendered
            self.assertIn('First Post', html)           # the test post is on the page

    def test_show_edit_post_form(self):
        """Test the edit post form view"""
        with app.test_client() as client:
            resp = client.get(f'/posts/{self.post_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Edit Post</h1>', html)           # the edit post detail page was rendered
            self.assertIn('value="First Post"', html)           # the form is populated with the test post data

    def test_edit_post(self):
        """Test the edit post view"""
        data = {'title': 'Updated Post',
                'content': 'This is updated test content.'}
        with app.test_client() as client:
            resp = client.post(f'/posts/{self.post_id}/edit', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Post Detail', html)              # the post detail page was returned
            self.assertIn('Updated Post', html)             # the updated post data is on the page

    def test_delete_post(self):
        """Test the delete post view"""
        with app.test_client() as client:
            resp = client.post(f'/posts/{self.post_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('User Detail', html)              # the user detail page was returned
            self.assertIn('Test Person', html)              # it's the user detail for the test user
            self.assertNotIn('First Post', html)            # the test post is not on the page
