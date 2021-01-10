# Created RESTful API for movies using flash- restful (something similar to IMDB).

# There are 2 levels of access:
- admin = who can add, remove or edit movies.
- users = who can just view the movies.

# Test Cases Included for all routes
- auth =  python -m unittest /tests/test_auth.py
- movie =  python -m unittest /tests/test_movie.py
- genre = python -m unittest /tests/test_genre.py

### Installation

It requires requirements.txt installed to run.

Install the dependencies and devDependencies and start the server.

```sh
$ virtualenv --python=python3 .venv
$ source .venv/bin/activate
$ pip install -r requirements.txt
$ flask create_superuser
$ flask run or python app.py
```


