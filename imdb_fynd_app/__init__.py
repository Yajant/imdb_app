import os, logging
from flask import Flask, request, jsonify, make_response
from .commands import create_tables, create_superuser
from .extensions import db, login_manager
from flask_cors import CORS

app = Flask(__name__,static_folder='static',template_folder='templates')

CORS(app)
# Add configuration variables in app
app.config.from_pyfile('settings.py')

# Initialize sqllachemy/ register sqlalchemy extension in application
db.init_app(app)

# Register cli command to create all tables
# Usage - flask run - flask create_tables
app.cli.add_command(create_tables)
app.cli.add_command(create_superuser)

# app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///IMDB.sqlite3"
# app.config["SECRET_KEY"]  = "ldfjsolasfuasdfjsodfusoij4w09r8pswojufsldkfjdf9"

# ---------------------
# CUSTOM ERROR HANDLERS
# Registering an Error Handler
# ---------------------
from imdb_fynd_app.errors.handlers import error_403, error_404, error_405, error_500
app.register_error_handler(403, error_403)
app.register_error_handler(404, error_404)
app.register_error_handler(405, error_405)
app.register_error_handler(500, error_500)

# ---------------------
# PATHS Settings 
# ---------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(app.instance_path)
# print(app.root_path,"####")

print("\nBASE_DIR :",BASE_DIR)
print("PROJECT_DIR :",PROJECT_DIR,"\n")

# ---------------------
# Logger Settings 
# ---------------------
log_path = os.path.join(PROJECT_DIR,'logs')

if not os.path.exists(log_path):
    os.makedirs(log_path)

# set up logging to file 
logging.basicConfig( 
    filename=os.path.join(log_path, 'logs.txt'),
    level=logging.INFO, 
    format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s- %(message)s', 
    datefmt='%H:%M:%S'
) 
# set up logging to console 
console = logging.StreamHandler() 
console.setLevel(logging.DEBUG) 
# set a format which is simpler for console use 
# formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
formatter = logging.Formatter('[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s- %(message)s')
console.setFormatter(formatter) 
# add the handler to the root logger 
logging.getLogger('').addHandler(console) 
logger = logging.getLogger(__name__)

from datetime import datetime
script_run_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("\n\n\n======================================================================================\n\n\n")
print("\n\n\n\n\n    PROCESS STARTED.-({0})   \n\n\n\n\n".format(script_run_at))
print("\n\n\n======================================================================================\n\n\n")

from helpers import create_response_format
@app.route('/welcome', methods=['GET'])
@app.route('/')
def welcome():
    msg = "Let's Begin"
    return create_response_format(msg=msg,status=200,is_valid=True)

from imdb_fynd_app.routes.auth import RegisterAPI, LoginAPI, LogoutAPI
from imdb_fynd_app.routes.movies import MoviesAPI
from imdb_fynd_app.routes.genre import GenreAPI, GenreMovieAPI
from flask_restful import Api

api = Api(app, prefix='/api')
resources = [
    # AUTH_APIS
    RegisterAPI, LoginAPI, LogoutAPI,
    
    # MOVIE_APIS        
    MoviesAPI,GenreAPI, GenreMovieAPI,
]

for resource in resources:
    api.add_resource(resource, resource.uri)

