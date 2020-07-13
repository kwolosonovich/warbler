from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, URL


class MessageForm(FlaskForm):
    """Form for adding/editing messages."""

    text = TextAreaField('text', validators=[DataRequired()])


class UserAddForm(FlaskForm):
    """Form for adding users."""

    url_validator = URL(message='Please provide valid URL')
    optional = Optional(strip_whitespace=True)


    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL', validators=[optional, url_validator])
    location = StringField('(Optional) Location', validators=[optional])
    bio = StringField('(Optional) Bio', validators=[optional])
    header_image_url = StringField('(Optional) Heading Image', validators=[optional, url_validator])


class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])


class UserAddFormRestricted(UserAddForm):
    """Used to display user profile info in edit form username as readonly"""
    # username = StringField('Username', validators=[DataRequired()])
    form_widget_args = {
        "username": {
            "readonly": True, 
        }
    }
