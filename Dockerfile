FROM python:3.10-alpine

RUN apk --no-cache add ffmpeg postgresql-dev musl-dev libffi-dev gcc

WORKDIR /filmflask
COPY . .
RUN pip install -r requirements.txt

CMD FLASK_APP=src/app.py flask run --host 0.0.0.0