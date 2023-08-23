
FROM ubuntu:latest

RUN apt-get update && apt-get install -y \
    openjdk-8-jdk \
    wget \
    tar


ENV JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64
ENV HIVE_HOME=/opt/hive
ENV PATH=$PATH:$HIVE_HOME/bin

RUN wget https://downloads.apache.org/hive/hive-3.1.2/apache-hive-3.1.2-bin.tar.gz
RUN tar -xzvf apache-hive-3.1.2-bin.tar.gz -C /opt/
RUN mv /opt/apache-hive-3.1.2-bin $HIVE_HOME
RUN rm apache-hive-3.1.2-bin.tar.gz


EXPOSE 10000


CMD ["tail", "-f", "/dev/null"]