import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # For sessions/cookies
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-cannot-guess-this-ever'

    # For sql-alchemy database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI') or \
        'sqlite:///' + os.path.join(basedir,'app.db')