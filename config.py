import os
import urllib.parse

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_segura'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Obtener y procesar la URI de la base de datos
    uri = os.getenv("DATABASE_URL")
    
    if uri:
        # Decodificar para manejar caracteres especiales
        decoded_uri = urllib.parse.unquote(uri)
        
        # Convertir de postgres:// a postgresql://
        if decoded_uri.startswith("postgres://"):
            decoded_uri = decoded_uri.replace("postgres://", "postgresql://", 1)
        
        # Asegurar parámetro SSL
        if "sslmode=require" not in decoded_uri:
            if "?" in decoded_uri:
                decoded_uri += "&sslmode=require"
            else:
                decoded_uri += "?sslmode=require"
        
        SQLALCHEMY_DATABASE_URI = decoded_uri
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///bodega.db"
