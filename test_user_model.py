"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"


# Now we can import app
from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test User Model"""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        user1 = User.signup("test1", "email1@gmail.com", "password", None)
        uid1 = 1111
        user1.id = uid1

        user2 = User.signup("test2", "email2@gmail.com", "password", None)
        uid2 = 2222
        user2.id = uid2

        db.session.commit()

        user1 = User.query.get(uid1)
        user2 = User.query.get(uid2)

        self.user1 = user1
        self.uid1 = uid1

        self.user2 = user2
        self.uid2 = uid2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(
            u.__repr__(), f"<User #{u.id}: testuser, test@test.com>")

    # TODO: FOLLOWERS AND FOLLOWING TEST
    def test_user_follows(self):
        # * user1 following user2
        self.user1.following.append(self.user2)
        db.session.commit()

        # * len of user1 following should be 1
        self.assertEqual(len(self.user1.following), 1)
        # * len of user2 following should be 0
        self.assertEqual(len(self.user2.following), 0)

        # * len of user2 follower should be 1
        self.assertEqual(len(self.user2.followers), 1)
        # * len of user1 follower should be 0
        self.assertEqual(len(self.user1.followers), 0)

        self.assertEqual(self.user2.followers[0].id, self.user1.id)
        self.assertEqual(self.user1.following[0].id, self.user2.id)

    def test_is_following(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    # TODO: SIGN UP TEST
    def test_valid_signup(self):
        """test user1 and user2 signed up"""
        self.assertIsNotNone(self.user1)
        self.assertEqual(self.user1.username, "test1")
        self.assertEqual(self.user1.email, "email1@gmail.com")
        self.assertNotEquals(self.user1.password, "password")
        self.assertTrue(self.user1.password.startswith("$2b$"))

        self.assertIsNotNone(self.user2)
        self.assertEqual(self.user2.username, "test2")
        self.assertEqual(self.user2.email, "email2@gmail.com")
        self.assertNotEquals(self.user2.password, "password")
        self.assertTrue(self.user2.password.startswith("$2b$"))

    def test_invalid_username_signup(self):
        invalid_user = User.signup(None, "test@email.com", "password", None)
        uid = 123456789
        invalid_user.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_email_signup(self):
        invalid_user = User.signup("test_username", None, "password", None)
        uid = 123456
        invalid_user.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    def test_invalid_password_signup(self):
        with self.assertRaises(ValueError) as context:
            User.signup("test_username", "test@email.com", "", None)

        with self.assertRaises(ValueError) as context:
            User.signup("test_username", "test@email.com", None, None)

    # TODO: AUTHENTICATION TEST
    def test_valid_authentication(self):
        u = User.authenticate(self.user1.username, "password")
        self.assertIsNotNone(u)
        self.assertEqual(self.user1.id, u.id)
        self.assertEqual(self.user1.username, "test1")

    def test_invalid_username_auth(self):
        self.assertFalse(User.authenticate("invalidusername", "password"))

    def test_invalid_password_auth(self):
        self.assertFalse(User.authenticate(
            self.user1.username, "wrongpassword"))
