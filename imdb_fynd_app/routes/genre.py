import requests
import json
import hashlib
import datetime
# from URL_CONSTANTS import API_ROOT
from sqlalchemy import func
from flask import Blueprint, render_template, request, redirect, url_for, g

from imdb_fynd_app.extensions import db
from imdb_fynd_app.models import User, Genre,MovieGenre,Movie

from imdb_fynd_app.core.imdb_decorator import token_required , is_superuser
from helpers import create_response_format, print_exception, isValidEmail
from imdb_fynd_app.core.views import BaseView
from imdb_fynd_app.core.http import request_data, parse_args

# ---------------
# GENRE
# ---------------

class GenreAPI(BaseView): 

    uri = '/genre'

    @is_superuser
    def post(self):
        try:
            data = parse_args(
                (
                    ('genre_name', str, True),                    
                ),
                request_data()
            )
                    
            genre_name = data.get('genre_name')                        
                    
            q = Genre(genre_name=genre_name,status='A')
            db.session.add(q)
            db.session.commit()
            return create_response_format(is_valid=True,msg='Genre Inserted Successfully',status=201,data={'genre_id':q.id})
        except Exception as e:
            print_exception(e)
            print("==Something went wrong==",str(e))
            return create_response_format(msg='CANNOT_CREATE_GENRE_CHECK_LOG')

    @is_superuser
    def get(self):
        try:
            q = db.session.query(Genre.genre_name,Genre.status)
            q = q.filter(Genre.status == 'A')
            result_set = [u._asdict() for u in q.all()]
            return create_response_format(is_valid=True,data=result_set,status=200,msg="Genre List")
        except Exception as e:
            print_exception(e)
            print("==Something went wrong in getting all detials for Genre==",str(e))
            return create_response_format(msg='CANNOT_FETCH_DATA_FOR_GENRE')

    @is_superuser
    def put(self):
        try:
            # to update we need genre id
            data = parse_args(
                (
                    ('genre_name', str, True),                    
                    ('genre_id', int, True),                    
                ),
                request_data()
            )
                    
            genre_name = data.get('genre_name')
            genre_id = data.get('genre_id')

            if (not genre_id or genre_id == 'NA' or genre_id is None) or (not genre_id or genre_name == 'NA' or genre_name is None):
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_AND_GENRE_NAME_THAT_NEED_TO_BE_EDITED')
            try:
                #ensure that genre is integer
                if not isinstance(genre_id,int):
                    return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("genre_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT')
            genre_id = int(genre_id)
            q = db.session.query(Genre)
            q.filter(Genre.id == genre_id).update({
                    'genre_name':genre_name,
                    'updated_date': datetime.datetime.now()

                })
            db.session.commit() 

            return create_response_format(is_valid=True,msg='Genre Updated Successfully',status=200)
        except Exception as e:
            print_exception(e)
            print("==Something went wrong in getting all detials for genre==",str(e))
            return create_response_format(msg='CANNOT_UPDATING_DATA_FOR_GENRE')

    @is_superuser
    def delete(self):
        try:
            # to DELETE we need genre_id
            # we will do soft delete            
            data = parse_args(
                (                    
                    ('genre_id', int, True),                    
                ),
                request_data()
            )
                                
            genre_id = data.get('genre_id')

            if (not genre_id or genre_id == 'NA' or genre_id is None) :
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_THAT_NEED_TO_BE_DELETED')
            try:
                #ensure that genre_id is integer
                if not isinstance(genre_id,int):
                    return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("genre_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT')
            
            genre_id = int(genre_id)
            genre_exist = Genre.query.filter_by(id=genre_id).first()
            if not genre_exist:                
                return create_response_format(msg="Genre doesn't exist, cannot delete",status=404)

            Genre.query.filter_by(id=genre_id).update({'status': 'D','updated_date': datetime.datetime.now()})
            db.session.commit()

            return create_response_format(is_valid=True,msg='Genre Deleted Successfully',status=200)
        except Exception as e:
            print_exception(e)
            print("==Something went wrong in getting all detials for genre==",str(e))
            return create_response_format(msg='CANNOT_DELETE_DATA_FOR_GENRE')

# ---------------
# GENRE MOVIE
# ---------------

class GenreMovieAPI(BaseView):    
    uri = '/genre_movie'
    
    @is_superuser
    def post(self):
        try:
            data = parse_args(
                (                    
                    ('movie_id', int, True),                    
                    ('genre_id', int, True),                    
                ),
                request_data()
            )
                                
            movie_id = data.get('movie_id')
            genre_id = data.get('genre_id')
            
            q = MovieGenre(genre_id=genre_id,movie_id=movie_id,status='A'
                        )
            db.session.add(q)
            db.session.commit()
            return create_response_format(is_valid=True,msg='Genre for movie Inserted Successfully',status=201,data={'moviegenre_id': q.id})
        except Exception as e:
            print_exception(e)
            print("==Something went wrong==",str(e))
            return create_response_format(msg='CANNOT_CREATE_GENRE_CHECK_LOG')

    @is_superuser
    def get(self):
        try:
            q = db.session.query(MovieGenre.genre_id,MovieGenre.movie_id,Movie.movie_name,
                Genre.genre_name
                )
            q = q.join(Movie,MovieGenre.movie_id == Movie.id)
            q = q.join(Genre,MovieGenre.genre_id == Genre.id)
            q = q.filter(Genre.status == 'A')
            result_set = [u._asdict() for u in q.all()]
            return create_response_format(is_valid=True,data=result_set,status=200,msg="GenreMovie List")
        except Exception as e:
            print_exception(e)
            print("==Something went wrong in getting all detials for Genre Movie==",str(e))
            return create_response_format(msg='CANNOT_FETCH_DATA_FOR_GENRE')

    @is_superuser
    def put(self):
        try:
            # to update we need genre id            
            data = parse_args(
                (                    
                    ('movie_id', int, True),                                                        
                    ('genre_id', int, True),                                                        
                    ('moviegenre_id', int, True),                                                        
                ),
                request_data()
            )
                                
            movie_id = data.get('movie_id')    
            genre_id = data.get('genre_id')    
            moviegenre_id = data.get('moviegenre_id')    

            if (not moviegenre_id or moviegenre_id == 'NA' or moviegenre_id is None) or (not genre_id or genre_id == 'NA' or genre_id is None) or (not movie_id or movie_id == 'NA' or movie_id is None):
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_AND_GENRE_NAME_MOVIE_NAME_THAT_NEED_TO_BE_EDITED')
            try:
                #ensure that genre is integer
                if not isinstance(moviegenre_id,int):
                    return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("genre_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT')
            moviegenre_id = int(moviegenre_id)
            q = db.session.query(MovieGenre)
            q.filter(MovieGenre.id == moviegenre_id).update({
                    'genre_id':genre_id,
                    'movie_id':movie_id,
                    'updated_date': datetime.datetime.now()

                })
            db.session.commit() 

            return create_response_format(is_valid=True,msg='Genre and Movie Updated Successfully',status=200)
        except Exception as e:
            print("==Something went wrong in getting all detials for genre==",str(e))
            return create_response_format(msg='CANNOT_UPDATING_DATA_FOR_GENRE_MOVIE')

    @is_superuser
    def delete(self):
        try:
            # to DELETE we need moviegenre_id
            # we will do soft delete            
            data = parse_args(
                (                    
                    ('moviegenre_id', int, True),                                                        
                ),
                request_data()
            )
                                
            moviegenre_id = data.get('moviegenre_id')            

            if (not moviegenre_id or moviegenre_id == 'NA' or moviegenre_id is None) :
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_THAT_NEED_TO_BE_DELETED')
            try:
                #ensure that moviegenre_id is integer
                if not isinstance(moviegenre_id,int):
                    return create_response_format(msg='PLS_PROVIDE_MOVIE_GENRE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("moviegenre_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_MOVIE_GENRE_ID_IN_PROPER_FORMAT')

            moviegenre_id = int(moviegenre_id)            
            moviegenre_exist = MovieGenre.query.filter_by(id=moviegenre_id).first()
            if not moviegenre_exist:                
                return create_response_format(msg="MovieGenre doesn't exist, cannot delete",status=404)

            MovieGenre.query.filter_by(id=moviegenre_id).update({'status': 'D','updated_date': datetime.datetime.now()})
            db.session.commit()

            return create_response_format(is_valid=True,msg='Genre Movie Deleted Successfully',status=200)
        except Exception as e:
            print("==Something went wrong in getting all detials for genre==",str(e))
            return create_response_format(msg='CANNOT_DELETING_DATA_FOR_GENRE_MOVIE')
