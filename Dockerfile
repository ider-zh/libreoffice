FROM ubuntu:18.04

RUN sed -e 's/security.ubuntu/mirrors.aliyun/g' \
    -e 's/archive.ubuntu/mirrors.aliyun/g' \
    -i /etc/apt/sources.list && \
    apt update && \
    apt install -y \
    git \
    ttf-wqy-zenhei \
    fonts-arphic-ukai \
    fonts-arphic-uming && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ADD test/DEBS /tmp/DEBS

RUN cd /tmp/DEBS && \
   dpkg -i *.deb && \
   rm -fr /tmp/DEBS
