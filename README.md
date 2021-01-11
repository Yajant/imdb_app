### Created RESTful API for movies using flask-restful (something similar to IMDB).

### There are 2 levels of access:
- admin = who can add, remove or edit movies.
- users = who can just view the movies.

### Installation

It requires requirements.txt installed to run.

Install the dependencies and start the server.

```sh
$ cd imdb_app
$ virtualenv --python=python3 .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ flask create_superuser
$ flask run or python app.py
```

### Test Cases Included for all routes
```sh
$ python -m unittest /imdb_fynd_app/tests/test_auth.py
$ python -m unittest /imdb_fynd_app/tests/test_movie.py
$ python -m unittest /imdb_fynd_app/tests/test_genre.py
```

### Custom Commands
```sh
$ flask create_tables
$ flask create_superuser
```



