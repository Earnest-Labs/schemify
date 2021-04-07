FROM python:3.7-alpine3.10

ARG PACKAGES="postgresql-libs"
ARG BUILD_PACKAGES="gcc musl-dev postgresql-dev"

COPY . /usr/src/app
WORKDIR /usr/src/app

RUN apk update && apk add $PACKAGES && apk add --virtual .build-deps $BUILD_PACKAGES \
    && python setup.py install \
    && apk --purge del .build-deps