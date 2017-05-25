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

***Introduction***

TopChef is a job queue designed for online experiment design involving a
control computer running experimental equipment, and a remote computing
service. The queueing and recording is handled by an HTTP REST API. The
service contracts between the server are handled using 
[JSON Schema](http://json-schema.org/).

***Project Management***
This project is being managed on [Asana](
    https://app.asana.com/0/349544982046885/349547942248954).

***Directory Structure***

All documentation is generated and kept in the ``docs`` directory. Each 
client is given a directory. The topchef REST API is kept in the ``topchef``
directory. A client for an NMR spectrometer is kept in the ``nmr_client``
directory. The client was designed to run on the Python interpreter in 
TOPSPIN 2.1. A computing client is located in the ``topchef_client``
directory. Each package has its own ``setup.py`` file, allowing independent
installation with distutils. Each package also has its own ``requirements.txt``
file. 

**Installing the Server**

1. Clone this repository using

```bash
    git clone git@github.com:whitewhim2718/TopChef.git
```

2. If installing the server, cd into the ``topchef`` directory, and install
   the required dependencies using

```bash
    pip install -r requirements.txt
```

3. Install the server by ``cd``'ing into the ``topchef`` directory and
    running.

```bash
    python setup.py install
```

4. Start the development server by running
```bash
    python topchef
```
   The ``__main__.py`` file in the ``topchef`` directory will start a
   development server at ``localhost:5000``.

***Installing the Client***

Installing the client is similar to that of the server, except instead of
``cd``'ing into ``topchef``, ``cd`` into ``topchef_client``. Then run 
``pip install -r requirements.txt`` and ``python setup.py install``.

***Running the Unit Tests***

Each package in this repository has a ``tests`` directory. The 
[py.test](http://doc.pytest.org/en/latest/) library was used to design the
unit tests. In order to run these tests, run ``py.test`` from one of the 
package directories. The test runner will discover all tests in the ``tests``
directory and run them. To run all tests from a specific file, pass the
filename as an argument to ``py.test``.

***Maintainers***

* [Michal Kononenko](https://github.com/MichalKononenko) (@michalkononenko)
* [Thomas Alexander](https://github.com/whitewhim2718) (@whitewhim2718)
 
