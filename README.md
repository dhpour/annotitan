# Annotitan
Automatic Speech Recognition data verifier by crowd-sourcing. It is a web based ASR data verifier.

## Description

It is designed for verifiing ASR dataset like [Youtube Persian ASR dataset](https://huggingface.co/PerSets/youtube-persian-asr) and [Filimo ASR dataset](https://huggingface.co/PerSets/filimo-persian-asr) but it can be used for any similar dataset if you can make it to be in compliance with this app structure in handling audio and metadata.

## How to Run

After creating and running the Docker containers, follow these steps:
- Do not forget that add .env file with following structure and variable to the root of the app.
- Put each dataset in a folder in media directory in the app root. This dataset folder should consists of archives and metadata file.
- Migrate Django database models
- Create django super user
- In Django shell use `shellutil.py` script to load audio from archives and pair them with metadata in database.
- Annotitan is a self-contained app that you can run locally or on the web. If you run it on web and you like to verify those who register you can add your smpt email account in the environemtn variables as expecte but if you do not need this feature you can comment/remove these lines in `anno/settings.py`:
```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_USE_TLS = True
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = os.getenv('EMAIL_PORT')
EMAIL_HOST_USER = os.getenv('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASS')
```