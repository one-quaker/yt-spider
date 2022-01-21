# yt-spider

1. install docker [mac](https://docs.docker.com/desktop/mac/install/) / [windows](https://docs.docker.com/desktop/windows/install/) / [linux](https://docs.docker.com/engine/install/ubuntu/)
2. run docker container `docker-compose up -d yt_spider`
3. run `docker ps` and find CONTAINER ID (**3deb3027a59e** in my case)
```
CONTAINER ID   IMAGE                        COMMAND                  CREATED          STATUS          PORTS     NAMES
3deb3027a59e   onepycoder/yt-spider:1.0.0   "/bin/sh -c 'while t…"   16 seconds ago   Up 14 seconds             yt-spider_yt_spider_1
```
4. run shell inside container `docker exec -it 3deb3027a59e /bin/bash`
5. run spider `python youtube.py`
