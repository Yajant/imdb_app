from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField,TextField , TextAreaField, DateField,SelectField, FloatField, IntegerField, DecimalField 
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, URL, NumberRange
from imdb_fynd_app.models import User
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
import decimal
from decimal import ROUND_HALF_UP
from wtforms import DecimalField
from imdb_fynd_app.tag_list_field import TagListField


class BetterDecimalField(DecimalField):
    """
    Very similar to WTForms DecimalField, except with the option of rounding
    the data always.
    """
    def __init__(self, label=None, validators=None, places=2, rounding=None,
                 round_always=False, **kwargs):
        super(BetterDecimalField, self).__init__(
            label=label, validators=validators, places=places, rounding=
            rounding, **kwargs)
        self.round_always = round_always

    def process_formdata(self, valuelist):
        if valuelist:
            try:
                self.data = decimal.Decimal(valuelist[0])
                if self.round_always and hasattr(self.data, 'quantize'):
                    exp = decimal.Decimal('.1') ** self.places
                    if self.rounding is None:
                        quantized = self.data.quantize(exp)
                    else:
                        quantized = self.data.quantize(
                            exp, rounding=self.rounding)
                    self.data = quantized
            except (decimal.InvalidOperation, ValueError):
                self.data = None
                raise ValueError(self.gettext('Not a valid decimal value'))

# from flask.ext.wtf import Form

class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=3, max=20)])    
    submit = SubmitField('Sign Up', id="RegistrationFormSubmit")

    '''custom validators: validates if user name already exits.'''
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    # '''custom validators: validates if email already exits.'''
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login',id="LoginFormSubmit")

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)],id="updateusername")
    email = StringField('Email',
                        validators=[DataRequired(), Email()],id="updateemail")
    picture = FileField('Update Profile Picture', validators=[FileAllowed(['jpg', 'png','jpeg'])],id="updatepicture")
    submit = SubmitField('Update',id="UpdateAccountFormSubmit")

    def validate_username(self, username):
        #Raise error only when username differs while updating the name, 
        # i.e don't raise error if user don't update the name

        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class MovieForm(FlaskForm):    
    movie_name = StringField('Movie',validators=[DataRequired(),])
    director_name = StringField('Director Name',validators=[DataRequired(),])    
    imdb_score = BetterDecimalField('Imdb Score',validators=[DataRequired(),NumberRange(1, 10)],round_always=True)    
    popularity = BetterDecimalField('Popularity',validators=[DataRequired(),NumberRange(1, 99)],round_always=True)        
    genre = TagListField(
        "Tags",
        separator=",",
        validators=[Length(max=8, message="You can only use up to 8 tags.")]
    )
    submit = SubmitField('Submit',id="SubmitMovie")

class MovieSearchForm(FlaskForm):
    choices = [('movie_name', 'Movie Name'),
               ('director_name', 'Director Name'),
               ('popularity', 'Popularity'),
               ('imdb_score', 'IMDB Score')]
    # select = SelectField('Search for movie', choices=choices)
    select = SelectField(choices=choices)
    search = StringField('')

