import requests
import json
import hashlib
import datetime
from sqlalchemy import func
from flask import Blueprint, render_template, request, redirect, url_for, g, flash

from imdb_fynd_app.extensions import db
from imdb_fynd_app.models import User, Genre,MovieGenre,Movie

from imdb_fynd_app import app
from imdb_fynd_app.core.imdb_decorator import token_required , is_superuser, admin_login_required
from helpers import create_response_format, print_exception
from imdb_fynd_app.core.views import BaseView
from imdb_fynd_app.core.http import request_data, parse_args
from imdb_fynd_app.forms import MovieForm, MovieSearchForm
from flask_login import current_user, login_required

# -------------------
# MOVIES FLASK VIEW
# -------------------

@app.route('/results')
def search_results(search):    
    results = []

    print(search.data," - search.data")
    search_text = search.data['search']
    #this is also be search functionality
    q = db.session.query(Movie.movie_name,Movie.director_name,Movie.imdb_score,Movie.popularity.label('99popularity'),
        ) 
    if search_text == '':
        #If nothing searched display all results
        q = q
    else:
        search_text = ('%' + search_text + '%').lower()
        q = q.filter(db.or_(func.lower(Movie.movie_name).like(search_text),
                             func.lower(Movie.director_name).like(search_text)))
    
    results = [u._asdict() for u in q.all()]
    print("==resultset==",results)

    if not results:
        print("111111")
        flash('No results found!', 'success')
        return redirect('/')
    else:
        print("111111222222")
        # display results
        flash('Results found!', 'success')
        return render_template('results.html', results=results)

# try:
#     movie_name = request.values.get('movie_name')
#     director_name = request.values.get('director_name')
#     from_imdb_score=request.values.get('from_imdb_score')
#     to_imdb_score=request.values.get('to_imdb_score')
#     from_popularity = request.values.get('from_popularity')
#     to_popularity = request.values.get('from_popularity')
#     movie_id = request.values.get('movie_id')
#     genre = request.values.get('genre')
#     search_text = request.values.get('search_text')
#     #this is also be search functionality
#     q = db.session.query(Movie.movie_name,Movie.director_name,Movie.imdb_score,Movie.popularity.label('99popularity'),
#         )            

#     if movie_name:
#         q = q.filter(Movie.movie_name.like(movie_name))
#     if movie_id:
#         q = q.filter(Movie.id ==movie_id)
#     if director_name:
#         q = q.filter(Movie.director_name.like(director_name))
#     if from_imdb_score:
#         q = q.filter(Movie.imdb_score <= from_imdb_score)
#     if to_imdb_score:
#         q = q.filter(Movie.imdb_score >= to_imdb_score)
#     if from_popularity:
#         q = q.filter(Movie.popularity <= from_popularity)
#     if to_popularity:
#         q = q.filter(Movie.popularity >= to_popularity)
#     if search_text:
#         search_text = ('%' + search_text + '%').lower()
#         q = q.filter(or_(func.lower(Movie.name).like(search_text),
#                          func.lower(Movie.director_name).like(search_text)))
#     result_set = [u._asdict() for u in q.all()]
#     print("==resultset==",result_set)
#     return create_response_format(msg="Movie List",data=result_set, is_valid=True,status=200)
# except Exception as e:
#     print_exception(e)
#     print("==Something went wrong in getting all detials for Movie==",str(e))
#     return create_response_format(msg='CANNOT_FETCH_DATA_FOR_MOVIE')


def save_changes(movie, form, new=False):
    """
    Save the changes to the database
    """
    # Get data from form and assign it to the correct attributes
    # of the SQLAlchemy table object
    
    movie.movie_name = form.movie_name.data
    movie.director_name = form.director_name.data
    movie.imdb_score = form.imdb_score.data
    movie.popularity = form.popularity.data
    movie.status = 'A'
    
    if new:
        # Add the new movie to the database
        db.session.add(movie)
    # commit the data to the database
    db.session.commit()


    tags = form.genre.data    

    for genre_name in tags:
        genre = Genre.query.filter_by(genre_name=genre_name.capitalize()).first()
        if not genre:
            genre = Genre(genre_name=genre_name.capitalize(),status='A')
            db.session.add(genre)   
            # commit the data to the database
            db.session.commit()

        movie_genre = MovieGenre()
        movie_genre.genre_id = genre.id
        movie_genre.movie_id = movie.id
        movie_genre.status = 'A'
        db.session.add(movie_genre)   
            
        # commit the data to the database
        db.session.commit()



@login_required
@admin_login_required
@app.route('/movies_view',methods=['GET', 'POST','PUT','DELETE'])
def movies_view():
    try:
        # call the service for the authenitcation        
        form = MovieForm()
        if form.validate_on_submit():

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

            # movie_exists = Movie.query.filter_by(movie_name=movie_name,director_name=director_name).first()
            # if movie_exists:                
            #     return create_response_format(msg="Movie with same director already exist",status=409)
            
            movie = Movie()                    
            save_changes(movie, form, new=True)
            
            # q = Movie(movie_name=movie_name,director_name=director_name,imdb_score=imdb_score,
            #     popularity =popularity,
            #     status='A'
            #             )
            # db.session.add(q)
            # db.session.commit()

            flash('Movie Inserted Successfully!', 'success')
            return redirect(url_for('movies_view'))                    
        return render_template('movie.html', title='Movie', form=form)
    
    except Exception as e:
        print_exception(e)
        print("==Something went wrong==",str(e))
        return create_response_format(msg='CANNOT_CREATE_MOVIE_CHECK_LOG')
      
# -------------------------------
# MOVIES FLASK RESTFUL API VIEW
# -------------------------------
class MoviesAPI(BaseView): 

    uri = '/movies'

    @is_superuser
    def post(self):
        try:
            data = parse_args(
                (
                    ('movie_name', str, True),
                    ('director_name', str, True),
                    ('imdb_score', float, True),
                    ('popularity', float, True),                    
                ),
                request_data()
            )
                    
            movie_name = data.get('movie_name')            
            director_name = data.get('director_name')
            imdb_score = data.get('imdb_score')
            popularity = data.get('popularity')
                        
            movie_exists = Movie.query.filter_by(movie_name=movie_name,director_name=director_name).first()
            if movie_exists:                
                return create_response_format(msg="Movie with same director already exist",status=409)

            q = Movie(movie_name=movie_name,director_name=director_name,imdb_score=imdb_score,popularity =popularity,status='A')
            db.session.add(q)
            db.session.commit()
            return create_response_format(msg='Movie Inserted Successfully',is_valid=True,status=201,data={'movie_id':q.id})
        except Exception as e:
            print_exception(e)
            print("==Something went wrong==",str(e))
            return create_response_format(msg='CANNOT_CREATE_MOVIE_CHECK_LOG')
    
    def get(self):
        '''Everyone has view and search access, don't restrict search api access'''
        try:            
            data = parse_args(
                (
                    ('movie_name', str, False),
                    ('director_name', str, False),
                    ('from_imdb_score', float, False),
                    ('to_imdb_score', float, False),                 
                    ('from_popularity', float, False),                    
                    ('to_popularity', float, False),                    
                    ('movie_id', int, False),                    
                    ('genre', str, False),                    
                    ('search_text', str, False),
                ),
                request_data()
            )
                    
            movie_name = data.get('movie_name')            
            director_name = data.get('director_name')
            from_imdb_score = data.get('from_imdb_score')
            to_imdb_score = data.get('to_imdb_score')
            from_popularity = data.get('from_popularity')
            to_popularity = data.get('to_popularity')
            movie_id = data.get('movie_id')
            genre = data.get('genre')
            search_text = data.get('search_text')

            #this is also be search functionality
            q = db.session.query(Movie.movie_name,Movie.director_name,Movie.imdb_score,Movie.popularity.label('99popularity'),
                )            

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
            return create_response_format(msg="Movie List",data=result_set, is_valid=True,status=200)
        except Exception as e:
            print_exception(e)
            print("==Something went wrong in getting all detials for Movie==",str(e))
            return create_response_format(msg='CANNOT_FETCH_DATA_FOR_MOVIE')
    
    @is_superuser
    def put(self):
        try:  
            data = parse_args(
                (
                    ('movie_name', str, True),
                    ('director_name', str, True),
                    ('imdb_score', float, True),
                    ('popularity', float, True),                    
                    ('movie_id', int, True),                                        
                ),
                request_data()
            )
                    
            movie_name = data.get('movie_name')            
            director_name = data.get('director_name')
            imdb_score = data.get('imdb_score')
            popularity = data.get('popularity')
            movie_id = data.get('movie_id')
            
            if (not movie_id or movie_id == 'NA' or movie_id is None) or (not movie_id or movie_id == 'NA' or movie_id is None):
                return create_response_format(msg='PLS_PROVIDE_MOVIE_ID_AND_MOVIE_NAME_THAT_NEED_TO_BE_EDITED')
            try:
                #ensure that movie id integer
                if not isinstance(movie_id,int):
                    return create_response_format(msg='PLS_PROVIDE_MOVIE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("==movie_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_MOVIE_ID_IN_PROPER_FORMAT')
            movie_id= int(movie_id)
            q = db.session.query(Movie)
            q.filter(Movie.id == movie_id).update({
                    'movie_name':movie_name,
                    'updated_date': datetime.datetime.now(),
                    'director_name':director_name,
                    'imdb_score':imdb_score,
                    'popularity':popularity,

                })
            db.session.commit() 

            return create_response_format(msg='Movie Updated Successfully',is_valid=True,status=200)
        except Exception as e:
            print_exception(e)
            print("==Something went wrong in getting all detials for movie==",str(e))
            return create_response_format(msg='CANNOT_UPDATE_DATA_FOR_MOVIE')

    @is_superuser
    def delete(self):
        try:                        
            # to DELETE we need movie_id
            # we will do soft delete            
            data = parse_args(
                (                                    
                    ('movie_id', int, True),                                        
                ),
                request_data()
            )
                    
            movie_id = data.get('movie_id')
            
            if (not movie_id or movie_id == 'NA' or movie_id is None) :
                return create_response_format(msg='PLS_PROVIDE_MOVIE_ID_THAT_NEED_TO_BE_DELETED')
            try:
                #ensure that movie_id is integer
                if not isinstance(movie_id,int):
                    return create_response_format(msg='PLS_PROVIDE_MOVIE_ID_IN_PROPER_FORMAT') 
            except Exception as e:
                print("movie_id not in proper format==",str(e))
                return create_response_format(msg='PLS_PROVIDE_MOVIE_ID_IN_PROPER_FORMAT')
            movie_id = int(movie_id)

            movie_exist = Movie.query.filter_by(id=movie_id).first()
            if not movie_exist:                
                return create_response_format(msg="Movie doesn't exist, cannot delete",status=404)

            Movie.query.filter_by(id=movie_id).update({'status': 'D','updated_date': datetime.datetime.now()})
            db.session.commit() 
            
            return create_response_format(msg="Movie Deleted Successfully",is_valid=True,status=200)
        except Exception as e:
            print_exception(e)
            print("==Something went wrong in deleting a movie==",str(e))
            return create_response_format(msg='CANNOT_DELETE_DATA_FOR_MOVIE')
    


