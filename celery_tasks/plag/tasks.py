

# =======================下面是所有celery要捕获的任务=============================

import time

from celery_tasks.main import celery_app


@celery_app.task(name="sent_plag")
def sent_plag(x, y,tim):
    time.sleep(tim)
    return x + y
