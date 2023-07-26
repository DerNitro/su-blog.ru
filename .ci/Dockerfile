FROM python:3.10-alpine

RUN apk --no-cache add py3-pip yaml-dev gcc python3-dev linux-headers libc-dev aspell aspell-en aspell-ru
COPY requirements.txt /requirements.txt

RUN adduser -D ci -u 9999
USER ci

RUN /usr/bin/pip3 install --no-cache-dir --upgrade --no-warn-script-location pip \
    && /usr/bin/pip3 install --no-cache-dir --upgrade --no-warn-script-location -r /requirements.txt \
    && rm -rf /tmp/.cache

VOLUME [ "/data" ] 
WORKDIR /data

ENV PATH="/home/ci/.local/bin:${PATH}"

ENTRYPOINT [ "nikola" ]
