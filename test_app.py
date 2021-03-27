from unittest import TestCase
from app import app
from models import User, db

app.config['TESTING'] = True
app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly_test'
app.config['SQLALCHEMY_ECHO'] = False

db.drop_all()
db.create_all()


class AppTests(TestCase):

    def setUp(self):
        """Add a test user"""

        User.query.delete()

        user = User(first_name='Test', last_name='Person', image_url='https://picsum.photos/200/300')
        db.session.add(user)
        db.session.commit()

        self.user_id = user.id

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
        """Thest the add new user view"""
        data = {'first-name': 'Peter',
                'last-name': 'Parker',
                'image-url': 'http://notaurl.com'}
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
