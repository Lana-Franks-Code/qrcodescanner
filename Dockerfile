# syntax=docker/dockerfile:1

FROM python:3.8-slim-buster

WORKDIR /pythonProject14

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN apt-get update && apt-get install libzbar0 -y && pip install pyzbar && apt-get install v4l-utils

COPY . .

EXPOSE 5000

ENV FLASK_APP=main.py

CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0"]
