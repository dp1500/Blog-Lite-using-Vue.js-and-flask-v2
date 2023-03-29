from database import db
from flask_login import UserMixin
from flask_login import login_user
from flask_login import LoginManager
from datetime import datetime


# from sqlalchemy.ext.declarative import declarative_base
# from flask_sqlalchemy import SQLAlchemy

# engine = None
# Base = declarative_base()
# db = SQLAlchemy()

login_manager = LoginManager()

# @login_manager.user_loader
# def load_user(user_id):
#   return users.query.get(int(user_id))

@login_manager.user_loader 
def load_user(user):
  return users.query.get(int(user))


class users(db.Model, UserMixin):
  __tablename__ = 'users'
  Uid = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True, nullable = False)
  username = db.Column(db.String, unique = True, nullable = False)
  name = db.Column(db.String, nullable = False)
  email = db.Column(db.String, nullable = False)
  password = db.Column(db.String, nullable = False)
  about = db.Column(db.String)
  profile_pic_url = db.Column(db.String)
  posts = db.Column(db.Integer)
  n_following = db.Column(db.Integer)
  n_followers = db.Column(db.Integer)
  
  def get_id(self):
           return (self.Uid)

class blogs(db.Model, UserMixin):
  __tablename__ = 'blogs'
  # __table_args__ = {'extend_existing': True}
  blog_id = db.Column(db.Integer, autoincrement = True, primary_key = True, unique = True, nullable = False)
  user_id = db.Column(db.Integer, db.ForeignKey("users.Uid"), unique = True,nullable = False)
  title = db.Column(db.String, nullable = False)
  description = db.Column(db.String, nullable = False)
  image_url = db.Column(db.String)
  likes = db.Column(db.Integer)
  n_comments = db.Column(db.Integer)
  time_stamp = db.Column(db.DateTime,nullable=False, unique=False, index=False,default=datetime.utcnow)


class follows(db.Model, UserMixin):
  __tablename__ = 'follows'
  following = db.Column(db.Integer,  db.ForeignKey("blogs.blog_id") ,unique = True, primary_key=True ,nullable = False)
  follower = db.Column(db.Integer, db.ForeignKey("users.Uid") , primary_key=True, unique = True, nullable = False)


class comments(db.Model, UserMixin):
  __tablename__ = 'comments'
  blog_id = db.Column(db.Integer, db.ForeignKey("users.Uid"), unique = True, primary_key=True ,nullable = False)
  poster_user_id = db.Column(db.Integer, db.ForeignKey("users.Uid"), unique = True,nullable = False)
  comment = db.Column(db.String, nullable = False)


    
    