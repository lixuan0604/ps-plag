# 如果使用 redis 作为中间人
# broker_url = 'redis://172.16.10.7:6381/0'
from celery import platforms

# backend = 'redis://172.16.10.7:6381/1'
from celery_tasks.base import base_redis


broker_url = base_redis + "/0"

result_backend = base_redis + "/1"

timezone = 'Asia/Shanghai'
task_serializer = 'pickle'

result_serializer = 'pickle'

accept_content = ['pickle', 'json']

worker_prefetch_multiplier = 1
task_acks_late = True
worker_concurrency=2

# 优先级需设置这些参数
# celery_acks_late: True
# worker_prefetch_multiplier = 1
# task_queues = (
#     Queue("celery", Exchange("celery"), routing_key="celery"),
#     Queue("celery_level", Exchange("celery_level"), routing_key="celery_level", queue_arguments={'x-max-priority': 1})
# )