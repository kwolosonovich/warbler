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

        u1 = User.signup(
            email="test1@test.com",
            username="testuser1",
            password="HASHED_PASSWORD",
            location="Phoenix",
            bio="Bio text",
            image_url="https://image.flaticon.com/icons/svg/44/44901.svg",
            header_image_url="https://image.flaticon.com/icons/svg/899/899718.svg"
        )
        u1.id = 1
        u1.password = 'pw1'

        u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",
            location="Phoenix",
            bio="Bio text",
            image_url="https://image.flaticon.com/icons/svg/44/44901.svg",
            header_image_url="https://image.flaticon.com/icons/svg/899/899718.svg"
        )
        u2.id = 2
        u2.password = 'pw2'

        # get users from users table using id
        u1 = User.query.get(1)
        u2 = User.query.get(2)
        # add users to session
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        #assign users to self
        self.u1 = u1
        self.u2 = u2

        self.client = app.test_client()

    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res
    
    def test_user_follow(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertEqual(len(self.u2.following), 0)
        self.assertEqual(len(self.u2.followers), 1)
        self.assertEqual(len(self.u1.followers), 0)
        self.assertEqual(len(self.u1.following), 1)

        self.assertEqual(self.u2.followers[0].id, self.u1.id)
        self.assertEqual(self.u1.following[0].id, self.u2.id)
        
    def test_is_following(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u1.is_following(self.u2))
        self.assertFalse(self.u2.is_following(self.u1))

    def test_is_followed_by(self):
        self.u1.following.append(self.u2)
        db.session.commit()

        self.assertTrue(self.u2.is_followed_by(self.u1))
        self.assertFalse(self.u1.is_followed_by(self.u2))

    # def test_valid_authentication(self):

    #     u = User.authenticate(self.u1.username, 'pw1')
    #     self.assertIsNotNone(u)
    #     self.assertEqual(u.id, self.uid1)

    # def test_invalid_username(self):
    #     self.assertFalse(User.authenticate("different_name", "same_testpw"))

    # def test_wrong_password(self):
    #     self.assertFalse(User.authenticate(self.u1.username, "badpassword"))


















        # u1.password = "test"
        # hashed_pwd = bcrypt.generate_password_hash(u1_password).decode('UTF-8')


    #     User(
    #         email=email,
    #         username=username,
    #         password=password,
    #         location=location,
    #         bio=bio,
    #         image_url=image_url,
    #         header_image_url=header_image_url
    #     )

    #     email = "test@test.com",
    #     user1.username = "testuser",
    #     user1.password = "HASHED_PASSWORD",
    #     user1.location = "Phoenix",
    #     user1.bio = "Bio text",
    #     user1.image_url = "https://image.flaticon.com/icons/svg/44/44901.svg",
    #     user1.header_image_url = "https://image.flaticon.com/icons/svg/899/899718.svg"

    #     user2 = User(
    #         email="test2@test.com",
    #         username="testuser2",
    #         password=hashed_pwd,
    #         location="Phoenix",
    #         bio="Bio text",
    #         image_url="https://image.flaticon.com/icons/svg/44/44901.svg",
    #         header_image_url="https://image.flaticon.com/icons/svg/899/899718.svg"
    #     )

    #     db.session.add(user2)
    #     db.session.commit()
    #     self.assertEqual(len(user2.messages), 0)
    #     self.assertEqual(len(user.messages), 0)



    # test following functions 

    # def test_is_following(self):
    #     # add second user to database
    #     u1 = User.signup('user1', 'test1@gmail.com', 'user1pw')
    #     u2 = User.signup('user2', 'test2@gmail.com', 'user2pw')
    #     db.session.add(u1)
    #     db.session.add(u2)
    #     db.session.commit()
    #     # add user as a follower of u2
    #     self.u1.following.append(self.u2)
    #     db.session.commit()

    #     user.query.get(u1)
    #     user.query.get(u2)

    #     self.u1 = u1
    #     self.u2 = u2

    #     self.assertTrue(self.u1.is_following(self.u2))
        # self.assertEqual(len(u2.followers), 1)


    # def test_is_following(self):

    # def test_signup(self):

    # def test_authenticate(self):

