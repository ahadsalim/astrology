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

    # Model Configuration
    ASTRO_MODEL = os.getenv('ASTRO_MODEL', 'agnes-2.0-flash')
    SIMPLIFY_MODEL = os.getenv('SIMPLIFY_MODEL', 'agnes-2.0-flash')

    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'change-me-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'

    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))

    @staticmethod
    def is_ai_configured():
        """Return True when an API key is available for AI features."""
        key = (Config.API_KEY or '').strip()
        return bool(key) and key.lower() != 'your_api_key_here'

    @staticmethod
    def validate():
        """Validate configuration.

        AI features require an API key, but the core Swiss Ephemeris flow works
        without one. So this never raises — it only reports whether AI is ready.
        """
        return Config.is_ai_configured()
