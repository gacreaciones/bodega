import os
import re

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_segura'
    
    # Manejo especial para la URL de Supabase
    uri = os.getenv("DATABASE_URL")
    
        if uri:
        # Forzar SSL
        if "?" in uri:
            uri += "&sslmode=require"
        else:
            uri += "?sslmode=require"
        
        SQLALCHEMY_DATABASE_URI = uri
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///bodega.db"
