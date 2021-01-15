import json, time
import logging
import unittest
from urllib.parse import urlencode
from imdb_fynd_app import app, api
from imdb_fynd_app.extensions import db
from imdb_fynd_app.routes.movies import MoviesAPI
from imdb_fynd_app.models import User, Genre,MovieGenre,Movie
from imdb_fynd_app.routes.auth import RegisterAPI, LoginAPI, LogoutAPI
from imdb_fynd_app.routes.genre import GenreAPI, GenreMovieAPI

log = logging.getLogger(__name__)

class BaseTestCase(unittest.TestCase):
    
    def setUp(self,create_superuser=False):
        # """Define test variables and initialize app."""
        self.client = app.test_client()
        self.app = app        
        self.app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///IMDB_TEST.sqlite3"
        db.init_app(self.app)
            
        # bind app context without Context Manager.
        ctx = self.app.app_context()
        with ctx:
            # create all tables
            db.create_all()
            # after this you can use current_app
            ctx.push()
        
        if create_superuser:   
            new_user = User.query.filter_by(email='bob@mailinator.com').one_or_none()
            if not new_user:              
                super_user = User(username='bob',email='bob@mailinator.com', password='admin', is_superuser=True,is_active=True)  
                db.session.add(super_user)
                db.session.commit()            
            data_login = self.login_user("bob@mailinator.com","admin",200)   
            self.data_login = data_login

    def tearDown(self):            
        """teardown all initialized variables."""        
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
        
    def http_send(self, uri, method, code, request_data=None, headers=None, **kwargs):
        if api.prefix:
            uri = api.prefix+uri

        headers = headers or {}        

        if method == 'HEAD':
            log.info('Head {0}'.format(uri))
            response = self.client.head(uri, headers=headers or {})
        elif method == 'GET':
            uri = uri + '?' + urlencode(request_data or {})
            log.info('Get {0}'.format(uri))
            response = self.client.get(uri, headers=headers or {})
        elif method == 'POST':
            log.info('Post {0}'.format(uri))
            response = self.client.post(uri, data=json.dumps(request_data or {}), content_type='application/json', headers=headers or {})
        elif method == 'PUT':
            log.info('Put {0}'.format(uri))
            response = self.client.put(uri, data=json.dumps(request_data or {}), content_type='application/json', headers=headers or {})
        elif method == 'DELETE':
            log.info('Delete {0}'.format(uri))
            response = self.client.delete(uri, data=json.dumps(request_data or {}), content_type='application/json', headers=headers or {})
        else:
            raise Exception('Unknown HTTP method : {0}'.format(method))

        try:
            self.assertEqual(response._status_code, code)
        except AssertionError as e:
            print(response.data.decode())
            raise e

        return response
    
    def p(self, obj):
        print(json.dumps(obj, indent=2))

    # -------------------------------
    # TEST USER HELPERS
    # -------------------------------
    def register_user(self, email, password,status):
        uri = RegisterAPI.uri

        request_data = {
            "email": email,
            "password": password
        }

        response = self.http_send(
            uri=uri,
            method='POST',
            request_data=request_data,
            code=status
        )
        json_response = json.loads(response.data.decode())
        return json_response

    def login_user(self, email, password,status):
        uri = LoginAPI.uri

        request_data = {
            "email": email,
            "password": password
        }
        
        response = self.http_send(
            uri=uri,
            method='POST',
            request_data=request_data,
            code=status
        )

        json_response = json.loads(response.data.decode())
        return json_response

    def add_movie(self):
        uri = MoviesAPI.uri

        request_data = {
            "popularity": 83.0,
            "director_name": "Victor Fleming",            
            "imdb_score": 8.3,
            "movie_name": "The Wizard of Oz"
        }
        
        response = self.http_send(
            uri=uri,
            method='POST',            
            code=201,
            request_data=request_data,
            headers=dict(
                Authorization='Bearer ' + self.data_login['data']['auth_token']
            )
        )     
        json_response = json.loads(response.data.decode())    
        return json_response 

    def add_genre(self):
        uri = GenreAPI.uri
    
        request_data = {            
            "genre_name": "Adventure"            
        }

        response = self.http_send(
            uri=uri,
            method='POST',            
            code=201,
            request_data=request_data,
            headers=dict(
                Authorization='Bearer ' + self.data_login['data']['auth_token']
            )
        )            
        json_response = json.loads(response.data.decode())    
        return json_response 

    def add_genre_movie(self,movie_name="Chronicles of FYND",director_name="Brijesh",genre_name="Technology"):
        movie = Movie(movie_name=movie_name,director_name=director_name,imdb_score=9.3,popularity =93.0,status='A')
        db.session.add(movie)
        genre = Genre(genre_name=genre_name,status='A')
        db.session.add(genre)
        db.session.commit()
                                
        uri = GenreMovieAPI.uri
    
        request_data = {            
            "genre_id": genre.id,
            "movie_id": movie.id
        }

        response = self.http_send(
            uri=uri,
            method='POST',            
            code=201,
            request_data=request_data,
            headers=dict(
                Authorization='Bearer ' + self.data_login['data']['auth_token']
            )
        )            
        json_response = json.loads(response.data.decode())    
        return json_response 

