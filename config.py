import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'una_clave_secreta_muy_segura'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Obtener la URI de la base de datos
    uri = os.getenv("DATABASE_URL")
    
    if uri:
        print(f"Database URL from env: {uri}")
        
        # Convertir de postgres:// a postgresql://
        if uri.startswith("postgres://"):
            uri = uri.replace("postgres://", "postgresql://", 1)
        
        # Añadir SSL si no está presente
        if "sslmode" not in uri:
            if "?" in uri:
                uri += "&sslmode=require"
            else:
                uri += "?sslmode=require"
        
        SQLALCHEMY_DATABASE_URI = uri
    else:
        print("Using SQLite fallback database")
        SQLALCHEMY_DATABASE_URI = "sqlite:///bodega.db"
