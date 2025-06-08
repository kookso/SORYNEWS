# postgres/Dockerfile
FROM postgres:15

RUN apt-get update && \
    apt-get install -y postgresql-server-dev-15 git make gcc && \
    git clone --branch v0.5.0 https://github.com/pgvector/pgvector.git && \
    cd pgvector && make && make install
