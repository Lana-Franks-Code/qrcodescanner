# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

# Inside Container
# make a new folder inside container
WORKDIR /pythonProject14

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
