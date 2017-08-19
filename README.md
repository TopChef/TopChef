**TopChef**

[![Build Status](
    https://travis-ci.org/TopChef/TopChef.svg?branch=master
)](https://travis-ci.org/TopChef/TopChef)

[![Documentation Status](
    https://readthedocs.org/projects/topchef/badge/?version=latest)](
    http://topchef.readthedocs.io/en/latest/?badge=latest)

[![Requirements Status](
https://requires.io/github/TopChef/TopChef/requirements.svg?branch=master
)](
https://requires.io/github/TopChef/TopChef/requirements/?branch=master)

TopChef is an asynchronous task queue that allows posting jobs for services 
defined at runtime. Service contracts are enforced using JSON schema, and 
the functionality is exposed through a REST API. This project solves the 
problem of running and queueing remote procedure calls between computers 
over an HTTP layer.

Please report bugs, feature requests, and other issues to the 
[issue tracker](https://github.com/TopChef/TopChef/issues). For support, 
please open an issue in the issue tracker.

***Running TopChef***

The easiest way to run TopChef is via the
[docker container](https://hub.docker.com/r/topchef/topchef/). To run this, 
install [docker](https://www.docker.com/) and run

```bash
    docker pull topchef/topchef
```

from the command line. This will download the latest build from the 
``master`` branch of this repository. In order to run the container, run

```bash
    docker run -i -t -p <port>:80 topchef/topchef
```

Where ``<port>`` is the port on which you want the container to run. If you 
want to configure the application, pass in the required environment 
variables after an ``-e`` flag. For instance, to set the database URI, run

```bash
    docker run -i -t -p <port>:80 -e DATABASE_URI=<database_uri> topchef/topchef
```

The Docker container runs TopChef via [Apache](https://httpd.apache.org/) 
using [mod_wsgi](https://en.wikipedia.org/wiki/Mod_wsgi). If a database URI 
is not provided, the container will create its own SQLite database inside 
the container.

****The Flask Development Server****

[Flask](http://flask.pocoo.org/) provides a development web server. To run 
this server, clone this repository onto your computer using

```bash
    git clone https://github.com/TopChef/TopChef
```

``cd`` into that directory, and run

```bash
    pip install .
```

This will install the core dependencies. Create a server database using

```bash
    python topchef create-db
```

This will create a test sqlite database in the repository's main directory 
titled ``db.sqlite3``. Finally, run the server using

```bash
    python topchef runserver
```

This will start a development server at ``http://localhost:5000``.

***Running The Tests***

TopChef maintains a unit, integration, and acceptance test suite. In order 
to run the unit tests, clone the repository and run

```bash
    pip install -r requirements.txt
```

In order to install the package dependencies. Finally, run

```bash
    nosetests test/unit --processes=-1 --process-timeout=180 --process-restartworker
```

To run the unit tests on all the cores available on the processor. Make sure
to set a long (about 3 minutes) timeout on tests, as hypothesis can take a 
long time to generate random examples for a test. Some test cases can take 
up to a minute to finish. 


***Maintainers***

* [Michal Kononenko](https://github.com/MichalKononenko) (@michalkononenko)
* [Thomas Alexander](https://github.com/whitewhim2718) (@whitewhim2718)
 
