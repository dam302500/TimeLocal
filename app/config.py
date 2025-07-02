import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration de base pour TimeLocal"""
    
    # Clés secrètes
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-key-change-in-production-urgently'
    
    # Base de données
    DATABASE_PATH = os.environ.get('DATABASE_PATH') or 'timelocal.db'
    DATABASE_URL = f"sqlite:///{DATABASE_PATH}"
    
    # Application
    APP_NAME = 'TimeLocal'
    APP_VERSION = '2.0.0'
    APP_URL = os.environ.get('APP_URL') or 'http://localhost:5000'
    
    # Upload de fichiers
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    
    # Stripe (Paiements)
    STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY')
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Twilio (SMS)
    TWILIO_SID = os.environ.get('TWILIO_SID')
    TWILIO_TOKEN = os.environ.get('TWILIO_TOKEN')
    TWILIO_PHONE = os.environ.get('TWILIO_PHONE')
    
    # Email (SMTP)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'True').lower() == 'true'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or MAIL_USERNAME
    
    # Google Maps (optionnel)
    GOOGLE_MAPS_API_KEY = os.environ.get('GOOGLE_MAPS_API_KEY')
    
    # Géolocalisation
    DEFAULT_RADIUS = int(os.environ.get('DEFAULT_RADIUS') or 5)  # km
    MAX_RADIUS = int(os.environ.get('MAX_RADIUS') or 50)  # km
    
    # Sessions
    SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7  # 7 jours
    
    # CORS
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')
    
    # Cache
    CACHE_TYPE = os.environ.get('CACHE_TYPE') or 'simple'
    CACHE_DEFAULT_TIMEOUT = int(os.environ.get('CACHE_DEFAULT_TIMEOUT') or 300)
    
    # Rate limiting
    RATELIMIT_STORAGE_URL = os.environ.get('REDIS_URL') or 'memory://'
    RATELIMIT_DEFAULT = os.environ.get('RATELIMIT_DEFAULT') or '100 per hour'
    
    # Logging
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'INFO'
    LOG_FILE = os.environ.get('LOG_FILE') or 'timelocal.log'
    
    # SocketIO
    SOCKETIO_ASYNC_MODE = 'eventlet'
    SOCKETIO_CORS_ALLOWED_ORIGINS = CORS_ORIGINS
    
    # Gamification
    POINTS_PER_HOUR = int(os.environ.get('POINTS_PER_HOUR') or 10)
    DAILY_MISSION_REFRESH_HOUR = int(os.environ.get('DAILY_MISSION_REFRESH_HOUR') or 9)
    
    # Notifications
    PUSH_VAPID_PRIVATE_KEY = os.environ.get('PUSH_VAPID_PRIVATE_KEY')
    PUSH_VAPID_PUBLIC_KEY = os.environ.get('PUSH_VAPID_PUBLIC_KEY')
    PUSH_VAPID_CLAIM_EMAIL = os.environ.get('PUSH_VAPID_CLAIM_EMAIL')
    
    # Debug
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    TESTING = os.environ.get('FLASK_TESTING', 'False').lower() == 'true'
    
    @staticmethod
    def allowed_file(filename):
        """Vérifie si l'extension du fichier est autorisée"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
    
    @classmethod
    def validate_config(cls):
        """Valide la configuration et retourne les erreurs"""
        errors = []
        
        if cls.SECRET_KEY == 'dev-key-change-in-production-urgently':
            errors.append("SECRET_KEY doit être changée en production")
        
        if not cls.STRIPE_SECRET_KEY and not cls.DEBUG:
            errors.append("STRIPE_SECRET_KEY requis en production")
        
        if not cls.MAIL_USERNAME and not cls.DEBUG:
            errors.append("Configuration email requise en production")
        
        return errors

class DevelopmentConfig(Config):
    """Configuration de développement"""
    DEBUG = True
    TESTING = False

class ProductionConfig(Config):
    """Configuration de production"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    @classmethod
    def validate_config(cls):
        errors = super().validate_config()
        
        if not cls.STRIPE_SECRET_KEY:
            errors.append("STRIPE_SECRET_KEY obligatoire en production")
        
        if not cls.MAIL_USERNAME:
            errors.append("Configuration email obligatoire en production")
        
        return errors

class TestingConfig(Config):
    """Configuration de test"""
    DEBUG = True
    TESTING = True
    DATABASE_PATH = ':memory:'
    WTF_CSRF_ENABLED = False

# Configuration par défaut selon l'environnement
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}