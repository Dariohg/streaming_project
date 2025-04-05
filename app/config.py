import os
from dotenv import load_dotenv

load_dotenv()


# Configuración base
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev_key_change_in_production'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    VIDEOS_PER_PAGE = 12
    ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mkv', 'mov', 'webm'}

    @staticmethod
    def init_app(app):
        pass


# Configuración de desarrollo
class DevelopmentConfig(Config):
    DEBUG = True
    DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or 'sqlite:///streaming.sqlite'


# Configuración de producción
class ProductionConfig(Config):
    DEBUG = False
    DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///streaming.sqlite'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Configuración de logs para producción
        import logging
        from logging.handlers import RotatingFileHandler

        file_handler = RotatingFileHandler('logs/streaming.log',
                                           maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('Streaming app startup')


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}