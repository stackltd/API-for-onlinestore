FROM python:latest

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN python setup.py sdist
RUN pip install diploma-frontend-0.6.tar.gz
RUN pip install --upgrade pip "poetry==2.2.1"
RUN poetry config virtualenvs.create false --local
COPY poetry.lock pyproject.toml ./
RUN poetry install --no-root

COPY onlinestore/ .

RUN python manage.py collectstatic --noinput
