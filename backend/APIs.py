from flask_restful import Resource, fields, marshal_with,reqparse, Api
from flask import jsonify
from models import *
from database import db
from validation import *
from flask import request, flash,Blueprint
from sqlalchemy import desc , select, join
from useful_functions import update_followers_AND_following_count

# from flask_jwt_extended import create_access_token, JWTManager, jwt_required
from jwt_utils import jwt
from flask_jwt_extended import jwt_required, get_jwt_identity

from flask_jwt_extended import create_access_token

# Create blueprint for API routes
api_routes = Blueprint('api', __name__)
api = Api(api_routes)

# from getImage import *

# from werkzeug.utils import secure_filename
# import os


# #configuring path and constraint to save images
# UPLOAD_FOLDER = 'static\images'
# ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# def allowed_file(filename):
#   return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# parser for updating profile data
profile_parser = reqparse.RequestParser()
profile_parser.add_argument('name')
profile_parser.add_argument('username')
profile_parser.add_argument('about')
profile_parser.add_argument('old_password')
profile_parser.add_argument('new_password')
profile_parser.add_argument('file')

profile_parser.add_argument('password')

#creating api for login
class Login(Resource):
    def post(self):
        
        username = request.json.get('username')
        password = request.json.get('password')

        user = users.query.filter_by(username=username).first()

        if user == None:
            response = jsonify(error='Username Does Not Exist')
            response.status_code = 409  # HTTP status code for conflict
            return response
        
        elif user.password != password:
            response = jsonify(error='Invalid credentials')
            response.status_code = 401  # HTTP status code for conflict
            return response
        
        elif user.password == password:
            access_token = create_access_token(identity=username)
            return {'access_token': access_token}, 200


# api to login using token based authentication
api.add_resource(Login, '/api/login')


#api for login out that deletes the cookie (token)
class Logout(Resource):
    def post(self):
        pass

class ProfileDataApi(Resource):
    
    @jwt_required()
    def get(self):
        
        current_user = get_jwt_identity()
        
        # update_followers_AND_following_count(Uid)

        user = users.query.filter_by(username=current_user).first() 

        if user:
            response = { "Uid": user.Uid, "name": user.name, "username": user.username, "posts": user.posts, "n_followers": user.n_followers, "n_following": user.n_following, "about": user.about, "profile_pic_url" : user.profile_pic_url}
            

            return jsonify(response)
        else:
            response = jsonify(error='Username Does Not Exist')
            response.status_code = 409  # HTTP status code for conflict
            return response

    def post(self):

        name = request.json.get('name')
        username = request.json.get('username')
        email = request.json.get('email')
        password = request.json.get('password')
        
        username_exists = users.query.filter_by(username=username).first()

        if username_exists:
            response = jsonify(error='Username already exists')
            response.status_code = 409  # HTTP status code for conflict
            return response

        else:
            new_user = users(username=username, name=name, password = password, email = email, posts = 0, n_followers=0, n_following=0)
            db.session.add(new_user)
            db.session.commit()

            return 200


    def put(self, Uid):
        Uid = int(Uid)
        user = db.session.query(users).filter(users.Uid == Uid).first()

        if user:

            args =profile_parser.parse_args()
            name = args.get("name", None) 
            username = args.get("username", None)
            about = args.get("about", None)
            old_password = args.get("old_password", None)
            new_password = args.get("new_password", None)
            file = args.get('file', None)

            if old_password == user.password:
                user.name = name
                user.username = username
                user.about = about
                
                if new_password:
                    user.password = new_password
                
                if file:

                    if file == '':
                        print('No image selected')

                    if file:
                        user.profile_pic_url = file
                        
                db.session.commit()
                flash("profile updated succesfully")
                # return { "Uid": user.Uid, "name": user.name, "username": user.username, "posts": user.posts, "followers": user.n_followers, "following": user.n_following, "about": user.about}
                return 200
            else:
                raise NotFoundError(message = "incorrect password", status_code= 400)
        else:
            raise NotFoundError(message = "user not found", status_code= 204)

    def delete(self, Uid):
        Uid = int(Uid)
        user = db.session.query(users).filter(users.Uid == Uid).first()

        if user:
            # blogs_by_user = db.session.query(blogs).filter(blogs.user_id == Uid).all()
            delete_blogs_by_user = blogs.__table__.delete().where(blogs.user_id == Uid)


            # followings = follows.query.filter(follows.follower == Uid or follows.following == Uid).all()
            delete_followings = follows.__table__.delete().where(follows.follower == Uid)
            delete_followers = follows.__table__.delete().where(follows.following == Uid)


            db.session.delete(user)

            # db.session.delete(blogs_by_user)
            # db.session.delete(followings)

            db.session.execute(delete_blogs_by_user)
            db.session.execute(delete_followings)
            db.session.execute(delete_followers)

            db.session.commit()
            return "profile succesfully deleted", 200
        else:
           raise NotFoundError(message = "user not found", status_code= 204)
 




class ProfileBlogsApi(Resource):
    def get(self, Uid):
        Uid = int(Uid)
        # user = db.session.query(users).filter(users.Uid == Uid).first()
       
        Blogs = db.session.query(blogs).filter(blogs.user_id == Uid).order_by(desc(blogs.time_stamp)) 
        

        if Blogs:

            blogsData = []
            for blog in Blogs:
                user = db.session.query(users).filter(users.Uid == blog.user_id).first()

                blogsData.append( { "username": user.username, "blog_id" : blog.blog_id, "title": blog.title, "description" : blog.description, "image_url": blog.image_url, 
                            "time_stamp": blog.time_stamp.isoformat()  })
            
            return blogsData

        else:
            raise NotFoundError(message = "blog not found", status_code= 204)   


# to sort list of bolgs according time
from operator import itemgetter

class FeedBlogsApi(Resource):

    def get(self, Uid):
        Uid = int(Uid)

        followings = follows.query.filter(follows.follower == Uid).all()

        # blogsData = []

        # if followings == None:
        #     return blogsData, 204

        #     # raise NotFoundError(message = "blog not found", status_code= 204)   

        # else:
        blogsData = []
        for follow in followings:
            Blogs = db.session.query(blogs).filter(blogs.user_id == follow.following).order_by(desc(blogs.time_stamp)).all()
            user = db.session.query(users).filter(users.Uid == follow.following).first()

            for blog in Blogs:
                blogsData.append( { "Uid":  user.Uid, "username": user.username, "profile_pic_url": user.profile_pic_url,"blog_id" : blog.blog_id, "title": blog.title, "description" : blog.description, "image_url": blog.image_url, 
                            "time_stamp": blog.time_stamp.isoformat()  })
        
        # if blogsData == []:
        #     raise NotFoundError(message = "blog not found", status_code= 204)   

        blogsData = sorted(blogsData, key=itemgetter('time_stamp'), reverse=True) 
        return blogsData




# parser for updating blogs data
blog_parser = reqparse.RequestParser()
blog_parser.add_argument('title')
blog_parser.add_argument('description')
blog_parser.add_argument('image_url')
blog_parser.add_argument('user_Uid')


class BlogApi(Resource):

    def get(self, blog_id):
        blog_id = int(blog_id)

        blog = db.session.query(blogs).filter(blogs.blog_id == blog_id).first()

        if blog:
            return {"blog_id" : blog.blog_id, "title": blog.title, "description" : blog.description, "image_url": blog.image_url, 
                                        "time_stamp": blog.time_stamp.isoformat() }, 200
        else:
            raise NotFoundError(message = "blog not found", status_code= 204)   

    def put(self, blog_id):

        blog_id = int(blog_id)
        blog = db.session.query(blogs).filter(blogs.blog_id == blog_id).first()

        if blog:

            args =blog_parser.parse_args()
            title = args.get("title", None) 
            description = args.get("description", None)
            image_url = args.get("image_url", None)

            if title == None or description == None:
                raise BusinessValidationError(status_code= 400, error_code=	"input missing", error_message= "input missing")
            
            blog.title = title
            blog.description = description
            if  image_url != None:
                blog.image_url = image_url

            db.session.commit()
            flash("Blog  updated succesfully")
            # return { "Uid": user.Uid, "name": user.name, "username": user.username, "posts": user.posts, "followers": user.n_followers, "following": user.n_following, "about": user.about}
            return 200
        else:
            raise NotFoundError(message = "blog not found", status_code= 204)
        
    def delete(self, blog_id):
        blog_id = int(blog_id)

        blog = db.session.query(blogs).filter(blogs.blog_id == blog_id).first()

        user = db.session.query(users).filter(users.Uid == blog.user_id).first()

        if blog:
            db.session.delete(blog)
            user.posts = user.posts-1

            db.session.commit()
            return "blog succesfully deleted", 200
        else:
            raise BusinessValidationError(status_code= 400, error_code=	"input missing", error_message= "bad request")
            
    @jwt_required()
    def post(self):

        current_user = get_jwt_identity()

        title = request.form.get('title')
        description = request.form.get('description')

        image_file = request.files.get('file')

        if image_file is None:
            return 'No file uploaded', 409
    
        # save the file to a folder on the server
        file_path = 'static\images\\blogs\\' + image_file.filename
        image_file.save(file_path)

        # args =blog_parser.parse_args()
        # title = args.get("title", None) 
        # description = args.get("description", None) 
        # image_url = args.get("image_url", None)
        # user_Uid = int(args.get("user_Uid", None))

        user = users.query.filter_by(username=current_user).first()

        new_blog = blogs(user_id = user.Uid, title = title, description = description, image_url = file_path, likes =0, n_comments =0)
        db.session.add(new_blog)

        user.posts = user.posts + 1
        db.session.commit()

        return 200


from  sqlalchemy.sql.expression import func, select
import random

# api to get blogss for browse page
class BrowseBlogsApi(Resource):

    def get(self):
        
        # Blogs = db.session.query(blogs).limit(6)

        # count = db.session.query(blogs).count()
        Blogs = db.session.query(blogs).limit(10)

        if blogs:

            blogsData = []

            for blog in Blogs:
                
                if random.randint(1, 40) > 4:
                    user = db.session.query(users).filter(users.Uid == blog.user_id).first()

                    blogsData.append( { "Uid":  user.Uid, "username": user.username, "profile_pic_url": user.profile_pic_url,"blog_id" : blog.blog_id, "title": blog.title, "description" : blog.description, "image_url": blog.image_url, 
                                "time_stamp": blog.time_stamp.isoformat() })

            random.shuffle(blogsData)        
            return blogsData
        else:
            raise NotFoundError(message = "blog not found", status_code= 204)

# class LikePostApi(Resource):
    
#     def get(self, blog_id):

#         blog_id = int(blog_id)

#         blog = db.session.query(blogs).filter(blogs.blog_id == blog_id).first()
#         blog.likes = blog.like + 1

#         db.session.commit()
#         return 200


##################### ADDING ALL APIs to the blueprint #################

#users data api
api.add_resource(ProfileDataApi, "/api/ProfileData","/api/ProfileData/<string:Uid>")

#user profile blogs api
api.add_resource(ProfileBlogsApi, "/api/ProfileBlogsData","/api/ProfileBlogsData/<string:Uid>")

#Feed blogs api
api.add_resource(FeedBlogsApi, "/api/FeedBlogsData","/api/FeedBlogsData/<string:Uid>")

# blogpost api
api.add_resource(BlogApi, "/api/BlogData","/api/BlogData/<string:blog_id>")

# api to get random blogs for browse page
api.add_resource(BrowseBlogsApi, "/api/BrowseBlogsApi","/api/BrowseBlogsApi/<string:Uid>")