"""
Contains user-serviceable configuration parameters
"""
import os

# METADATA
SOURCE_REPOSITORY = 'https://www.github.com/MichalKononenko/TopChef'
VERSION = '0.1dev'
AUTHOR = 'Michal Kononenko'
AUTHOR_EMAIL = 'michalkononenko@gmail.com'

# HOSTING PARAMETERS
PORT = 5000
HOSTNAME = 'localhost'
THREADS = 3
DEBUG = True

#DIRECTORY
BASE_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
SCHEMA_DIRECTORY = os.path.join(BASE_DIRECTORY, 'schemas')

# DATABASE
DATABASE_URI = 'sqlite:////var/tmp/db.sqlite3'


# ROOT USER
ROOT_USERNAME = 'root'
ROOT_EMAIL = 'mkononen@uwaterloo.ca'
