FROM python:3.7
LABEL maintainer="mailmzb@163.com"
ENV TZ="Asia/Shanghai"
ENV FLASK_ENV="production"
WORKDIR /usr/src
RUN pip install uwsgi -i https://pypi.tuna.tsinghua.edu.cn/simple
# 以下两句在 COPY . . 之前主要是为了利用 build 缓存，避免每次都重装 python 依赖
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt --timeout 600

COPY . .

CMD uwsgi --ini uwsgi_config.ini --cache-blocksize 0