from flask import request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Length
from flask_babel import _, lazy_gettext as _l
from app.models import User


class EditProfileForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)  # passes this call (plus its args) to the parent class
        self.original_username = original_username

    def validate_username(self, username):
        # validate for uniqueness if the username was changed
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user is not None:
                raise ValidationError(_l('Username already in use.  Please select a different username.'))


class PostForm(FlaskForm):
    post = TextAreaField(_l('What\'s on your mind?'), validators=[DataRequired(), Length(min=1, max=140)],
                         render_kw={'autofocus': True})
    submit = SubmitField(_l('Submit'))
