"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows
from bs4 import BeautifulSoup

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.testuser = User.signup(username="testuser", email="test@email.com", password="testuser", image_url=None)
        self.testuser_id = 8989
        self.testuser.id = self.testuser_id

        self.u1 = User.signup("testuser1", "test1@test.com", "password", None)
        self.u1_id = 778
        self.u1.id = self.u1_id

        self.u2 = User.signup("testuser2", "test2@test.com", "password", None)
        self.u2_id = 884
        self.u2.id = self.u2_id

        self.u3 = User.signup("huulamnguyen", "test3@test.com", "password", None)
        self.u4 = User.signup("liamnguyen", "test4@test.com", "password", None)

        db.session.commit()

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_index(self):
        with self.client as c:
            resp = c.get("/users")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))
            self.assertIn("@huulamnguyen", str(resp.data))
            self.assertIn("@liamnguyen", str(resp.data))
    
    def test_user_search(self):
        with self.client as c:
            resp = c.get('/users?q=test')

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@testuser", str(resp.data))
            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))

            self.assertNotIn("@huulamnguyen", str(resp.data))
            self.assertNotIn("@liamnguyen", str(resp.data))
    
    def test_user_show(self):
        with self.client as c:
            resp = c.get(f'/users/{self.testuser_id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", str(resp.data))
        
        with self.client as c:
            resp = c.get(f'/users/{self.u1_id}')
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser1", str(resp.data))

    def setup_like(self):
        m1 = Message(text="Trending warble", user_id=self.testuser_id)
        m2 = Message(text="Moving to NYC", user_id=self.testuser_id)
        m3 = Message(id=123, text="I want Alex", user_id=self.u1_id)

        db.session.add_all([m1, m2, m3])
        db.session.commit()

        # testuser likes u1's message
        l1 = Likes(user_id=self.testuser_id, message_id=m3.id)

        db.session.add(l1)
        db.session.commit()
    
    def test_user_show_with_likes(self):
        with self.client as c:
            resp = c.get(f'/users/{self.testuser_id}')

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class":"stat"})

            self.assertEqual(len(found), 4)
            









