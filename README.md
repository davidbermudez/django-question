# Get Started

## Clone

Clone repository:


    git clone https://github.com/davidbermudez/django-question.git


## Launch Containers

Go to directory django-question


    cd django-question


Create file app/secret.py
This file must contain the SECRET_KEY variable to prevent it from being shared to the repository


    nano app/secret.py


Launch containers


    docker-compose up

## Create superuser

    python manage.py createsuperuser


## Install bulma css

Install the python package django-bulma from pip

    pip install django-bulma

Add to INSTALLED_APPS in your settings.py:

    'bulma',


Create user test
John
zFY8PmQDHmiyrBB


https://developer.mozilla.org/es/docs/Learn/Server-side/Django/Authentication