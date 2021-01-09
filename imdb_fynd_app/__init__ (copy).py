from flask import Flask, request, jsonify, make_response
from flask_sqlalchemy import SQLAlchemy
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps

app = Flask(__name__)

app.config['SECRET_KEY'] = 'qwertyuiop'
DB_NAME = 'IMDB'
SQLALCHEMY_DATABASE_URI = 'sqlite:///{}.db'.format(DB_NAME)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI

#it should be above db variable
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECURITY_PASSWORD_SALT'] = 'thisisasecretsalt'
app.debug = True

# Instantiate the database
db = SQLAlchemy(app)
bcrypt = Bcrypt()
engine = create_engine(SQLALCHEMY_DATABASE_URI)
#conn is a object
conn = engine.connect()
# Load login manger before models as it is being used in models.py
login_manager = LoginManager()
#Added this line fixed the issue.
login_manager.init_app(app) 
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

# flask-security models
roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('role.id')))

from imdb_fynd_app.models import User,Author,RelatedAuthors, Role

# Create Security
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# Only needed on first execution to create first user

# @app.before_first_request
# def create_user():
#    db.create_all()
#    user_datastore.create_user(username='admin',email='admin@mailinator.com', password='download123', superuser=True)
#    db.session.commit()

db.create_all() 

# ---------------------
# PATHS Settings 
# ---------------------
ROOT_DIR = Path(__file__).parent.parent.parent
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROJECT_DIR = os.path.dirname(app.instance_path)
# print(app.root_path,"####")
print("ROOT_DIR :",ROOT_DIR)
print("BASE_DIR :",BASE_DIR)
print("PROJECT_DIR :",PROJECT_DIR)
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
    format='[%(asctime)s]{%(pathname)s:%(lineno)d}%(levelname)s- %(message)s', 
    datefmt='%H:%M:%S'
) 
# set up logging to console 
console = logging.StreamHandler() 
console.setLevel(logging.DEBUG) 
# set a format which is simpler for console use 
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
console.setFormatter(formatter) 
# add the handler to the root logger 
logging.getLogger('').addHandler(console) 
logger = logging.getLogger(__name__)

from datetime import datetime
script_run_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
print("\n\n\n======================================================================================\n\n\n")
print("\n\n\n\n\n    PROCESS STARTED.-({0})   \n\n\n\n\n".format(script_run_at))
print("\n\n\n======================================================================================\n\n\n")

from imdb_fynd_app import routes
from imdb_fynd_app.errors import handlers

@app.route('/', methods=['GET'])
def test():
    return 'Hello world'
