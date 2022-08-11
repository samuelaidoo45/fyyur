import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database
database = "fyyur"
database_user = "postgres"
password = "password"
database_host = "127.0.0.1"
database_host_port = "5432"
DATABASE_URI = "postgresql://{}:{}@{}/{}".format(database_user,password,database_host+":"+database_host_port,database)
# DATABASE_URI = "postgresql://postgres:password@localhost:5432/fyyur"

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = DATABASE_URI


# TODO IMPLEMENT DATABASE URL
#SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost:5432/fyyur'
