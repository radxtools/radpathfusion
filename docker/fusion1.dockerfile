# set base image (host OS)
FROM python:3.8

RUN pip install numpy

RUN apt-get update && apt-get install -y python3-opencv

WORKDIR /

CMD ["/usr/bin/bash"]