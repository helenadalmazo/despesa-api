database_filename = "despesa_api.db"

class Config:
    DEBUG = True
    SECRET_KEY = "dXNlcm5hbWU6cGFzc3dvcmQ="
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + database_filename
    SQLALCHEMY_TRACK_MODIFICATIONS = False