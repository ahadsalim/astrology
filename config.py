import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""

    # AI provider configuration.
    # Defaults target Agnes AI — a free, OpenAI-compatible gateway.
    #   Base URL : https://apihub.agnes-ai.com/v1
    #   Free text models: agnes-2.0-flash / agnes-1.5-flash / agnes-2.5-flash
    # Get a free API key at https://platform.agnes-ai.com/ and set API_KEY.
    API_KEY = os.getenv('API_KEY', '')
    API_URL = os.getenv('API_URL', 'https://apihub.agnes-ai.com/v1')

    # Model Configuration (override in .env; GapGPT users often set SIMPLIFY_MODEL=gpt-5.6-luna)
    ASTRO_MODEL = os.getenv('ASTRO_MODEL', 'agnes-2.0-flash')
    SIMPLIFY_MODEL = os.getenv('SIMPLIFY_MODEL', 'agnes-2.0-flash')

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

