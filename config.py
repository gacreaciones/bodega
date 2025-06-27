import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_segura'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    uri = os.getenv("DATABASE_URL")
    SQLALCHEMY_DATABASE_URI = 'uri'
