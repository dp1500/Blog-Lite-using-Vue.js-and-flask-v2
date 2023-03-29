from models import *
from database import db
from flask_login import current_user

#returns a list of all the people current user is following
def following_list(user):
  followings = follows.query.filter(follows.follower == user.Uid).all()
  following_list = []
  for following in followings:
    following_list.append(following.following)
  return following_list

# returns if current user is following inpur parameteruser
def get_follow_status(username):
  followings_list = None
  followings_list = following_list(current_user)

  following_status = False

  Other_user = db.session.query(users).filter(users.username == username).first()

  if Other_user.Uid in followings_list:
    following_status = True
  
  return following_status

# returns if current user is following inpur parameteruser
def update_followers_AND_following_count(Uid):

  user = db.session.query(users).filter(users.Uid == Uid).first()

  n_following = follows.query.filter(follows.follower == Uid).count()
  n_followers = follows.query.filter(follows.following == Uid).count()

  user.n_following = n_following
  user.n_followers = n_followers
  db.session.commit()

  return None