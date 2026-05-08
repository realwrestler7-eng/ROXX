"""
ROXX AI - Configuration Management
Part 1 (Continued): Database Configuration & Environment Setup

This module handles:
- Database connection configuration
- Environment variables management
- App settings
- API configurations
"""

import os
from datetime import timedelta

class Config:
    """
    Base configuration class
    Contains common settings for all environments
    """
    
    # App Settings
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    DEBUG = False
    TESTING = False
    
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///roxx_ai.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # Session Configuration
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 500 * 1024 * 1024  # 500 MB max file size
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'mp3', 'wav', 'mp4', 'avi'}
    
    # AI API Keys (Load from environment)
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
    REPLICATE_API_TOKEN = os.environ.get('REPLICATE_API_TOKEN')
    HUGGINGFACE_API_KEY = os.environ.get('HUGGINGFACE_API_KEY')
    GOOGLE_API_KEY = os.environ.get('GOOGLE_API_KEY')
    
    # Voice Settings
    VOICE_SETTINGS = {
        'boy': {
            'pitch': 1.0,
            'speed': 1.0,
            'voice_id': 'boy_default'
        },
        'girl': {
            'pitch': 1.2,
            'speed': 1.0,
            'voice_id': 'girl_default'
        }
    }
    
    # AI Generation Credits
    CREDITS_CONFIG = {
        'image_generation': 10,
        'photo_repair': 15,
        'video_maker': 50,
        'voice_synthesis': 5,
        'singer': 25,
        'chat_premium': 1
    }
    
    # Logging Configuration
    LOG_LEVEL = 'INFO'
    LOG_FILE = 'logs/roxx_ai.log'


class DevelopmentConfig(Config):
    """
    Development environment configuration
    """
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///roxx_ai_dev.db'
    SQLALCHEMY_ECHO = True  # Log all SQL queries
    SESSION_COOKIE_SECURE = False
    LOG_LEVEL = 'DEBUG'


class ProductionConfig(Config):
    """
    Production environment configuration
    """
    DEBUG = False
    TESTING = False
    
    # Must be set in production
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = os.environ.get('SECRET_KEY')
    
    if not SQLALCHEMY_DATABASE_URI or not SECRET_KEY:
        raise ValueError("DATABASE_URL and SECRET_KEY must be set in production!")
    
    SESSION_COOKIE_SECURE = True
    LOG_LEVEL = 'WARNING'


class TestingConfig(Config):
    """
    Testing environment configuration
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False
    SESSION_COOKIE_SECURE = False


# Configuration Dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}


def get_config():
    """
    Get configuration based on environment
    
    Returns:
        Config: Configuration class
    """
    env = os.environ.get('FLASK_ENV', 'development')
    return config.get(env, config['default'])
