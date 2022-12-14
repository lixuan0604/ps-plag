# =======================下面是所有celery要捕获的任务=============================
import json
import logging
import time

from werkzeug.datastructures import FileStorage

from celery_tasks.main import celery_app
import requests


def change_type(byte):
    if isinstance(byte,bytes):
        return str(byte,encoding="utf-8")
    return json.JSONEncoder.default(byte)


# @celery_app.task(name="sent_text")
# def sent_text(file,file_name,data):
#     logging.info("11111")
#     url = "http://172.16.10.8:8001/ai/batch_generate"
#     payload = {'id': '1'}
#     files = [
#         ('files', (file_name, file,
#                    'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
#     ]
#     headers = {}
#     response = requests.request("POST", url, headers=headers, files=files,data=data)
#     print(response.text)
#     return response.text


@celery_app.task(name="sent_text")
def sent_text(data,url):
    # url = "http://172.16.10.8:8001/ai/batch_generate"
    payload = {'id': '1'}
    # files = [
    #     ('files', (file_name, file,
    #                'application/vnd.openxmlformats-officedocument.wordprocessingml.document'))
    # ]
    # headers = {}
    logging.info("异步执行：开始调用算法")
    logging.info(f"异步执行：调用算法请求体：{data}")
    response = requests.post(url,json=data)
    logging.info("异步执行：调用算法完成")
    logging.info(response.text)
    return response.text
