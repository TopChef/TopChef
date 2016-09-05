#!/usr/bin/env python
from topchef import configuration, METADATA

METADATA.create_all(bind=configuration.database_engine)

