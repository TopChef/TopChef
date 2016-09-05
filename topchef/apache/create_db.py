#!/usr/bin/env python
from topchef import config, METADATA

METADATA.create_all(bind=config.database_engine)

