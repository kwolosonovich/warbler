# to test use python - m unittest - v test_message_model.py

import os
from app import app
from models import db, Message, User, Follows, Likes
from unittest import TestCase

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""
    def setUp(self):
        """Create test client, add sample data."""
        db.drop_all()
        db.create_all()
        
        user1 = User.signup(email='user1@gmail.com',
                            username='user1',
                            image_url="/static/images/default-pic.png",
                            location='Phoenix',
                            bio="test bio",
                            header_image_url="/static/images/warbler-hero.jpg",
                            password='password1')
        self.id = 1
        # get user from users table using id
        self.user1 = User.query.get(1)
        # add users to session
        db.session.add(user1)
        db.session.commit()
        #assign users to self
        self.user1 = user1
        
        self.client = app.test_client()
                
    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res

    def test_message_model(self):
        """Test message model"""
        
        message1 = Message(
            text="test text",
            user_id=self.id
        )

        db.session.add(message1)
        db.session.commit()

        # User should have 1 message
        self.assertTrue(self.user1.messages)
        # self.assertEqual(self.user1.messages[0].text, "test text")
        
    def test_message_likes(self):
        '''Test likes messages functionality.''' 
        message1 = Message(
            text="test text 1",
            user_id=self.id
        )
        message2 = Message(
            text="test text 2",
            user_id=self.id
        )
        
        user2 = User.signup(email='user2@gmail.com',
                            username='user2',
                            image_url="/static/images/default-pic.png",
                            location='Phoenix',
                            bio="test bio",
                            header_image_url="/static/images/warbler-hero.jpg",
                            password='password2')
        user2.id = 2
        self.id = user2.id
        
        db.session.add_all([message1, message2, user2])
        db.session.commit()
        
        user2.likes.append(message1)
        
        db.session.commit()
        
        likes = Likes.query.all()
        self.assertEqual(len(likes), 1)
        self.assertEqual(likes[0].message_id, message1.user_id)
