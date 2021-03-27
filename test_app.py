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
        with app.test_client() as client:
            resp = client.get('/')

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(resp.location, 'http://localhost/users')

    def test_get_users(self):
        with app.test_client() as client:
            resp = client.get('/users')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Users</h1>', html)
            self.assertIn('Test Person', html)

    def test_get_users_new(self):
        with app.test_client() as client:
            resp = client.get('/users/new')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Create A User</h1>', html)

    def test_post_users_new(self):
        data = {'first-name': 'Peter',
                'last-name': 'Parker',
                'image-url': 'http://notaurl.com'}
        with app.test_client() as client:
            resp = client.post('/users/new', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Peter Parker', html)

    def test_get_user_detail(self):
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Test Person', html)

    def test_get_user_edit(self):
        with app.test_client() as client:
            resp = client.get(f'/users/{self.user_id}/edit')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('<h1>Edit User</h1>', html)
            self.assertIn('value="Test"', html)

    def test_post_user_edit(self):
        data = {'first-name': 'Peter',
                'last-name': 'Parker',
                'image-url': 'http://notaurl.com'}
        with app.test_client() as client:
            resp = client.post(f'/users/{self.user_id}/edit', data=data, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Peter Parker', html)

    def test_post_user_delete(self):
        with app.test_client() as client:
            resp = client.post(f'/users/{self.user_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('Test Person', html)