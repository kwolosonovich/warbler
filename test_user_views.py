# test by using: python - m unittest - v test_message_views.py

from app import app, CURR_USER_KEY
import os
from unittest import TestCase

from models import db, connect_db, Message, User, Likes, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

db.create_all()

app.config['WTF_CSRF_ENABLED'] = False


class user1Views(TestCase):

    def setUp(self):

        db.drop_all()
        db.create_all()

        self.client = app.test_client()
        #test user 1
        self.user1 = User.signup(email = 'user1@gmail.com',
                                    username = 'user1',
                                    image_url="/static/images/default-pic.png",
                                    location='Phoenix',
                                    bio = "test bio",
                                    header_image_url = "/static/images/warbler-hero.jpg",
                                    password = 'password1')

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
        # test user 3
        self.user3 = User.signup(email='user3@gmail.com',
                                 username='user3',
                                 image_url="/static/images/default-pic.png",
                                 location='Phoenix',
                                 bio="test bio",
                                 header_image_url="/static/images/warbler-hero.jpg",
                                 password='password3')
        self.user3_id = 3
        self.user3.id = self.user3_id
        
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

    def tearDown(self):
        resp = super().tearDown()
        db.session.rollback()
        return resp

    def test_users_index(self):
        '''Test if user name is included in index.'''
        with self.client as c:
            resp = c.get("/users")

            self.assertIn("@user1", str(resp.data))
            self.assertIn("@user2", str(resp.data))
            self.assertIn("@user3", str(resp.data))
            self.assertTrue(resp.status_code == 200)

    def test_users_search(self):
        '''Test search filter.'''

        with self.client as c:
            resp = c.get("/users?q=user1")

            self.assertIn("@user1", str(resp.data)) 
            self.assertNotIn("@user2", str(resp.data))
            self.assertNotIn("@user3", str(resp.data))
            self.assertEqual(resp.status_code, 302)

    def test_user_show(self):
        '''Test if search is included in rendered content.'''
        with self.client as c:
            resp = c.get(f"/users/{self.user1.id}")

            self.assertIn("1", str(resp.data))

    def setup_likes(self):
        '''Add like to message.'''
        message1 = Message(text="test message1", user_id=self.user1_id)
        message2 = Message(text="test message2", user_id=self.user1_id)
        message3 = Message(id=8, text="test message3", user_id=self.user1_id)
        db.session.add_all([message1, message2, message3])
        db.session.commit()

        like = Likes(user_id=self.user1_id, message_id=8)

        db.session.add(like)
        db.session.commit()

    def test_user_show_with_likes(self):
        '''Test if likes are rendered.'''
        self.setup_likes()

        with self.client as c:
            resp = c.get(f"/users/{self.user1_id}")

            self.assertEqual(resp.status_code, 302)

            self.assertIn("@user1", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 2 messages
            self.assertIn("2", found[0].text)

            # Test for a count of 0 followers
            self.assertIn("0", found[1].text)

            # Test for a count of 0 following
            self.assertIn("0", found[2].text)

            # Test for a count of 1 like
            self.assertIn("1", found[3].text)

    def test_add_like(self):
        '''Test add like to message.'''
        m = Message(id=4, text="test add like", user_id=self.user1_id)
        db.session.add(m)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1_id

            resp = c.post("/messages/4/like", follow_redirects=True)
            self.assertTrue(resp.status_code == 200)


            likes = Likes.query.filter(Likes.message_id == 4).all()
            self.assertEqual(len(likes), 1)
            self.assertEqual(likes[0].user_id, self.user1_id)

    def test_remove_like(self):
        '''Test remove like from message.'''
        self.setup_likes()

        m = Message.query.filter(Message.text == "test message").one()
        self.assertIsNotNone(message)
        self.assertNotEqual(message.user_id, self.user1_id)

        l = Likes.query.filter(
            Likes.user_id == self.user1_id and Likes.message_id == message.id
        ).one()

        # Now we are sure that user1 likes the message "test message"
        self.assertIsNotNone(l)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.test1_id

            resp = c.post(f"/messages/{message.id}/like", follow_redirects=True)
            self.assertTrue(resp.status_code == 200)

            likes = Likes.query.filter(Likes.message_id == messsage.id).all()
            # the like has been deleted
            self.assertEqual(len(likes), 0)

    def test_unauthenticated_like(self):
        '''Restrict access if unauthorized user'''
        self.setup_likes()

        m = Message.query.filter(Message.text == "likable warble").one()
        self.assertIsNotNone(message)

        like_count = Likes.query.count()

        with self.client as c:
            resp = c.post(f"/messages/{message.id}/like", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)

            self.assertIn("Access unauthorized", str(resp.data))

            # The number of likes has not changed since making the request
            self.assertEqual(like_count, Likes.query.count())

    def setup_followers(self):
        '''Set up users follow other users.'''
        f1 = Follows(user_being_followed_id=self.user1_id,
                     user_following_id=self.user1_id)
        f2 = Follows(user_being_followed_id=self.u2_id,
                     user_following_id=self.user1_id)
        f3 = Follows(user_being_followed_id=self.user1_id,
                     user_following_id=self.user_id)

        db.session.add_all([f1, f2, f3])
        db.session.commit()

    def test_user_show_with_follows(self):
        '''Test if followed users are shown'''
        self.setup_followers()

        with self.client as c:
            resp = c.get(f"/users/{self.user1_id}")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@user1", str(resp.data))
            soup = BeautifulSoup(str(resp.data), 'html.parser')
            found = soup.find_all("li", {"class": "stat"})
            self.assertEqual(len(found), 4)

            # test for a count of 0 messages
            self.assertIn("0", found[0].text)

            # Test for a count of 2 following
            self.assertIn("2", found[1].text)

            # Test for a count of 1 follower
            self.assertIn("1", found[2].text)

            # Test for a count of 0 likes
            self.assertIn("0", found[3].text)

    def test_show_following(self):
        '''Test the users followed'''
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1_id

            resp = c.get(f"/users/{self.user1_id}/following")
            self.assertTrue(resp.status_code == 200)
            self.assertIn("user2", str(resp.data))
            self.assertIn("user3", str(resp.data))

    def test_show_followers(self):
        '''Test if users who are following current user are shown.'''
        self.setup_followers()
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user1_id

            resp = c.get(f"/users/{self.user1_id}/followers")

            self.assertIn("user2", str(resp.data))
            self.assertNotIn("user3", str(resp.data))
 
    def test_unauthorized_following_page_access(self):
        '''Test restrict access to following page if unauthorization.'''
        self.setup_followers()
        with self.client as c:

            resp = c.get(
                f"/users/{self.user1_id}/following", follow_redirects=True)
            self.assertTrue(resp.status_code == 200)
            self.assertNotIn("@user2", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))

    def test_unauthorized_followers_page_access(self):
        '''Test restrict access to follower page if unauthorization.'''
        self.setup_followers()
        with self.client as c:

            resp = c.get("/users/1/followers", follow_redirects=True)
            self.assertTrue(resp.status_code == 200)
            self.assertNotIn("@user2", str(resp.data))
            self.assertIn("Access unauthorized", str(resp.data))
