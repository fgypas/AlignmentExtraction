FROM ubuntu:16.04

RUN apt-get update && \
  apt-get install --yes \
    make \
    g++ \
    zlib1g-dev \
    libbz2-dev \
    wget \
    perl && \
  cd /tmp && \
  wget http://research-pub.gene.com/gmap/src/gmap-gsnap-2018-03-25.tar.gz && \
  tar xzf gmap-gsnap-*.tar.gz && \
  cd /tmp/gmap-* && \
  ./configure --prefix=/usr/local --with-simd-level=sse42 && \
  make && \
  make check && \
  make install && \
  rm -rf /tmp/gmap-* && \
  apt-get remove --purge --yes \
    make \
    g++ \
    wget && \
  apt-get autoremove --purge --yes
