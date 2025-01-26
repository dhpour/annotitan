# Annotitan
It is a web based Automatic Speech Recognition data verifier by crowd-sourcing app.

## Description

This application is designed for verifing ASR datasets like [Youtube Persian ASR dataset](https://huggingface.co/PerSets/youtube-persian-asr) and [Filimo ASR dataset](https://huggingface.co/PerSets/filimo-persian-asr), but it can also be used for any other similar datasets.

## How to Run

Follow these steps:
- Add a `.env` file with following key/value pairs to the root of the app.
```
SECRET_KEY=A_LONG_STRING _AS_DJANGO_KEY
DB_NAME=YOUR_POSTGRESS_DB_NAME
DB_USER=YOUR_DB_USER
DB_PASS=YOUR_DB_PASS
DB_PORT=YOUR_DB_PORT
DB_HOST=YOUR_DB_SERVICE_NAME in docker-compose.yml (here is 'db')
MEDIA_FOLDER="media/"
MEDIA_VOLUME="/media"
ADMIN_ROUTE="admin/"
EMAIL_HOST=YOUR_EMAIL_HOST
EMAIL_PORT=YOUR_EMAIL_PORT
EMAIL_USER=YOUR_EMAIL_USER
EMAIL_PASS=YOUR_EMAIL_PASS
ALLOWED_HOSTS='["localhost", "127.0.0.1","0.0.0.0", ]'
NGINX_CONF='./nginx/local_nginx.conf:/etc/nginx/conf.d/default.conf:ro'
DEBUG='True'
```
- Put each dataset in a folder in `media` directory in the app root. This dataset folder should consists of archives and metadata file.
- Run the app with `docker-compose.yml`
- Start an interactive shell inside `web` container
    - Migrate Django database models
    - Create django super user
    - In Django shell use `shellutil.py` script to load audio from archives and pair them with metadata in database.
- `Annotitan` is a self-sufficient app that you can run locally or on the web. If you run it on the web and would like to verify the users who register to contribute to annotating your data, you should add your SMTP email account to the environment variables (`.env` file) for the user verification process.
