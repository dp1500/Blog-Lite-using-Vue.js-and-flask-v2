from flask import Flask, jsonify,make_response

from flask_cors import CORS

import requests
from flask import render_template
from flask import request
from flask_login import login_user
from flask_login import LoginManager
from flask_login import current_user
from werkzeug.utils import secure_filename 
from flask_restful import Resource, Api


# import uuid
from werkzeug.security import generate_password_hash, check_password_hash
# import jwt
import datetime
from functools import wraps


from requests.adapters import HTTPAdapter

# Create a session with a specific number of retries
s = requests.Session()
adapter = HTTPAdapter(max_retries=3)
s.mount('https://', adapter)

from APIs import *
# from flask_jwt_extended import create_access_token, JWTManager, jwt_required
from jwt_utils import jwt

import os

from models import *

import sqlalchemy
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import create_engine
# from sqlalchemy import Table, Column, Integer, String, ForeignKey, delete
 
current_dir = os.path.abspath(os.path.dirname(__file__))

from config import *

app = Flask(__name__)

from flask_jwt_extended import JWTManager
app.config.from_object(Config)
jwt.init_app(app)
jwt = JWTManager(app)


app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + os.path.join(
  current_dir, "database.sqlite3")

from database import db
db.init_app(app)


# Import API routes from APIs.py
from APIs import api_routes

# Register API routes with app
app.register_blueprint(api_routes)

login_manager = LoginManager(app)
login_manager.init_app(app)
@login_manager.user_loader
def load_user(user_id):
  return users.query.get(int(user_id))

#configuring flask api
api = Api(app)
api.init_app(app)
   
CORS(app, resources={r"/*": {"origins": "*"}})

app.app_context().push()

engine = create_engine("sqlite:///./database.sqlite3")


# #creating api for login
# class Login(Resource):
#     def post(self):
        
#         username = request.json.get('username')
#         password = request.json.get('password') 

#         user = users.query.filter_by(username=username).first()

#         if user == None:
#             response = jsonify(error='Username Does Not Exist')
#             response.status_code = 409  # HTTP status code for conflict
#             return response
        
#         elif user.password != password:
#             response = jsonify(error='Invalid credentials')
#             response.status_code = 401  # HTTP status code for conflict
#             return response
        
#         elif user.password == password:
#             access_token = create_access_token(identity=username)
#             return {'access_token': access_token}, 200




@app.route('/shark', methods = ['GET', 'POST'])
def shark():
    if request.method == 'POST':
        name = "test 1"
        username = "test 1 username"
        password = "password test"
        

        new_user = users(username=username, name=name, password = password, posts = 0, n_followers=0, n_following=0)
        db.session.add(new_user)
        db.session.commit()
        
        return 'database updates with username: ' + username
    else:
        return 'Hello this is shark d from flask backend'

if __name__ == '__main__':
    app.run(debug = True)
