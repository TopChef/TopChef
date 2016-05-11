from topchef.api_server import app, create_root_user, create_metadata
from topchef.config import HOSTNAME, PORT, DEBUG

if __name__ == '__main__':
    create_metadata()
    create_root_user()
    app.run(host=HOSTNAME, port=PORT, debug=DEBUG)
