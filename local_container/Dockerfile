FROM apache/airflow:3.0.3

COPY requirements.txt /

USER root
RUN apt-get update && \
    apt-get install -y curl gnupg2 software-properties-common && \
    apt-get install -y openjdk-17-jdk && \
    apt-get clean

RUN mkdir -p /opt/airflow/jars && \
    curl -L -o /opt/airflow/jars/hadoop-aws-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-aws/3.3.4/hadoop-aws-3.3.4.jar && \
    curl -L -o /opt/airflow/jars/aws-java-sdk-bundle-1.12.262.jar \
    https://repo1.maven.org/maven2/com/amazonaws/aws-java-sdk-bundle/1.12.262/aws-java-sdk-bundle-1.12.262.jar && \
    curl -L -o /opt/airflow/jars/hadoop-common-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-common/3.3.4/hadoop-common-3.3.4.jar && \
    curl -L -o /opt/airflow/jars/hadoop-client-api-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-api/3.3.4/hadoop-client-api-3.3.4.jar && \
    curl -L -o /opt/airflow/jars/hadoop-client-runtime-3.3.4.jar \
    https://repo1.maven.org/maven2/org/apache/hadoop/hadoop-client-runtime/3.3.4/hadoop-client-runtime-3.3.4.jar

ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64
ENV PATH="$JAVA_HOME/bin:$PATH"

USER airflow

RUN pip install --no-cache-dir -r /requirements.txt