from flask import request
import os
from main import app
from werkzeug.utils import secure_filename

#configuring path and constraint to save images
UPLOAD_FOLDER = 'static\images'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
def allowed_file(filename):
  return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS