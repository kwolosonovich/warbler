"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows
from flask_bcrypt import Bcrypt, check_password_hash, generate_password_hash

bcrypt = Bcrypt()

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
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        self.client = app.test_client()

#test user 1
        self.user1 = User.signup(email='user1@gmail.com',
                                 username='user1',
                                 image_url="/static/images/default-pic.png",
                                 location='Phoenix',
                                 bio="test bio",
                                 header_image_url="/static/images/warbler-hero.jpg",
                                 password='password1')

        self.user1_id = 1,
        self.user1.id = self.user1_id
        # test user 2
        self.user2 = User.signup(email='user2@gmail.com',
                                 username='user2',
                                 image_url="/static/images/default-pic.png",
                                 location='Phoenix',
                                 bio="test bio",
                                 header_image_url="/static/images/warbler-hero.jpg",
                                 password='password2')
        self.user2_id = 2
        self.user2.id = self.user2_id

        # get users from users table using id
        user1 = User.query.get(1)
        user2 = User.query.get(2)
        # add users to session
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        #assign users to self
        self.user1 = user1
        self.user2 = user2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_follow(self):
        '''Test users following eachother.'''
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertEqual(len(self.user2.following), 0)
        self.assertEqual(len(self.user2.followers), 1)
        self.assertEqual(len(self.user1.followers), 0)
        self.assertEqual(len(self.user1.following), 1)

        self.assertEqual(self.user2.followers[0].id, self.user1.id)
        self.assertEqual(self.user1.following[0].id, self.user2.id)
        
    def test_is_following(self):
        '''Test user following another user'''
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user1.is_following(self.user2))
        self.assertFalse(self.user2.is_following(self.user1))

    def test_is_followed_by(self):
        '''Test user being followed by another user'''
        self.user1.following.append(self.user2)
        db.session.commit()

        self.assertTrue(self.user2.is_followed_by(self.user1))
        self.assertFalse(self.user1.is_followed_by(self.user2))

    def test_valid_authentication(self):
        '''Test valid password authorization'''
        u = User.authenticate(self.user1.username, 'pw1')
        self.assertIsNotNone(u)
        self.assertEqual(u.id, self.uid1)

    def test_invalid_username(self):
        '''Test invalid username with password'''
        self.assertFalse(User.authenticate(
            self.user1.username, "test"))

    def test_wrong_password(self):
        '''Test wrong password'''
        self.assertFalse(User.authenticate(
            self.user1.username, "badpassword"))



 


