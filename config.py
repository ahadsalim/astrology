import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration"""
    
    # API Configuration
    API_KEY = os.getenv('API_KEY', '')
    API_URL = os.getenv('API_URL', 'https://api.gapgpt.app/v1')
    
    # Model Configuration
    ASTRO_MODEL = os.getenv('ASTRO_MODEL', 'gpt-4o-mini')
    SIMPLIFY_MODEL = os.getenv('SIMPLIFY_MODEL', 'gpt-5.6-luna')
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    @staticmethod
    def validate():
        """Validate required configuration"""
        if not Config.API_KEY:
            raise ValueError("API_KEY is required. Please set it in .env file")
        return True
