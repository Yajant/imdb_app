import jwt
from imdb_fynd_app.extensions import db
from imdb_fynd_app import settings
from datetime import datetime, date, timedelta
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import event
from sqlalchemy import Column, DateTime, Integer, String, text,Float,Boolean

# --------------
# User
# --------------

# class Role(db.Model, RoleMixin):
#     id = db.Column(db.Integer(), primary_key=True)
#     name = db.Column(db.String(80), unique=True)
#     description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    
    __tablename__='user'

    id = Column(Integer, primary_key=True)
    username = Column(String(20), nullable=False,default='')
    email = Column(String(120), unique=True, nullable=False)
    image_file = Column(String(120), nullable=False, default='default.jpg')
    password = Column(String(255), nullable=False)
    auth_token = Column(String(255))
    is_superuser = Column(Boolean(), default=False)
    is_active = Column(Boolean(), default=True)    
    # roles = db.relationship('Role', secondary=roles_users,
    #                         backref=db.backref('users', lazy='dynamic'))

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)

    def __repr__(self):        
        return "User(%s, %s, %s)" % (self.username, self.email, self.image_file)

    def encode_auth_token(self,user_id):
        """
        Generates the Auth Token
        :return: string
        """        
        try:                            
            exp = datetime.utcnow() + timedelta(days=1)
            
            payload = {
                'exp': exp,                
                'iat': datetime.utcnow(),              
                'sub': user_id
            }
            return jwt.encode(
                payload,                
                getattr(settings, "SECRET_KEY",""),
                algorithm='HS256'
            )
        except Exception as e:            
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: bool, integer|string
        """                    
        try: 
            payload = jwt.decode(auth_token, getattr(settings, "SECRET_KEY", ""),algorithms=['HS256'])                 
            is_blacklisted_token = User.check_blacklist(auth_token)
            if is_blacklisted_token:
                return False,'Token blacklisted. Please log in again.'
            else:
                return True, payload['sub']
        except jwt.ExpiredSignatureError:
            return False,'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return False,'Invalid token. Please log in again.'

    @staticmethod
    def check_blacklist(auth_token):        
        # check whether auth token has been blacklisted                            
        res = User.query.filter_by(auth_token=auth_token).one_or_none()
        #if auth token found in db, that means it is already blacklisted/token already expired        
        if res:
            return True
        else:
            return False

# Add an SQLAlchemy attribute event on User.password and 
# hash the password there if changed. This way, anytime a user password is changed from anywhere, 
# it'll be automatically hashed.
@event.listens_for(User.password, 'set', retval=True)
def hash_user_password(target, value, oldvalue, initiator):
    if value != oldvalue:
        return generate_password_hash(value)
    return value

# --------------
# Movies
# --------------
class Movie(db.Model):
    __tablename__ = 'movie'

    id = Column(Integer, primary_key=True)
    movie_name = Column(String(100))
    director_name = Column(String(50))
    imdb_score = Column(Float)
    popularity = Column(Float,name='99popularity')
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(1), default='A')
    

class Genre(db.Model):
    __tablename__ = 'genre'

    id = Column(Integer, primary_key=True)
    genre_name = Column(String(100))
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(1), name='status', default='A')


class MovieGenre(db.Model):
    __tablename__ = 'movie_genre'

    id = Column(Integer, primary_key=True)
    movie_id = Column(Integer,db.ForeignKey('movie.id'))
    genre_id = Column(Integer,db.ForeignKey('genre.id'))
    created_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_date = Column(DateTime, nullable=False, default=datetime.utcnow)
    status = Column(String(1), default='A')
