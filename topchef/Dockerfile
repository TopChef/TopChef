FROM debian:latest

MAINTAINER Michal Kononenko "michalkononenko@gmail.com"

# Set up the Debian machine
RUN apt-get update && apt-get install -y apache2 \
    libapache2-mod-wsgi \
    build-essential \
    python \
    python-dev \
    python-pip \
 && apt-get clean \
 && apt-get autoremove \
 && rm -rf /var/lib/apt/lists

# Install requirements
COPY ./requirements.txt /var/www/topchef/requirements.txt
RUN pip install -r /var/www/topchef/requirements.txt

# Copy in an apache configuration file
COPY ./apache/topchef.conf /etc/apache2/sites-available/topchef.conf

COPY ./apache/topchef.wsgi /var/www/topchef/topchef.wsgi

RUN a2dissite 000-default.conf
RUN a2ensite topchef.conf

EXPOSE 80

WORKDIR /var/www/topchef

