from topchef.api_server import app
from topchef.config import HOSTNAME, PORT, DEBUG

if __name__ == '__main__':
    app.run(host=HOSTNAME, port=PORT, debug=DEBUG)
