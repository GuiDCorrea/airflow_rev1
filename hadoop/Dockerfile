FROM apache/hadoop-runner
ARG HADOOP_URL=https://www.apache.org/dyn/mirrors/mirrors.cgi?action=download&filename=hadoop/common/hadoop-2.9.0/hadoop-2.9.0.tar.gz
WORKDIR /opt
RUN sudo rm -rf /opt/hadoop && wget --no-check-certificate https://dlcdn.apache.org/hadoop/common/hadoop-3.3.6/hadoop-3.3.6.tar.gz -O /tmp/hadoop.tar.gz && \
    tar zxf /tmp/hadoop.tar.gz -C /tmp && \
    mv /tmp/hadoop-3.3.6 /opt/hadoop && \
    rm -rf /opt/hadoop/share/doc
ADD log4j.properties /opt/hadoop/etc/hadoop/log4j.properties
RUN sudo chown -R hadoop:users /opt/hadoop/etc/hadoop/*