import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # For sessions/cookies
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-cannot-guess-this-ever'

    # For flask-email
    MAIL_SERVER = '127.0.0.1'
    MAIL_PORT = 8025
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_STARTTLS = False
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or None
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or None
    ADMINS = ['your-email@example.com']

    # For sql-alchemy database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir,'app.db')