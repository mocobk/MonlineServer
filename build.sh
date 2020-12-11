#!/bin/bash

echo "构建新的镜像"
docker build -t monline-server -f Dockerfile-alpine .

echo "停止正在运行的容器"
docker stop monline-server

echo "删除旧的容器"
docker rm monline-server

echo "创建并启动一个新的容器"
docker run -d --name monline-server -p 5050:5050 monline-server
