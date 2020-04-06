# -*- coding: utf-8 -*-
import io
import random
from urllib.parse import quote

import xlwt
from django.db.models import Avg
from django.http import HttpResponse
from rest_framework.decorators import api_view

from api.helpers import DefaultResponse
from backend.models import Emp, Dept


@api_view(('GET', ))
def get_bar_data(request):
    queryset = Emp.objects.values('dept__name').annotate(avgsal=Avg('sal'))
    names, sals = [], []
    for result in queryset:
        names.append(result['dept__name'])
        sals.append('%.2f' % float(result['avgsal']))
    return DefaultResponse(data={
        'names': names,
        'sals': [
            sals,
            ['%.2f' % (random.randint(-1000, 1000) + float(sal)) for sal in sals],
            ['%.2f' % (random.randint(-1000, 1000) + float(sal)) for sal in sals],
            ['%.2f' % (random.randint(-1000, 1000) + float(sal)) for sal in sals],
        ]
    })


def export_excel(request):
    # 创建工作簿
    wb = xlwt.Workbook()
    # 添加工作表
    sheet = wb.add_sheet('员工信息表')
    # 向Excel表单中写入表头
    titles = ('编号', '姓名', '职位', '主管', '工资', '部门')
    #通过数据库来调取员工数据写入单元格内
    for col, title in enumerate(titles):
        sheet.write(0, col, title)
    queryset = Emp.objects.all().defer('comm')
    props = ('no', 'name', 'job', 'mgr', 'sal', 'dept')
    for row, emp in enumerate(queryset):
        for col, prop in enumerate(props):
            #动态获取属性，这里有点难理解可能。
            value = getattr(emp, prop, '')
            if isinstance(value, (Dept, Emp)):
                value = value.name
            sheet.write(row + 1, col, value)
    # 保存excel
    buffer = io.BytesIO()
    wb.save(buffer)
    # 将二进制数据写入响应的消息体中并设置MIME类型
    resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.msexecl')
    # 中文文件名需要处理成百分号编码用到
    filename =('员工信息表.xls')
    # 通过响应头告知浏览器下载该文件以及对应的文件名
    resp['content-disposition'] = f'attachment; filename="{quote(filename)}"'
    return resp
