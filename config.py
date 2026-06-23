import os 

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = 'super_secret'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'bootcamp.db')
    SQLALCHEMY_TRACK_MODIFICATION = False