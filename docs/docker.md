The below documentation explains how to create and run docker containers.

# Prerequisites:
Software Installation
1. Docker

# Build

This command will create the image using the file `docker/notebook.dockerfile` and will name the name image `notebook`

```sh
docker build -f docker/fusion1.dockerfile -t notebook .
docker tag notebook radxtools/radpathfusion-examples
```

# Run

This command will create a container called `topology-radiomics-examples` that will start the image `notebook`

```sh
docker rm radpathfusion-examples
docker run -d -p 3000:3000 --name radpathfusion-examples notebook
```

# Compose

```sh
cd docker
docker-compose up
```

# Pushing to Docker Repo

The docker repo can be found [here](https://hub.docker.com/repository/docker/radxtools/topology-radiomics-examples)

```sh
docker login
>>username
>>password
docker tag notebook radxtools/radpathfusion-examples
docker push radxtools/radpathfusion-examples:latest
```

# Debugging the docker build

If the app is already running, we can open a shell using the following command.

```
docker exec -it radpathfusion-examples /bin/bash
```

This will create a shell. You can use this shell to troubleshoot other things like installed packages, file system paths and etc...