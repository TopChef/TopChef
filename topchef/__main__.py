#!/usr/bin/env python
from topchef.api_server import app
from topchef.config import config
from topchef.database import METADATA

METADATA.create_all(bind=config.database_engine)
app.run(host=config.HOSTNAME, port=config.PORT, debug=config.DEBUG)
