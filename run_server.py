from topchef.api_server import app
from topchef.config import HOSTNAME, PORT, DEBUG
from topchef.database import METADATA, ENGINE

if __name__ == '__main__':
    METADATA.create_all(bind=ENGINE)
    app.run(host=HOSTNAME, port=PORT, debug=DEBUG)
