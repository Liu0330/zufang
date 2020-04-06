# -*- coding: utf-8 -*-
import re

USERNAME_PATTERN = re.compile(r'^\w{6,20}$')
TEL_PATTERN = re.compile(r'1[3-9]\d{9}')
EMAIL_PATTERN = re.compile(r'')

MOBILE_CODE_SUCCESS = (100001, '短信验证码发送成功')
CODE_TOO_FREQUENCY = (100002, '请不要在120秒以内重复发送手机验证码')
INVALID_TEL_NUM = (100003, '请提供有效的手机号')

USER_LOGIN_SUCCESS = (200001, '用户登录成功')
USER_LOGIN_FAILED = (200002, '用户名或密码错误')
INVALID_LOGIN_INFO = (200003, '请输入有效的登录信息')
