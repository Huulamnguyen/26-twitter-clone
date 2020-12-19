"""Message model tests."""

# run these tests like:
#
#    python -m unittest test_message_model.py


from app import app
import os
from unittest import TestCase
from sqlalchemy import exc

from models import db, User, Message, Follows, Likes

# BEFORE IMPORT APP. Set up an environmental varible to use different database to test
os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# IMPORT APP

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class MessageModelTestCase(TestCase):
    """ Test Message Model """

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.uid = 123456789
        user = User.signup("testuser", "test@email.com", "password", None)
        user.id = self.uid

        db.session.commit()

        self.user = User.query.get(self.uid)

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """ Test basic model works """
        m1 = Message(text="Testing Message 1", user_id=self.uid)
        m2 = Message(text="Testing Message 2", user_id=self.uid)
        db.session.add_all([m1, m2])
        db.session.commit()

        # User should have 1 message
        self.assertEqual(len(self.user.messages), 2)
        self.assertEqual(self.user.messages[0].text, "Testing Message 1")
        self.assertEqual(self.user.messages[1].text, "Testing Message 2")

    def test_message_likes(self):
        m1 = Message(text="Testing Message 1", user_id=self.uid)
        m2 = Message(text="Testing Message 2", user_id=self.uid)

        db.session.add_all([m1, m2])
        db.session.commit()

        self.user.likes.append(m1)
        db.session.commit()

        like = Likes.query.filter(Likes.user_id == self.uid).all()
        self.assertEqual(len(like), 1)
        self.assertEqual(like[0].message_id, m1.id)
