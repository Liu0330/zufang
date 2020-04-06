# import pymysql
#
# pymysql.install_as_MySQLdb((1, 4, 2, "final", 0))
import os

import celery

from celery.schedules import crontab
from django.conf import settings
import pymysql
pymysql.install_as_MySQLdb()

# 加载Django项目配置
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zufang.settings')

# 创建Celery对象，指定模块名、消息代理（消息队列）和持久化方式
app = celery.Celery(
    'zufang',
    # broker='redis://120.77.222.217:6379/1',
    broker='amqp://luohao:1qaz2wsx@120.77.222.217:5672/zufangwang_vhost',
    # backend='redis://120.77.222.217:6379/2'
    backend='django-db'
)

# 直接通过代码修改Celery相关配置
app.conf.update(
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    # 定时任务（计划任务）相当于是消息的生产者
    # 如果只有生产者没有消费者那么消息就会在消息队列中积压
    # 将来实际部署项目的时候生产者、消费者、消息队列可能都是不同节点
    # celery -A zufang beat -l debug ---> 消息的生产者
    # celery -A zufang worker -l debug ---> 消息的消费者
    beat_schedule={
        'task1': {
            'task': 'common.tasks.remove_expired_record',
            'schedule': crontab('*', '*', '*', '*', '*'),
            'args': ()
        },
    },
)
# # 从配置文件中读取Celery相关配置
# app.config_from_object('django.conf:settings')
# 自动从指定的应用中发现任务（异步任务/定时任务）
app.autodiscover_tasks(('common', ))
# # 自动从注册的应用中发现任务（异步任务/定时任务）
# app.autodiscover_tasks(settings.INSTALLED_APPS)
