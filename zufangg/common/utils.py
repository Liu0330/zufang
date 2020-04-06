"""
项目常用工具函数
"""
import json
import random
from functools import wraps, partial

from hashlib import md5
from io import BytesIO

import qrcode
import requests
from PIL.Image import Image
from qiniu import Auth, put_file, put_stream

from common.consts import EXECUTOR
from zufang import app


def get_ip_address(request):
    """获得请求的IP地址"""
    ip = request.META.get('HTTP_X_FORWARDED_FOR', None)
    return ip or request.META['REMOTE_ADDR']


def to_md5_hex(origin_str):
    """生成MD5摘要"""
    return md5(origin_str.encode('utf-8')).hexdigest()


def gen_mobile_code(length=6):
    """生成指定长度的手机验证码"""
    return ''.join(random.choices('0123456789', k=length))


def gen_captcha_text(length=4):
    """生成指定长度的图片验证码文字"""
    return ''.join(random.choices(
        '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        k=length)
    )


def make_thumbnail(image_file, path, size, keep=True):
    """生成缩略图"""
    image = Image.open(image_file)
    origin_width, origin_height = image.size
    if keep:
        target_width, target_height = size
        w_rate, h_rate = target_width / origin_width, target_height / origin_height
        rate = w_rate if w_rate < h_rate else h_rate
        width, height = int(origin_width * rate), int(origin_height * rate)
    else:
        width, height = size
    image.thumbnail((width, height))
    image.save(path)


def gen_qrcode(data):
    """生成二维码"""
    image = qrcode.make(data)
    buffer = BytesIO()
    image.save(buffer)
    return buffer.getvalue()

@app.task
def send_sms_by_luosimao(tel, message):
    """发送短信（调用螺丝帽短信网关）"""
    resp = requests.post(
        url='http://sms-api.luosimao.com/v1/send.json',
        auth=('api', 'key-'),
        data={
            'mobile': tel,
            'message': message
        },
        timeout=10,
        verify=False)
    return json.loads(resp.content)


QINIU_ACCESS_KEY = 'access_key'
QINIU_SECRET_KEY = 'secret_key'
QINIU_BUCKET_NAME = 'bucket_name'

auth = Auth(QINIU_ACCESS_KEY, QINIU_SECRET_KEY)

@app.task
def upload_filepath_to_qiniu(file_path, filename):
    """将文件上传到七牛云存储"""
    token = auth.upload_token(QINIU_BUCKET_NAME, filename)
    put_file(token, filename, file_path)

@app.task
def upload_stream_to_qiniu(file_stream, filename, size):
    """将数据流上传到七牛云存储"""
    token = auth.upload_token(QINIU_BUCKET_NAME, filename)
    put_stream(token, filename, file_stream, None, size)


# def url_from_key(file_key):
#     """通过文件的key拼接访问URL"""
#     return f'https://s3.{AWS3_REGION}.amazonaws.com.cn/{AWS3_BUCKET}/{file_key}'
#
#
# def s3_upload_file(file):
#     """上传文件到亚马逊S3"""
#     hasher = hashlib.md5()
#     file_name, file_size = file.name, file.size
#     key = uuid.uuid4() + "." + os.path.splitext(file_name)[1]
#     multipart_upload_init_info = S3.create_multipart_upload(
#         ACL='public-read', Bucket=AWS3_BUCKET, Key=key,
#         Expires=(datetime.datetime.today() + datetime.timedelta(days=1)),
#     )
#     upload_id = multipart_upload_init_info['UploadId']
#     part_key = multipart_upload_init_info['Key']
#
#     uploaded_size, chunks_number, parts_list = 0, 1, []
#     while uploaded_size <= file_size:
#         chunks = file.read(MAX_READ_SIZE)
#         hasher.update(chunks)
#         chunks_response = S3.upload_part(
#             Body=chunks, Bucket=AWS3_BUCKET, Key=part_key,
#             PartNumber=chunks_number, UploadId=upload_id
#         )
#         parts_list.append({
#             'ETag': chunks_response['ETag'],
#             'PartNumber': chunks_number
#         })
#         chunks_number = chunks_number + 1
#         uploaded_size += MAX_READ_SIZE
#     S3.complete_multipart_upload(
#         Bucket=AWS3_BUCKET, Key=part_key,
#         UploadId=upload_id, MultipartUpload={'Parts': parts_list}
#     )
#     body_md5 = hasher.hexdigest()
#     return url_from_key(key), body_md5

def run_in_thread_pool(*, callbacks=(), callbacks_kwargs=()):
    """将函数放入线程池执行的装饰器"""

    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            future = EXECUTOR.submit(func, *args, **kwargs)
            for index, callback in enumerate(callbacks):
                try:
                    kwargs = callbacks_kwargs[index]
                except IndexError:
                    kwargs = None
                fn = partial(callback, **kwargs) if kwargs else callback
                future.add_done_callback(fn)
            return future

        return wrapper

    return decorator