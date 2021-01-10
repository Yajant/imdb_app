import json, time
from imdb_fynd_app.core.tests import BaseTestCase
from imdb_fynd_app.models import User
from imdb_fynd_app.routes.auth import RegisterAPI, LoginAPI, LogoutAPI
from imdb_fynd_app.extensions import db
from imdb_fynd_app.models import User, Genre,MovieGenre,Movie
from imdb_fynd_app.routes.movies import MoviesAPI
from imdb_fynd_app.routes.genre import GenreAPI, GenreMovieAPI

# -------------------------------
# TEST USER
# To run the test enter this command in your terminal.
# python -m unittest /home/yajant/Downloads/imdb_fynd_app/imdb_fynd_app/tests/test_genre.py
# -------------------------------
class TestGenre(BaseTestCase):   

    def setUp(self):
        super().setUp(create_superuser=True)

    def test_view_post(self):                    
        json_response= self.add_genre()
            
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Genre Inserted Successfully", json_response['message']) 
        
    def test_view_get(self):        
        # Given
        uri = GenreAPI.uri

        json_response= self.add_genre()            
        self.assertTrue(True, type(json_response['is_valid']))     
        
        response = self.http_send(
            uri=uri,
            method='GET',            
            code=200,
            headers=dict(
                Authorization='Bearer ' + self.data_login['data']['auth_token']
            )
        )
        json_response = json.loads(response.data.decode())  
        
        print(json_response," - json_response")                        
        # Then
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Genre List", json_response['message']) 

    def test_view_put(self): 
        time.sleep(1)               
        uri = GenreAPI.uri  

        json_response = self.add_genre()

        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertTrue(json_response['data']['genre_id'])        
              
        request_data = {            
            "genre_name": "Family",
            "genre_id": int(json_response['data']['genre_id'])
        }
                
        response = self.http_send(
            uri=uri,
            method='PUT',            
            code=200,
            request_data=request_data,
            headers=dict(
                Authorization='Bearer ' + self.data_login['data']['auth_token']
            )
        )
        
        # When
        json_response = json.loads(response.data.decode())      
        
        # Then
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Genre Updated Successfully", json_response['message'])         
        self.assertEqual("Family", request_data['genre_name'])  
    
    def test_view_delete(self): 
        time.sleep(1)               
        uri = GenreAPI.uri  

        json_response = self.add_genre()

        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertTrue(json_response['data']['genre_id'])        
              
        request_data = {            
            "genre_id": int(json_response['data']['genre_id'])
        }

        print(request_data, " - request_data")
                
        response = self.http_send(
            uri=uri,
            method='DELETE',            
            code=200,
            request_data=request_data,
            headers=dict(
                Authorization='Bearer ' + self.data_login['data']['auth_token']
            )
        )
        
        # When
        json_response = json.loads(response.data.decode())      
                
        # Then
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Genre Deleted Successfully", json_response['message'])   

class TestGenreMovie(BaseTestCase):   

    def setUp(self):
        super().setUp(create_superuser=True)

    def test_view_post(self):                    
        json_response= self.add_genre_movie()
            
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Genre for movie Inserted Successfully", json_response['message']) 
        
    def test_view_get(self):        
        # Given
        uri = GenreMovieAPI.uri

        json_response= self.add_genre_movie()            
        self.assertTrue(True, type(json_response['is_valid']))     
        
        response = self.http_send(
            uri=uri,
            method='GET',            
            code=200,
            headers=dict(
                Authorization='Bearer ' + self.data_login['data']['auth_token']
            )
        )
        json_response = json.loads(response.data.decode())  
        
        print(json_response," - json_response")                        
        # Then
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("GenreMovie List", json_response['message']) 

    def test_view_put(self): 
        time.sleep(1)               
        uri = GenreMovieAPI.uri  

        #Add first GenreMovie
        GenreMovie1 = self.add_genre_movie()

        self.assertTrue(True, type(GenreMovie1['is_valid']))     
        self.assertTrue(GenreMovie1['data']['moviegenre_id']) 
        
        #Add second GenreMovie
        GenreMovie2 = self.add_genre_movie(movie_name="The Pursuit of Happyness",director_name="Will Smith",genre_name="Fiction")

        self.assertTrue(True, type(GenreMovie2['is_valid']))     
        self.assertTrue(GenreMovie2['data']['moviegenre_id']) 

        movie_genre = MovieGenre.query.get(GenreMovie2['data']['moviegenre_id'])
        movie_id= movie_genre.movie_id
        genre_id= movie_genre.genre_id

        request_data = {            
            "movie_id": movie_id,
            "genre_id": genre_id,
            "moviegenre_id": int(GenreMovie1['data']['moviegenre_id'])
        }
                
        response = self.http_send(
            uri=uri,
            method='PUT',            
            code=200,
            request_data=request_data,
            headers=dict(
                Authorization='Bearer ' + self.data_login['data']['auth_token']
            )
        )
        
        # When
        json_response = json.loads(response.data.decode())      
        
        # Then
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Genre and Movie Updated Successfully", json_response['message'])                 
    
    def test_view_delete(self): 
        time.sleep(1)               
        uri = GenreMovieAPI.uri  

        json_response = self.add_genre_movie()

        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertTrue(json_response['data']['moviegenre_id'])        
              
        request_data = {            
            "moviegenre_id": int(json_response['data']['moviegenre_id'])
        }

        print(request_data, " - request_data")
                
        response = self.http_send(
            uri=uri,
            method='DELETE',            
            code=200,
            request_data=request_data,
            headers=dict(
                Authorization='Bearer ' + self.data_login['data']['auth_token']
            )
        )
        
        # When
        json_response = json.loads(response.data.decode())      
                
        # Then
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Genre Movie Deleted Successfully", json_response['message'])   
