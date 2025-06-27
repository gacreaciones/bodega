import os
import re

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_segura'
    
    # Manejo especial para la URL de Supabase
    uri = os.getenv("DATABASE_URL")
    
    # Conversión necesaria para SQLAlchemy
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = uri or "sqlite:///bodega.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
