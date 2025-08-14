# build python package
FROM python:3.11-slim as build-python
WORKDIR /src
COPY . /src
RUN python3 /src/setup.py sdist

# build application image
FROM logilab/cubicweb-base:cw4-postgres16-python3.11

WORKDIR /src
USER root

RUN pip install -U pip
COPY ./docker/requirements.txt /src/docker/requirements.txt

COPY ./docker/pyramid.ini.j2 /pyramid.ini.j2
COPY --from=build-python /src/dist/cubicweb-intranet-*.tar.gz /src/cubicweb-intranet.tar.gz
RUN pip install cubicweb-intranet.tar.gz -r /src/docker/requirements.txt
RUN chown -R cubicweb: /etc/cubicweb.d

# enable stats socket used by uwsgi prometheus exporter
RUN echo "memory-report = true" >> /etc/uwsgi/uwsgi.ini
RUN echo "stats = 127.0.0.1:8001" >> /etc/uwsgi/uwsgi.ini

USER cubicweb
ENV CUBE=intranet
RUN cubicweb-ctl create intranet instance --automatic --no-db-create
