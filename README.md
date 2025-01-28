# AnnoTitan
It is a web-based Automatic Speech Recognition data verifier that uses a crowd-sourcing model.

## Description

This application is designed for verifing ASR datasets like [Youtube Persian ASR dataset](https://huggingface.co/PerSets/youtube-persian-asr) and [Filimo ASR dataset](https://huggingface.co/PerSets/filimo-persian-asr), but it can also be used for any other similar datasets.

## Start up the app

Follow these steps:
- Add a `.env` file with the following key/value pairs to the root of the app.
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
CSRF_TRUSTED_ORIGINS='[""]'
NGINX_CONF='./nginx/local_nginx.conf:/etc/nginx/conf.d/default.conf:ro'
DEBUG='True'
SPLIT_PREFIX=unvalidated
```
- Put each dataset in a folder in `media` directory at the app root. This dataset folder should consist of archives and metadata file.
    ```
    app_root_directory
    |
    ├───media
    │   └───filimo
    |       ├───unvalidated.csv
    │       └───data
    |           ├───unvalidated_001.tar
    |           |          ...
    |           |          ...
    |           └───unvalidated_033.tar
    ```

- Run the app with `docker-compose.yml`
    ```
    docker compose up -d
    ```

- Start an interactive shell inside `web` container (Django container)

    ```
    docker exec -it <CONTAINER_NAME> /bin/bash
    ```

    - Migrate Django database models

    ```
    python manage.py migrate
    ```
    - Create Django super user
    ```
    python manage.py createsuperuser
    ```

    - Go to localhost/admin and login to admin panel with your superuser user/pass
    - Select `Add` in `Datasets` row
    - Enter `filimo` or `youtube` (based on your dataset) in name and data folder fields. Select current date and time and finally set Added by field and save.
    - Activate dataset by going to `Active dataset` row and select add. From dropdown menu select `filimo` and save.

    - In the Django shell use `shellutil.py` script to load audio from archives and pair them with metadata in the database.
    ```
    python manage.py shell
    ```
    inside shell:
    ```
    >>> from shellutil import load_all_datasets
    >>> load_all_datasets()
    ```
    and wait until all records of csv and audio path added to the db. For checking if everything done correctly, and check if number of records are equal to the dataset.
    ```
    >>> from asrann.models import Record 
    >>> Record.objects.count()
    ```
    - Now go to the app page `localhost`. You should see following page.
    ![alt text](image.png)

## Run locally or on the web
- `AnnoTitan` is a self-sufficient app that you can run locally or on the web. If you run it on the web and would like to verify the users who register to contribute to annotating your data, you should add your SMTP email account to the environment variables (`.env` file) for the user verification process.

## How to use
