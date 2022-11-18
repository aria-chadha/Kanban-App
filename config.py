import os
import secrets

DEBUG= True
SQLALCHEMY_DATABASE_URI = 'sqlite:///./ananya.sqlite3'
SECRET_KEY= os.environ.get("SECRET_KEY", "my_key")
salt=str(secrets.SystemRandom().getrandbits(128))
SECURITY_PASSWORD_SALT = os.environ.get("SECURITY_PASSWORD_SALT", salt)
SQLALCHEMY_TRACK_MODIFICATIONS=False