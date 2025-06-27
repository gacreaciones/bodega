import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_segura'
    
    # Obtener la variable de entorno DATABASE_URL
    uri = os.getenv("DATABASE_URL")
    
    # Manejo de la URI de la base de datos
    if uri:
        # Convertir de postgres:// a postgresql:// si es necesario
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        
        # Forzar SSL
        if "?" in uri:
            uri += "&sslmode=require"
        else:
            uri += "?sslmode=require"
        
        SQLALCHEMY_DATABASE_URI = uri
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///bodega.db"
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
