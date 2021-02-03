
class Config(object):
    SECRET_KEY = 'secret_key'
    #Flask Mail Config
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'FinantecAppDomain@gmail.com'
    MAIL_PASSWORD = 'SWE4713domain'
    MAIL_DEFAULT_SENDER = 'FinantecAppDomain@gmail.com'
    MAIL_MAX_EMAILS = None
    MAIL_ASCII_ATTACHMENTS = False

class DevelopementConfig(Config):
    pass