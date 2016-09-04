# Dockerfile to set up the TopChef server, exposing port 80 in the container

# Start with the latest minimum debian distribution
FROM debian:latest

# Define API metadata
MAINTAINER Michal Kononenko "@MichalKononenko"

ENV VERSION="1.0-rc1"
ENV DESCRIPTION="Asynchronous job queue for running services"

ENV SOURCE_REPOSITORY="https://github.com/TopChef/TopChef.git" 

ENV HOSTNAME = "0.0.0.0"
ENV PORT = "80"
ENV THREADS = 20
ENV DEBUG = "FALSE"


ENV BASE_DIRECTORY = "/var/www/topchef"
ENV SCHEMA_DIRECTORY = "/var/www/topchef/schemas"

ENV LOGFILE = "/var/www/topchef/topchef.log"

ENV DATABASE_URI = "sqlite:////var/www/topchef/db.sqlite3"

EXPOSE 80

# Set up the Debian machine
RUN apt-get update
RUN apt-get -y upgrade

RUN apt-get install -y apt-utils \
    apache2 \
    libapache2-mod-wsgi \
    python \
    python-dev \
    python-pip \
    git \
 && apt-get clean \
 && apt-get autoremove \
 && rm -rf /var/lib/apt/lists

#Clone the repo into this directory

RUN git clone ${SOURCE_REPOSITORY} /opt/source

WORKDIR /opt/source/topchef/

RUN pip install -r requirements.txt

RUN python setup.py install

# Copy in an apache configuration file
COPY ./apache/topchef.conf /etc/apache2/sites-available/topchef.conf

# Copy the WSGI file
COPY ./apache/topchef.wsgi /var/www/topchef/topchef.wsgi

WORKDIR /var/www/topchef

RUN a2dissite 000-default.conf
RUN a2ensite topchef.conf

# Now that the source repository has been copied, remove the 
# cloned Git repository
RUN rm -r /opt/source

# Git and Python headers aren't required anymore either
RUN apt-get remove -y --purge python-dev \
    python-pip \
    git \
 && apt-get clean \
 && apt-get autoremove -y

ENTRYPOINT /usr/sbin/apache2ctl -D FOREGROUND

