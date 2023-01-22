# Get Started

## Clone

Clone repository:

    git clone https://github.com/davidbermudez/django-question.git


## Create files configuration

### .env

	nano .env

Content:

	POSTGRES_DB=questions
	POSTGRES_USER=
	POSTGRES_PASSWORD=
	
### secret.py

	nano app/secret.py

Content:

	SECRET_KEY = ''
	POSTGRES_DB = 'questions'
	POSTGRES_USER = ''
	POSTGRES_PASSWORD = ''
	POSTGRES_HOST = 'db' (or IP server PostgreSQL)	

## Launch Containers

### Go to directory django-question

    cd django-question


### Launch containers:

First time:
    
    docker-compose build

    
Init container:

    docker-compose up

Access to container in ejecution:

	docker exec -it django-question_web_1 bash


## Install dependencies

pip install -r requirements.txt

(reverse => python -m pip freeze > requirements.txt)

## Configure database (in server local)

### Create migration

    python manage.py migrate

### Create superuser 

    python manage.py createsuperuser

