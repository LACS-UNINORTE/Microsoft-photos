from decouple import config
class Config(object):
    SECRET_KEY=config('SECRET_KEY')
    MAIL_SERVER='smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USERNAME = config('MAIL_USERNAME')
    MAIL_PASSWORD = config('MAIL_PASSWORD')
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

class DevelopmentConfig(Config):
    DEBUG=True

class ProductionConfig(Config):
    DEBUG=False
    HOST='lacs.photos.net'
