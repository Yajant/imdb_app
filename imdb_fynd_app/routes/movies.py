import requests
import json
import hashlib
import datetime
from sqlalchemy import func
from flask import Blueprint, render_template, request, redirect, url_for, g

from imdb_fynd_app.extensions import db
from imdb_fynd_app.models import User, Genre,MovieGenre,Movie

from imdb_fynd_app.core.imdb_decorator import token_required , is_superuser
from helpers import create_response_format, print_exception
from imdb_fynd_app.core.views import BaseView

# movie_blueprint = Blueprint('movies', __name__)
# @movie_blueprint.route('/api/movies',methods=['GET', 'POST','PUT','DELETE'])

##MOVIE
class Movies(BaseView): 

    uri = '/movies'

    @is_superuser
    def post(self):
        try:            
            movie_name = request.values.get('movie_name')
            if not movie_name:
                return create_response_format(msg='PLS_PROVIDE_MOVIE_NAME')
            director_name = request.values.get('director_name')
            if not director_name:
                return create_response_format(msg='PLS_PROVIDE_DIRECTOR_NAME')
            imdb_score=request.values.get('imdb_score')
            if not imdb_score:
                return create_response_format(msg='PLS_PROVIDE_imdb_score')
            popularity = request.values.get('popularity')
            if not popularity:
                return create_response_format(msg='PLS_PROVIDE_POPULARITY_FOR_MOVIE')
        
            q = Movie(movie_name=movie_name,director_name=director_name,imdb_score=imdb_score,popularity =popularity,status='A')
            db.session.add(q)
            db.session.commit()
            return create_response_format(msg='Movie Inserted Successfully!',is_valid=True,status=201)
        except Exception as e:
            print_exception(e)
            print("==Something went wrong==",str(e))
            return create_response_format(msg='CANNOT_CREATE_GENRE_CHECK_LOG')

    @is_superuser
    def get(self):
        try:
            movie_name = request.values.get('movie_name')
            director_name = request.values.get('director_name')
            from_imdb_score=request.values.get('from_imdb_score')
            to_imdb_score=request.values.get('to_imdb_score')
            from_popularity = request.values.get('from_popularity')
            to_popularity = request.values.get('from_popularity')
            movie_id = request.values.get('movie_id')
            genre = request.values.get('genre')
            search_text = request.values.get('search_text')
            #this is also be search functionality
            q = db.session.query(Movie.movie_name,Movie.director_name,Movie.imdb_score,Movie.popularity.label('99popularity'),
                )
            q = q.filter(Movie.status == 'A')
            if movie_name:
                q = q.filter(Movie.movie_name.like(movie_name))
            if movie_id:
                q = q.filter(Movie.id ==movie_id)
            if director_name:
                q = q.filter(Movie.director_name.like(director_name))
            if from_imdb_score:
                q = q.filter(Movie.imdb_score <= from_imdb_score)
            if to_imdb_score:
                q = q.filter(Movie.imdb_score >= to_imdb_score)
            if from_popularity:
                q = q.filter(Movie.popularity <= from_popularity)
            if to_popularity:
                q = q.filter(Movie.popularity >= to_popularity)
            if search_text:
                search_text = ('%' + search_text + '%').lower()
                q = q.filter(or_(func.lower(Movie.name).like(search_text),
                                 func.lower(Movie.director_name).like(search_text)))
            result_set = [u._asdict() for u in q.all()]
            print("==resultset==",result_set)
            return create_response_format(msg="Movie List",data=result_set, is_valid=True)
        except Exception as e:
            print_exception(e)
            print("==Something went wrong in getting all detials for Genre==",str(e))
            return create_response_format(msg='CANNOT_FETCH_DATA_FOR_MOVIE')
    
    def put(self):
        '''Everyone has view and search access, don't restrict search api access'''
        try:            
            # to update we need genre id
            movie_name = request.values.get('movie_name')
            if not movie_name:
                return create_response_format(msg='PLS_PROVIDE_MOVIE_NAME')
            director_name = request.values.get('director_name')
            if not director_name:
                return create_response_format(msg='PLS_PROVIDE_DIRECTOR_NAME')
            imdb_score=request.values.get('imdb_score')
            if not imdb_score:
                return create_response_format(msg='PLS_PROVIDE_imdb_score')
            popularity = request.values.get('popularity')
            if not popularity:
                return create_response_format(msg='PLS_PROVIDE_POPULARITY_FOR_MOVIE')
            movie_id = request.values.get('movie_id')
            if (not movie_id or movie_id == 'NA' or movie_id is None) or (not movie_id or movie_id == 'NA' or movie_id is None):
                return create_response_format(msg='PLS_PROVIDE_MOVIE_ID_AND_MOVIE_NAME_THAT_NEED_TO_BE_EDITED')
            try:
                #ensure that movie id integer
                if not isinstance(eval(movie_id),int):
                    return create_response_format(msg='PLS_PROVIDE_MOVIE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("==movie_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT')
            movie_id= int(movie_id)
            q = db.session.query(Movie)
            q.filter(Movie.id == movie_id).update({
                    'movie_name':movie_name,
                    'update_dttm': datetime.datetime.now(),
                    'director_name':director_name,
                    'imdb_score':imdb_score,
                    'popularity':popularity,

                })
            db.session.commit() 

            return create_response_format(msg='Genre Updated Successfully!',is_valid=True)
        except Exception as e:
            print_exception(e)
            print("==Something went wrong in getting all detials for genre==",str(e))
            return create_response_format(msg='CANNOT_UPDATING_DATA_FOR_GENRE')

    @is_superuser
    def delete(self):
        try:                        
            # to DELETE we need movie_id
            # we will do soft delete
            movie_id = request.values.get('movie_id')
            if (not movie_id or movie_id == 'NA' or movie_id is None) :
                return create_response_format(msg='PLS_PROVIDE_MOVIE_ID_THAT_NEED_TO_BE_DELETED')
            try:
                #ensure that movie_id is integer
                if not isinstance(eval(movie_id),int):
                    return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("genre_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT')
            movie_id = int(movie_id)
            q = db.session.query(Genre)
            q.filter(Movie.id == movie_id).update({
                    'status':'D',
                    'update_dttm': datetime.datetime.now()

                })
            db.session.commit() 

            return create_response_format(msg="Movie Deleted Successfully!",is_valid=True)
        except Exception as e:
            print_exception(e)
            print("==Something went wrong in getting all detials for movie==",str(e))
            return create_response_format(msg='CANNOT_DELETE_DATA_FOR_MOVIE')
    


