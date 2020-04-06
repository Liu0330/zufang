# import pymysql
#
# pymysql.install_as_MySQLdb((1, 4, 2, "final", 0))
import os

import celery

from celery.schedules import crontab
from django.conf import settings
import pymysql
pymysql.install_as_MySQLdb()

# ����Django��Ŀ����
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'zufang.settings')

# ����Celery����ָ��ģ��������Ϣ������Ϣ���У��ͳ־û���ʽ
app = celery.Celery(
    'zufang',
    # broker='redis://120.77.222.217:6379/1',
    broker='amqp://luohao:1qaz2wsx@120.77.222.217:5672/zufangwang_vhost',
    # backend='redis://120.77.222.217:6379/2'
    backend='django-db'
)

# ֱ��ͨ�������޸�Celery�������
app.conf.update(
    timezone=settings.TIME_ZONE,
    enable_utc=True,
    # ��ʱ���񣨼ƻ������൱������Ϣ��������
    # ���ֻ��������û����������ô��Ϣ�ͻ�����Ϣ�����л�ѹ
    # ����ʵ�ʲ�����Ŀ��ʱ�������ߡ������ߡ���Ϣ���п��ܶ��ǲ�ͬ�ڵ�
    # celery -A zufang beat -l debug ---> ��Ϣ��������
    # celery -A zufang worker -l debug ---> ��Ϣ��������
    beat_schedule={
        'task1': {
            'task': 'common.tasks.remove_expired_record',
            'schedule': crontab('*', '*', '*', '*', '*'),
            'args': ()
        },
    },
)
# # �������ļ��ж�ȡCelery�������
# app.config_from_object('django.conf:settings')
# �Զ���ָ����Ӧ���з��������첽����/��ʱ����
app.autodiscover_tasks(('common', ))
# # �Զ���ע���Ӧ���з��������첽����/��ʱ����
# app.autodiscover_tasks(settings.INSTALLED_APPS)
