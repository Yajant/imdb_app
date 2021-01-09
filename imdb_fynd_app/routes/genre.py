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

##GENRE
genre_blueprint= Blueprint('genre', __name__)

@genre_blueprint.route('/genre',methods=['GET', 'POST','PUT','DELETE'])
def genre():
    # call the service for the authenitcation
    session_id = request.values.get('session_id')
    if not session_id:
        return create_response_format(msg='PLS_PROVIDE_SESSION_FOR_AUTHICATION')
    
    if request.method == 'POST': 
        try:
            genre_name = request.values.get('genre_name')
            if not genre_name:
                return create_response_format(msg='PLS_PROVIDE_GENRE_NAME')
            
            q = Genre(genre_name=genre_name,status='A')
            db.session.add(q)
            db.session.commit()
            return create_response_format(is_valid=True,msg='Genre Inserted Successfully!')
        except Exception as e:
            print("==Something went wrong==",str(e))
            return create_response_format(msg='CANNOT_CREATE_GENRE_CHECK_LOG')

    elif request.method == 'GET':
        try:
            q = db.session.query(Genre.genre_name,Genre.status)
            q = q.filter(Genre.status == 'A')
            result_set = [u._asdict() for u in q.all()]
            return create_response_format(is_valid=True,data=result_set)
        except Exception as e:
            print("==Something went wrong in getting all detials for Genre==",str(e))
            return create_response_format(msg='CANNOT_FETCH_DATA_FOR_GENRE')

    elif request.method == 'PUT':
        try:
            # to update we need genre id
            genre_name = request.values.get('genre_name')
            genre_id = request.values.get('genre_id')
            if (not genre_id or genre_id == 'NA' or genre_id is None) or (not genre_id or genre_name == 'NA' or genre_name is None):
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_AND_GENRE_NAME_THAT_NEED_TO_BE_EDITED')
            try:
                #ensure that genre is integer
                if not isinstance(eval(genre_id),int):
                    return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("genre_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT')
            genre_id = int(genre_id)
            q = db.session.query(Genre)
            q.filter(Genre.id == genre_id).update({
                    'genre_name':genre_name,
                    'update_dttm': datetime.datetime.now()

                })
            db.session.commit() 

            return create_response_format(is_valid=True,msg='Genre Updated Successfully!')
        except Exception as e:
            print("==Something went wrong in getting all detials for genre==",str(e))
            return create_response_format(msg='CANNOT_UPDATING_DATA_FOR_GENRE')

    elif request.method == 'DELETE':
        try:
            # to DELETE we need genre_id
            # we will do soft delete
            genre_id = request.values.get('genre_id')
            if (not genre_id or genre_id == 'NA' or genre_id is None) :
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_THAT_NEED_TO_BE_DELETED')
            try:
                #ensure that genre_id is integer
                if not isinstance(eval(genre_id),int):
                    return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("genre_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT')
            genre_id = int(genre_id)
            q = db.session.query(Genre)
            q.filter(Genre.id == genre_id).update({
                    'status':'D',
                    'update_dttm': datetime.datetime.now()

                })
            db.session.commit() 

            return create_response_format(is_valid=True,msg='Genre Deleted Successfully!')
        except Exception as e:
            print("==Something went wrong in getting all detials for genre==",str(e))
            return create_response_format(msg='CANNOT_DELETING_DATA_FOR_GENRE')
    else:
        return create_response_format(msg='UNAUTHORISED_METHOD_FOR_ACCESS')


@genre_blueprint.route('/genre_movie',methods=['GET', 'POST','PUT','DELETE'])
def genre_movie():
    session_id = request.values.get('session_id')
    if not session_id:
        create_response_format(msg='PLS_PROVIDE_SESSION_FOR_AUTHICATION')
    
    if request.method == 'POST': 
        try:

            movie_id = request.values.get('movie_id')
            genre_id = request.values.get('genre_id')
            if not genre_id or not movie_id:
                return create_response_format(msg='PLS_PROVIDE_GENRE_NAME_MOVIE_NAME')

            
            q = MovieGenre(genre_id=genre_id,movie_id=movie_id,status='A'
                        )
            db.session.add(q)
            db.session.commit()
            return create_response_format(is_valid=True,msg='Genre for movie Inserted Successfully!')
        except Exception as e:
            print("==Something went wrong==",str(e))
            return create_response_format(msg='CANNOT_CREATE_GENRE_CHECK_LOG')

    elif request.method == 'GET':
        try:
            q = db.session.query(MovieGenre.genre_id,MovieGenre.movie_id,Movie.movie_name,
                Genre.genre_name
                )
            q = q.join(Movie,MovieGenre.movie_id == Movie.id)
            q = q.join(Genre,MovieGenre.genre_id == Genre.id)
            q = q.filter(Genre.status == 'A')
            result_set = [u._asdict() for u in q.all()]
            return create_response_format(is_valid=True,data=result_set)
        except Exception as e:
            print("==Something went wrong in getting all detials for Genre Movie==",str(e))
            return create_response_format(msg='CANNOT_FETCH_DATA_FOR_GENRE')

    elif request.method == 'PUT':
        try:
            # to update we need genre id
            movie_id = request.values.get('movie_id')
            genre_id = request.values.get('genre_id')
            moviegenre_id = request.values.get('moviegenre_id')
            if (not moviegenre_id or moviegenre_id == 'NA' or moviegenre_id is None) or (not genre_id or genre_id == 'NA' or genre_id is None) or (not movie_id or movie_id == 'NA' or movie_id is None):
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_AND_GENRE_NAME_MOVIE_NAME_THAT_NEED_TO_BE_EDITED')
            try:
                #ensure that genre is integer
                if not isinstance(eval(moviegenre_id),int):
                    return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("genre_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_IN_PROPER_FORMAT')
            moviegenre_id = int(moviegenre_id)
            q = db.session.query(MovieGenre)
            q.filter(MovieGenre.id == moviegenre_id).update({
                    'genre_id':genre_id,
                    'movie_id':movie_id,
                    'update_dttm': datetime.datetime.now()

                })
            db.session.commit() 

            return create_response_format(is_valid=True,msg='Genre and Movie Updated Successfully!')
        except Exception as e:
            print("==Something went wrong in getting all detials for genre==",str(e))
            return create_response_format(msg='CANNOT_UPDATING_DATA_FOR_GENRE_MOVIE')


    elif request.method == 'DELETE':
        try:
            # to DELETE we need moviegenre_id
            # we will do soft delete
            moviegenre_id = request.values.get('moviegenre_id')
            if (not moviegenre_id or moviegenre_id == 'NA' or moviegenre_id is None) :
                return create_response_format(msg='PLS_PROVIDE_GENRE_ID_THAT_NEED_TO_BE_DELETED')
            try:
                #ensure that moviegenre_id is integer
                if not isinstance(eval(moviegenre_id),int):
                    return create_response_format(msg='PLS_PROVIDE_MOVIE_GENRE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("moviegenre_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_MOVIE_GENRE_ID_IN_PROPER_FORMAT')
            moviegenre_id = int(moviegenre_id)
            q = db.session.query(MovieGenre)
            q.filter(MovieGenre.id == moviegenre_id).update({
                    'status':'D',
                    'update_dttm': datetime.datetime.now()

                })
            db.session.commit() 

            return create_response_format(is_valid=True,msg='Genre Movie Deleted Successfully!')
        except Exception as e:
            print("==Something went wrong in getting all detials for genre==",str(e))
            return create_response_format(msg='CANNOT_DELETING_DATA_FOR_GENRE_MOVIE')
    else:
        return create_response_format(msg='UNAUTHORISED_METHOD_FOR_ACCESS')