# AnnoTitan
It is a web-based Automatic Speech Recognition data verifier that uses a crowd-sourcing model.

## Description

This application is designed for verifing ASR datasets like [Youtube Persian ASR dataset](https://huggingface.co/PerSets/youtube-persian-asr) and [Filimo ASR dataset](https://huggingface.co/PerSets/filimo-persian-asr), but it can also be used for any other similar datasets.

## Start the app

Follow these steps:
- Add a `.env` file with the following key/value pairs to the root of the app.
```
SECRET_KEY=A_LONG_STRING_AS_DJANGO_KEY
DB_NAME=YOUR_POSTGRESS_DB_NAME
DB_USER=YOUR_DB_USER
DB_PASS=YOUR_DB_PASS
DB_PORT=YOUR_DB_PORT
DB_HOST=YOUR_DB_SERVICE_NAME in docker-compose.yml (here is 'db')
MEDIA_FOLDER="media/"
MEDIA_VOLUME="/media"
ADMIN_ROUTE="admin/"
#EMAIL_HOST=YOUR_EMAIL_HOST
#EMAIL_PORT=YOUR_EMAIL_PORT
#EMAIL_USER=YOUR_EMAIL_USER
#EMAIL_PASS=YOUR_EMAIL_PASS
USE_EMAIL_VERIFICATION='False'
ALLOWED_HOSTS='["localhost", "127.0.0.1","0.0.0.0", ]'
CSRF_TRUSTED_ORIGINS='[""]'
NGINX_CONF='./nginx/local_nginx.conf:/etc/nginx/conf.d/default.conf:ro'
DEBUG='True'
SPLIT_PREFIX=unvalidated
SCORE_THRESHOLD=2
```
- Place each dataset in a folder within the `media` directory at the app's root. This dataset folder should contain archives (in data folder) and a metadata file.
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

    - Migrate Django database models (inside the interactive shell)

    ```
    python manage.py migrate
    ```
    - Create Django super user (inside the interactive shell)
    ```
    python manage.py createsuperuser
    ```

    - Go to `localhost/admin` and log in to admin panel with your superuser credentials.
    - Select `Add` in `Datasets` row
    - Enter `filimo` or `youtube` (based on your dataset) in the name and data folder fields. Select the current date and time, set the "Added by" field, and save.
    - Activate the dataset by going to the `Active dataset` row and selecting `Add`. From dropdown menu, select `filimo` and save.

    - In the Django shell use `shellutil.py` script to load audio from archives and pair them with metadata in the database.
    ```
    python manage.py shell
    ```
    inside the Django shell:
    ```
    >>> from shellutil import load_all_datasets
    >>> load_all_datasets()
    ```
    Wait until all records of csv and audio paths are added to the database. To check if everything is done correctly, the number of records should equal the dataset size:

    ```
    >>> from asrann.models import Record 
    >>> Record.objects.count()
    ```
    - Go to the app page at `localhost`. You should see following page.

    ![alt text](image.png)

    - Now for two final steps: go to `localhost/admin`, log in and navigate to your user record page, find `user_tested` and check it, then find `score weight` field and increase it to 2, then save.
    - Now start annotating at least 10 records. This will create enough ground truth records for the Test Phase (`تست برچسب‌زنی`) for other regular users. If you do not make these ground truth records, there wll be none for the Test Phase, and the regular users will see nothing when they click on `تست برچسب زنی`.

## Run locally or on the web
`AnnoTitan` is a self-sufficient app that you can run locally or on the web. If you run it on the web, you will want to verify the users who register to contribute to annotating your data. To do so, ensure that `USE_EMAIL_VERIFICATION` is set to True in the `.env` file, and then add your SMTP email account to the `.env` file for the user verification process (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASS`).

If you run it locally you can set `USE_EMAIL_VERIFICATION` to False. Delete other fields related to email in `.env` file (`EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_USER`, `EMAIL_PASS`).

## SCORE_THRESHOLD and score_weight
SCRE_THRESHOLD is the threshold that defined in the `.env` file and any record's score  must meet this to be considered an annotaed record. 

score_weight is the score that each user adds to the score of each record they vote on. By default, each user has a score_weight of 1, but it can be changed by the superuser.

For SCORE_THRESHOLD of let say 2, records must reach 2 or -2 to considered annotated, meaning each record needs at least two votes with a score_weight of 1 or one vote with a score_weight of 2.

For simplicity and faster annotating, you can set `SCORE_THRESHOLD` to 1, so each record becomes annotated with just one vote.

## How to use
Each user must pass the Test Phase (unless, of course, the superuser, whose `user_tested` field is set to True beforehand).

![alt text](image-1.png)
After passing 10 tests, the real Annotation Phase begins.

![alt text](image-2.png)

The `راهنما` menu shows instructions on how and what to `accept` or `reject` in records. It also displays keyword shortcuts for fast annotating.

![alt text](image-3.png)

The `فعالیت شما` menu shows all your previous annotations, and you can review and change them if needed.

![alt text](image-4.png)

The `گزارش کاربران` shows each user's number of votes. The superuser sees all users but the admin only sees activity from other admins and regular users. This option limited to superusers and admins.

![alt text](image-5.png)

The `گزارش` shows a summary of all records, annotations and total weights for each record. It also displays a list of votes and their scores. This option limited to superusers and admins.

![alt text](image-6.png)