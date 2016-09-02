import os

os.environ["BASE_DIRECTORY"] = "/var/www/topchef"
os.environ["PORT"] = "80"
os.environ["HOSTNAME"] = "0.0.0.0"
os.environ["DATABASE_URI"] = "sqlite:////var/www/topchef/db.sqlite3"
os.environ["SCHEMA_DIRECTORY"] = "/var/www/topchef/schemas"
os.environ["DEBUG"] = "False"
os.environ["LOGFILE"] = "/var/www/topchef/topchef.log"

from topchef import app as application

