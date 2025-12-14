import os

class Config:
    # Clave secreta - usa variable de entorno o fallback
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_secret_key_change_in_production')
    
    # Configuración de correo con Gmail
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'pipeg5275@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'nmeqvujhvrtyeqzn')
    MAIL_DEFAULT_SENDER = ("HandiGenius", os.environ.get('MAIL_USERNAME', 'pipeg5275@gmail.com'))


class DevelopmentConfig(Config):
    DEBUG = True
    MYSQL_HOST = os.environ.get('MYSQL_HOST', 'localhost')
    MYSQL_USER = os.environ.get('MYSQL_USER', 'root')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', '')
    MYSQL_DB = os.environ.get('MYSQL_DB', 'handigeniussandra')


class ProductionConfig(Config):
    DEBUG = False
    # En producción DEBE usar variables de entorno
    MYSQL_HOST = os.environ.get('MYSQL_HOST')
    MYSQL_USER = os.environ.get('MYSQL_USER')
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD')
    MYSQL_DB = os.environ.get('MYSQL_DB')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig
}