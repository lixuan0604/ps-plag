import celery as celery
from celery_tasks.base import base_redis
from celery import platforms

# 利用导入的 Celery 创建对象
celery_app = celery.Celery('celery', broker=base_redis + '/0', backend=base_redis + '/1')

# 配置config文件
celery_app.config_from_object('celery_tasks.config')

# 让celery_app自动捕获目标地址下的任务(捕获tasks)
# celery_app.autodiscover_tasks(['celery_tasks.message', 'celery_tasks.email'])

celery_app.autodiscover_tasks(['celery_tasks.text'])
