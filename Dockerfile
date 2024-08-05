# syntax=docker/dockerfile:1
FROM python:3
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /code
COPY requirements.txt /code/
RUN pip install -r requirements.txt
COPY anno/ /code/anno
COPY asrann/ /code/asrann
COPY manage.py /code/manage.py
COPY requirements.txt /code/requirements.txt
COPY .gitignore /code/.gitignore
COPY README.md /code/README.md
COPY docker-compose.yml /code/docker-compose.yml
COPY Dockerfile /code/Dockerfile
COPY .env /code/.env
COPY shellutil.py /code/shellutil.py
COPY static/ /code/static