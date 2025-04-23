from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', 
                          validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', 
                            validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                    validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email',
                       validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class PostReactionForm(FlaskForm):
    post_url = StringField('Post URL', validators=[DataRequired()])
    reaction_type = SelectField('Reaction Type', 
                              choices=[
                                  ('LIKE', 'Like'),
                                  ('LOVE', 'Love'),
                                  ('HAHA', 'Haha'),
                                  ('WOW', 'Wow'),
                                  ('SAD', 'Sad'),
                                  ('ANGRY', 'Angry')
                              ],
                              validators=[DataRequired()])
    count = IntegerField('Number of Reactions', 
                        validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField('Start Reactions')

class CommentReactionForm(FlaskForm):
    comment_url = StringField('Comment URL', validators=[DataRequired()])
    reaction_type = SelectField('Reaction Type', 
                              choices=[
                                  ('LIKE', 'Like'),
                                  ('LOVE', 'Love'),
                                  ('HAHA', 'Haha'),
                                  ('WOW', 'Wow'),
                                  ('SAD', 'Sad'),
                                  ('ANGRY', 'Angry')
                              ],
                              validators=[DataRequired()])
    count = IntegerField('Number of Reactions', 
                        validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField('Start Reactions')

class TokenForm(FlaskForm):
    token = StringField('Facebook Access Token', validators=[DataRequired(), Length(max=512)])
    submit = SubmitField('Add Token')
