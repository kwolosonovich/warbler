"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest -v test_message_views.py


import os
from unittest import TestCase

from models import Follows, db, connect_db, Message, User

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


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        db.drop_all()
        db.create_all()

        self.client = app.test_client()

        self.user1 = User.signup(email='user1@gmail.com',
                                    username='user1',
                                    image_url="/static/images/default-pic.png",
                                    location='Phoenix',
                                    bio="test bio",
                                    header_image_url="/static/images/warbler-hero.jpg",
                                    password='password1')

        self.user1_id = 1
        db.session.commit()

    def test_add_message(self):
        """Test if user can post message."""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            response = c.post("/messages/new", data={"text": "test message"})

            # Make sure it redirects
            self.assertEqual(response.status_code, 302)

            msg = Message.query.one()
            self.assertEqual(msg.text, "test message")


    def test_add_no_session(self):
        '''Test redirect if user is not in session.'''
        with self.client as c:
            response = c.post("/messages/new",
                          data={"text": "test message"}, follow_redirects=True)
            self.assertTrue(response.status_code == 200)

    def test_invalid_user(self):
        '''Test restricted access if user is not in session.'''
        with self.client as c:
            response = c.post('/messages/new', data={'text': "test message"}, follow_redirects=True)
            self.assertTrue(response.status_code == 200)
            self.assertIn("Access unauthorized", str(response.data))



        # ********************* Does't work *********************

    def test_message_show(self):

        m = Message(
            id=11,
            text="test message",
            user_id=self.user1_id
        )
        
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id
            
            m = Message.query.get(11)

            response = c.get(f'/messages/{m.id}')

            self.assertTrue(response.status_code == 200)
            self.assertIn(m.text, str(response.data))

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_invalid_message_show(self):
        print(self.user1)
        with self.client as c:
            with c.session_transaction() as sess:
                # print(sess.keys())
                sess[CURR_USER_KEY] = self.user1.id
            
            response = c.get('/messages/9')

            self.assertEqual(response.status_code == 404)

    def test_message_delete(self):
        '''Test delete message'''
        m = Message(
            id=11,
            text="test message",
            user_id=self.user1_id
        )
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1.id

            response = c.post("/messages/11/delete", follow_redirects=True)
            self.assertTrue(response.status_code == 200)

            m = Message.query.get(11)
            self.assertIsNone(m)

    def test_unauthorized_message_delete(self):
        '''Test restricted access to message if unauthorized.'''
        user2 = User.signup(email='user2@gmail.com',
                            username='user2',
                            image_url="/static/images/default-pic.png",
                            location='Phoenix',
                            bio="test bio",
                            header_image_url="/static/images/warbler-hero.jpg",
                            password='password2')
        user2.id = 2

        #Message is owned by user1
        m = Message(
            id=11,
            text="test message",
            user_id=self.user1_id
        )
        db.session.add_all([user2, m])
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = 76543

            response = c.post("/messages/11/delete", follow_redirects=True)
            self.assertTrue(response.status_code == 200)
            self.assertIn("Access unauthorized", str(response.data))

            m = Message.query.get(11)
            self.assertIsNotNone(m)

    def test_message_delete_no_authentication(self):
        '''Test restricted access to delete message if unauthorized.'''
        m = Message(
            id=11,
            text="test message",
            user_id=self.user1_id
        )
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            response = c.post("/messages/11/delete", follow_redirects=True)
            self.assertTrue(response.status_code == 200)
            self.assertIn("Access unauthorized", str(response.data))

            m = Message.query.get(11)
            self.assertIsNotNone(m) 
