FROM python:3.10-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive
RUN apt update && apt install -y hunspell hunspell-en-us hunspell-ru && rm -rf /var/lib/apt/lists/*

COPY requirements.txt /requirements.txt
RUN /usr/local/bin/pip3 install --no-cache-dir --break-system-packages --upgrade --no-warn-script-location -r /requirements.txt \
    && rm -rf /tmp/.cache

ARG UID
RUN adduser --system --disabled-password --uid $UID ci
USER ci

VOLUME [ "/data" ] 
WORKDIR /data

ENV PATH="/home/ci/.local/bin:${PATH}"

ENTRYPOINT [ "nikola" ]
