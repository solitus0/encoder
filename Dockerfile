FROM python:3.10-alpine

RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install --upgrade pip setuptools supervisor && \
    pip3 install --ignore-installed distlib pipenv

RUN apk add --no-cache git bash zsh vim curl wget make yarn py3-pip && rm -rf /var/cache/apk/* /tmp/*

WORKDIR /var/www/api

COPY . /var/www/api

RUN --mount=type=cache,target=/root/.cache/pip \
    pipenv install .

ENTRYPOINT ["/bin/sh", "-c"]

CMD ["while true; do sleep 10; done"]
