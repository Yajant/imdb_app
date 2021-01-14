import os, sys
from random import randint 
from os import urandom
from PIL import Image
from flask import Blueprint, render_template, request, redirect, url_for, jsonify, make_response, flash, session
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash
import logging
from imdb_fynd_app import app
from imdb_fynd_app.extensions import db
from imdb_fynd_app.models import User
from imdb_fynd_app.routes.movies import search_results
from imdb_fynd_app.core.imdb_decorator import token_required , is_superuser
from imdb_fynd_app.core.views import BaseView
from imdb_fynd_app.core.http import request_data, parse_args
from imdb_fynd_app.forms import RegistrationForm,LoginForm,UpdateAccountForm, MovieSearchForm
from helpers import create_response_format, print_exception, isValidEmail
from flask.views import MethodView

logger = logging.getLogger(__name__)

@app.route("/", methods=['GET', 'POST'])
@app.route("/home", methods=['GET', 'POST'])
def home():
    search = MovieSearchForm(request.form)
    if request.method == 'POST':
        return search_results(search)

    return render_template('home.html', description='IMDB App',title='Fynd', form=search)

@app.route("/about")
def about():    
    return render_template('about.html')

@app.route("/register_enduser", methods=['GET', 'POST'])
def register_enduser():    
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()           

    if form.validate_on_submit():         
        user = User(username=form.username.data, email=form.email.data, password=form.password.data,is_active=True)    
        db.session.add(user)
        db.session.commit()
        flash('Registered Successfully', 'success')
        return redirect(url_for('home'))                      
        
    return render_template('register.html', title='Register', form=form)

@app.route("/login_enduser", methods=['GET','POST'])
def login_enduser(): #url_for takes func name
    if current_user.is_authenticated:
        return redirect(url_for('account'))
    
    form = LoginForm()

    if form.validate_on_submit():                    
        user = User.query.filter_by(email=form.email.data).first()                
        
        if user and user.check_password(form.password.data):             
            login_user(user, remember=form.remember.data)                                    
            next_page = request.args.get('next')
            session["user_id"] = user.id
            print(session," ----")
            return redirect(next_page) if next_page else redirect(url_for('account'))                
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
     
    return render_template('login.html', title='Login', form=form)
    
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture):    
    random_hex = urandom(8).hex() 
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext    
    picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)

    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)  
   
    return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    try:
        form = UpdateAccountForm()
        if form.validate_on_submit():
            if form.picture.data:
                picture_file = save_picture(form.picture.data)
                current_user.image_file = picture_file
            current_user.username = form.username.data
            current_user.email = form.email.data
            db.session.commit()
            flash('Your account has been updated!', 'success')
            return redirect(url_for('account'))
        elif request.method == 'GET':
            form.username.data = current_user.username
            form.email.data = current_user.email
        image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
        return render_template('account.html', title='Account',
                               image_file=image_file, form=form)
    except Exception as e:
        print_exception(e)

class RegisterAPI(BaseView): 

    uri = '/user/register'
    endpoint = 'register' #name url_for will search for

    def post(self):
        try:     
            # get the post data
            data = parse_args(
                (
                    ('email', str, True),
                    ('password', str, True)
                ),
                request_data()
            )
                                
            email = data.get('email')            
            password = data.get('password')

            is_Valid_Email = isValidEmail(email)
            if not is_Valid_Email:
                return create_response_format(msg="""Please enter a valid email. Valid e-mail can contain only contain latin letters, numbers, '@' and '.'. """)
                
            if not email:
                return create_response_format(msg='email_IS_MANDOTRY')
            if not password:
                return create_response_format(msg='password_IS_MANDOTRY')
            else:
                #check length for password
                pass_length = len(password)
                if pass_length < 3 or pass_length > 20:
                    return create_response_format(msg='PASSWORD_SHOULD_BE_BETWEEN_LENGTH_3_TO_20')
            
            new_user = User.query.filter_by(email=email).one_or_none()
            if new_user is None:                                
                new_user = User(email=email.lower(), password=password,is_active=True)
            else:
                return create_response_format(msg='USERNAME_ALREADY_EXISTS',status=409)
            db.session.add(new_user)
            db.session.commit()

            ## generate the auth token
            auth_token = new_user.encode_auth_token(new_user.id)                
            logger.info(str(auth_token))
                        
            data = {'auth_token': auth_token}
                        
            return create_response_format(msg='User Registed Successfully',data=data,is_valid=True,status=201)            

        except Exception as e:
            print_exception(e)
            return create_response_format(msg='SOMETHING_WENT_WRONG_IN_REGISTERING_USER')

class LoginAPI(BaseView): 

    uri = '/user/login'
    endpoint = 'login' 
        
    def post(self):
        try:
            data = parse_args(
                (
                    ('email', str, True),
                    ('password', str, True)
                ),
                request_data()
            )
                    
            email = data.get('email')            
            password = data.get('password')

            if not email:
                return create_response_format(msg='email_IS_MANDOTRY')
            if not password:
                return create_response_format(msg='password_IS_MANDOTRY')

            # check that email exits or not
            user = User.query.filter_by(email=email).one_or_none()
            if not user:                
                return create_response_format(msg="No user found!", status=404)
           
            #authenticate password            
            if user and user.check_password(password):
                auth_token = user.encode_auth_token(user.id)
                print(auth_token, " - auth_token")
                if auth_token:                                                                            
                    # data = {'auth_token': auth_token.decode()}
                    data = {'auth_token': auth_token}
                    logger.info("Successfully logged in -'{0}'".format(user.email))

                    print("\n---------------------------------------------------------------------------\n")
                    print("\nLogged in user: '{0}'".format(user.email))
                    print("\n---------------------------------------------------------------------------\n")

                    return create_response_format(msg='Successfully logged in',data=data, status=200, is_valid=True)     
            else:                
                return create_response_format(msg='Login Unsuccessful. Please check email and password.', status=401)     

        except Exception as e:
            print_exception(e)
            return create_response_format(msg='SOMETHING_WENT_WRONG_IN_LOGGING_USER')

class LogoutAPI(BaseView): 

    uri = '/user/logout'
    endpoint = 'logout' 

    @token_required
    def post(self):   
        current_user = self.current_user                      
        auth_header = request.headers.get('Authorization')

        if auth_header:
            auth_token = auth_header.split(" ")[1]
        else:
            auth_token = ''

        if auth_token and current_user.id:                                        
            try:                
                # insert the token                
                current_user.auth_token = auth_token
                db.session.commit()
                                
                logger.info("Successfully logged out. -'{0}'".format(current_user.email))
                return create_response_format(msg='Successfully logged out.', status=200,is_valid=True)                
            except Exception as e:
                logger.error(e)
                return create_response_format(exception=True,status=200)            
        else:                    
            return create_response_format(msg='Provide a valid auth token.',status=403)        
