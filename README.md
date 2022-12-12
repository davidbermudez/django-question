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

    docker build .
    
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

## OAuth Google

https://www.section.io/engineering-education/django-google-oauth/

Install django-allauth

    pip install django-allauth

Add to INSTALLED_APPS in your settings.py:

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',

Add to bottom in your settings.py:

    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'allauth.account.auth_backends.AuthenticationBackend'
    ]

Then set Google as the OAuth provider under SOCIALACCOUNT_PROVIDERS configurations.

    SOCIALACCOUNT_PROVIDERS = {
        'google': {
            'SCOPE': [
                'profile',
                'email',
            ],
            'AUTH_PARAMS': {
                'access_type': 'online',
            }
        }
    }

    SITE_ID = 2

    LOGIN_REDIRECT_URL = '/'
    LOGOUT_REDIRECT_URL = '/'