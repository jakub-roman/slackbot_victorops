FROM python:3.7-alpine

RUN apk add musl-dev gcc

WORKDIR /app

ADD requirements.txt .

RUN pip install -r requirements.txt

ADD src/ .

ENTRYPOINT [ "/bin/sh" ]
