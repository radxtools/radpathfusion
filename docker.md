```
docker build -f docker/temp.dockerfile -t fusion .
```

```
docker rm fusion
docker run --name fusion -i fusion
```

```
docker exec -it fusion bash
```

----

```
docker build -f docker/fusion1.dockerfile -t rad .
```

```
docker rm rad
docker run --name rad -i rad
```

```
docker exec -it f bash
```