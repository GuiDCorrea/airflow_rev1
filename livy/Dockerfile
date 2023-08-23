FROM openjdk:8-jdk

RUN apt-get update && apt-get install -y curl && \
    curl -Lo livy.zip https://archive.apache.org/dist/incubator/livy/0.7.0-incubating/apache-livy-0.7.0-incubating-bin.zip && \
    unzip livy.zip && \
    mv apache-livy-0.7.0-incubating-bin /opt/livy && \
    rm livy.zip

ENV LIVY_HOME=/opt/livycd
ENV PATH=$PATH:$LIVY_HOME/bin

EXPOSE 8998

CMD ["tail", "-f", "/dev/null"]
