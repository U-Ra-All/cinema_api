# Cinema API

API service for cinema management written on DRF

## Installation

Python3 must be already installed

```shell
git clone https://github.com/U-Ra-All/cinema_api.git
cd cinema_api
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 manage.py migrate
python3 manage.py runserver # starts Django Server
```

Create a file called .env in the same folder as the settings file.
Make sure to have the following development-specific values in there.
You can find the example in [.env_sample](.env_sample)

```shell
SECRET_KEY = "Your_Super_Secret_Key"
```

You can use the following superuser (or create another one by yourself):

```shell
Login: admin_user@mail.com
Password: 7QancRe2
```

## Get Cinema API project from Docker Hub

```shell
docker pull uraall/docker-cinema-api
```

## Run with Docker

```shell
docker-compose build
docker-compose up
```

## Getting access

- create user via /api/user/register/
- get access token via /api/user/token/

## Features

* JWT authenticated
* Admin panel /admin/
* Documentation is located at /api/doc/swagger/
* Managing orders and tickets
* Creating movies with genres, actors
* Creating cinema halls
* Adding movie sessions
* Filtering movies and movie sessions
