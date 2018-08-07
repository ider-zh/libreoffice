FROM ubuntu:18.04

MAINTAINER ider <ider@knogen.cn>

RUN sed -e 's/security.ubuntu/mirrors.aliyun/g' \
    -e 's/archive.ubuntu/mirrors.aliyun/g' \
    -i /etc/apt/sources.list && \
    apt update && \
    apt install -y \
    git \
    curl \
    libx11-6 \
    libxinerama-dev  \
    ghostscript             \
    libxinerama1            \
    libdbus-glib-1-2        \
    libcairo2               \
    libcups2                \
    libgl1-mesa-dri         \
    libgl1-mesa-glx         \
    libsm6        \
    openjdk-8-jre \
    python3 \
    python3-pip \
    ttf-wqy-zenhei \
    fonts-arphic-ukai \
    fonts-arphic-uming && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* && \
    pip3 install flask

RUN mkdir /tmp/lo \
  && cd /tmp/lo \
  && curl -L -k https://download.documentfoundation.org/libreoffice/stable/6.0.6/deb/x86_64/LibreOffice_6.0.6_Linux_x86-64_deb.tar.gz | tar xz --strip-components=1 \
  && cd DEBS \
  && dpkg -i *.deb \
  && rm -fr /tmp/lo

WORKDIR /root
EXPOSE 5000

RUN git clone https://github.com/ider-zh/libreoffice.git

CMD python3 libreoffice/run.py
