import json, time
from imdb_fynd_app.extensions import db
from imdb_fynd_app.core.tests import BaseTestCase
from imdb_fynd_app.models import User, Genre,MovieGenre,Movie
from imdb_fynd_app.routes.movies import MoviesAPI

# -------------------------------
# TEST USER
# To run the test enter this command in your terminal.
# python -m unittest /home/yajant/Downloads/imdb_fynd_app/imdb_fynd_app/tests/test_movie.py
# -------------------------------
class TestMovie(BaseTestCase):   

    def setUp(self):
        super().setUp(create_superuser=True)

    def test_view_post(self):                    
        json_response = self.add_movie()
            
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Movie Inserted Successfully", json_response['message']) 
        
    def test_view_get(self):        
        # Given
        uri = MoviesAPI.uri
        
        response = self.http_send(
            uri=uri,
            method='GET',            
            code=200,
            headers=dict(
                Authorization='Bearer ' + self.data_login['data']['auth_token']
            )
        )
        json_response = json.loads(response.data.decode())  
                        
        # Then
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Movie List", json_response['message']) 

    def test_view_put(self): 
        time.sleep(1)               
        uri = MoviesAPI.uri  

        json_response = self.add_movie()

        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertTrue(json_response['data']['movie_id'])        
              
        request_data = {
            "popularity": 93.0,
            "director_name": "Brijesh",            
            "imdb_score": 9.3,
            "movie_name": "Chronicles of FYND",
            "movie_id": int(json_response['data']['movie_id'])
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
        self.assertEqual("Movie Updated Successfully", json_response['message']) 
        self.assertEqual(93.0, request_data['popularity'])    
        self.assertEqual(9.3, request_data['imdb_score'])    
        self.assertEqual("Brijesh", request_data['director_name'])    
        self.assertEqual("Chronicles of FYND", request_data['movie_name'])  
    
    def test_view_delete(self): 
        time.sleep(1)               
        uri = MoviesAPI.uri  

        json_response = self.add_movie()

        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertTrue(json_response['data']['movie_id'])        
              
        request_data = {            
            "movie_id": int(json_response['data']['movie_id'])
        }
                
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
        
        print(json_response,  " - json_response")
        # Then
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Movie Deleted Successfully", json_response['message'])   

class TestMovieEndUser(BaseTestCase):

    def test_view_get(self):     
        q = Movie(movie_name="Chronicles of FYND",director_name="Brijesh",imdb_score=9.3,popularity =93.0,status='A')
        db.session.add(q)
        db.session.commit()

        # Given
        uri = MoviesAPI.uri
        
        response = self.http_send(
            uri=uri,
            method='GET',            
            code=200,            
        )
        json_response = json.loads(response.data.decode())  
                
        # Then
        self.assertTrue(True, type(json_response['is_valid']))     
        self.assertEqual("Movie List", json_response['message']) 