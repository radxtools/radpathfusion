# set base image (host OS)
FROM python:3.8

RUN pip install numpy

RUN apt-get update && apt-get install -y python3-opencv

WORKDIR /notebooks

# copy the dependencies file to the working directory
COPY requirements.txt .
COPY notebooks ./notebooks

# install dpendencies
RUN PIP_INSTALL="python -m pip install --upgrade --no-cache-dir --retries 10 --timeout 60" && \
    $PIP_INSTALL install -r requirements.txt

# # command to run on container start
CMD [ "jupyter", "notebook", "--port=3000", "--no-browser", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=" ]

EXPOSE 3000