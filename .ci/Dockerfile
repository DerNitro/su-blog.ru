FROM python:3.10-alpine

RUN apk --no-cache add py3-pip yaml-dev gcc python3-dev linux-headers libc-dev

COPY requirements.txt /requirements.txt

RUN /usr/bin/pip3 install --no-cache-dir --upgrade pip \
    && /usr/bin/pip3 install --no-cache-dir --upgrade -r /requirements.txt \
    && rm -rf /tmp/.cache

VOLUME [ "/data" ] 
WORKDIR /data

ENTRYPOINT [ "nikola" ]
