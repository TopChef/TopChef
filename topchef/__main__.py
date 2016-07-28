#!/usr/bin/env python
import os
from topchef.api_server import app
from topchef.config import config
from topchef.database import METADATA

METADATA.create_all(bind=config.database_engine)

if not os.path.isdir(config.SCHEMA_DIRECTORY):
    os.mkdir(config.SCHEMA_DIRECTORY)

app.run(host=config.HOSTNAME, port=config.PORT, debug=config.DEBUG)
