import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
# from flask_login import LoginManager, logout_user

from forms import UserAddForm, LoginForm, MessageForm
    # UserAddFormRestricted
from models import db, connect_db, User, Message, authenticateCurrent, Follows, Likes
from seed import seed_database

CURR_USER_KEY = "curr_user"
# TODO: set to False before deploying in production
DEBUG=True
app = Flask(__name__)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view="users.login"

    
# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgres:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)

if DEBUG:
    seed_database()
else:
    db.create_all()

##############################################################################
# User signup/login/logout


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                location=form.location.data,
                bio=form.bio.data,
                header_image_url=form.header_image_url.data or User.header_image_url.default.arg
            )
            db.session.commit()
            
            do_login(user)
            return redirect("/")


        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('users/signup.html', form=form)

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""
    print("called")

    do_logout()
    flash("Logged you out")

    return redirect('/login')

##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    # snagging messages in order from the database;
    # user.messages won't be in order by default
    messages = (Message
                .query
                .filter(Message.user_id == user_id)
                .order_by(Message.timestamp.desc())
                .limit(100)
                .all())
    return render_template('users/show.html', user=user, messages=messages)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
 
    # get the current user
    user = User.query.get_or_404(user_id)
    
    #
    # follows = Follows.query
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get_or_404(follow_id)
    g.user.following.append(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    followed_user = User.query.get(follow_id)
    g.user.following.remove(followed_user)
    db.session.commit()

    return redirect(f"/users/{g.user.id}/following")


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(g.user.id)
    form = UserAddForm(obj=user)
    id = user.id

    if request.method == "POST":
        g.user.password = form.password.data,
        g.user.email = form.email.data,
        g.user.image_url = form.image_url.data or User.image_url.default.arg,
        g.user.location = form.location.data,
        g.user.bio = form.bio.data,
        g.user.header_image_url = form.header_image_url.data or User.header_image_url.default.arg
        entered_password = form.password.data
        
        check_pw = entered_password
        current_password = g.user.password

        authenticateCurrent(check_pw, current_password)

        if True:
            db.session.commit()
            flash('Profile updated', 'success')
            return redirect('/')

        flash('Access unauthorized', "danger")

    return render_template('users/edit.html', form=form, id=id)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    do_logout()

    db.session.delete(g.user)
    db.session.commit()

    return redirect("/signup")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def messages_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def messages_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def messages_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    msg = Message.query.get(message_id)
    db.session.delete(msg)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """
    # SELECT 
    # f.user_being_followed_id, 
    # f.user_following_id, 
    # m.text, 
    # m.timestamp,
    # m.id,
    # m.user_id, 
    # m.image_url,
    # FROM follows f
    # LEFT JOIN messages m
    # ON f.user_being_followed_id = m.user_id
    # WHERE f.user_being_followed_id = 223;


    if g.user:
        #TODO: come back to this after follow button works

        user_follows = (Follows
                        .query
                        .filter_by(user_following_id=g.user.id)
                        .all())
        #TODO: ask mentor - is there a way to do the following in query using sqlalchemy 
        user_follows = [row.user_being_followed_id for row in user_follows]
        
        # same as previous line
        # new_follows_rows = []
        # for row in follow_rows:
        #     new_follows_rows.append(row.user_being_followed_id)
        
        messages = Message.query.all()
        # create message list
        user_follows_message_ids = []
        # check if the user currently is following another user - if false return last 100 messages
        if len(user_follows) > 0:
            for row in messages:
                if row.user_id in user_follows:
                    user_follows_message_ids.append(row.id)
                    
            
            messages = (Message
                        .query
                        .filter(Message.id.in_(user_follows_message_ids))
                        .order_by(Message.timestamp.desc())
                        .limit(100)
                        .all())  
        else:
            # TODO: ask mentor if we should leave this if they haven't followed anyone yet?
            flash('Start following users to create a custom feed')
            messages = (Message
                        .query
                        .order_by(Message.timestamp.desc())
                        .limit(100)
                        .all())
        print()
        return render_template('home.html', messages=messages)

    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

if __name__ == "__main__":
    app.run(debug=DEBUG)
