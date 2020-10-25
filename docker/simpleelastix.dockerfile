# set base image (host OS)
FROM python:3.8

RUN pip install numpy

RUN apt-get update && apt-get install -y cmake \
    build-essential \
    git
# r-base \
# r-base-dev \
# ruby \
# ruby-dev \
# tcl \
# tcl-dev \
# tk \
# tk-dev

WORKDIR /

RUN git clone https://github.com/SuperElastix/SimpleElastix \
    && mkdir build \
    && cd build \
    && cmake ../SimpleElastix/SuperBuild \
    && make -j2

CMD ["/bin/bash"]