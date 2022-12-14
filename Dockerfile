FROM python:3.7

#RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list

WORKDIR /app

ENV TZ=Asia/Shanghai \
    DEBIAN_FRONTEND=noninteractive

RUN ln -fs /usr/share/zoneinfo/${TZ} /etc/localtime \
    && echo ${TZ} > /etc/timezone \
    && dpkg-reconfigure --frontend noninteractive tzdata \
    && rm -rf /var/lib/apt/lists/*

RUN apt update


RUN apt install -y libreoffice

COPY requirements.txt .

RUN pip install -U pip -i https://pypi.mirrors.ustc.edu.cn/simple/
RUN pip install -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/


EXPOSE 8000