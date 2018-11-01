FROM python:3.6-slim-stretch

MAINTAINER Ian Allison <iana@pims.math.ca>

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libcurl4-openssl-dev \
      libssl-dev \
      build-essential \
      && \
    apt-get purge && apt-get clean

RUN pip3 install --no-cache-dir tornado ruamel.yaml oauthlib psycopg2-binary pycurl sqlalchemy

RUN mkdir -p /srv/hubsharder
ADD db.py /srv/hubsharder/db.py
ADD sharder.py /srv/hubsharder/sharder.py
ADD request-sharder.py /srv/hubsharder/request-sharder.py
ADD wait-for-it.sh /srv/hubsharder/wait-for-it.sh
RUN chmod +x /srv/hubsharder/wait-for-it.sh
ADD templates /srv/hubsharder/templates

WORKDIR /srv/hubsharder

ENTRYPOINT ["/srv/hubsharder/wait-for-it.sh", "db:5432", "--", "python3.6", "/srv/hubsharder/request-sharder.py", "--postgres"]
