FROM apache/airflow:3.0.3

COPY requirements.txt /

USER root
RUN apt-get update && \
    apt-get install -y curl gnupg2 software-properties-common && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

USER airflow

RUN pip install --no-cache-dir -r /requirements.txt