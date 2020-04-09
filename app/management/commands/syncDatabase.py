import json

import requests
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from multiprocessing import Process, Queue
import logging
import time
from app.configutils import getconfig, ACCESS_TOKEN, ConfirmedUser
from app.models import  get_or_none, URLSource, Project, Ammeters
from app.wxHandler import handlerSendWarningMessage
from service.UrlService import get_urls
from service.wxutils import WxMessageUtil

logger = logging.getLogger(__name__)

def syncbd():
    url = 'http://tzdpc.piercingeyes.cn/api/ammeterlist.json'
    re = requests.get(url)
    data = json.loads(re.content.decode('utf-8'))
    device_cnt=0
    all_device = 0
    try:
        source_id = data['source_id']
        projectname = data['projectname']
        province = data['province']
        city = data['city']
        district = data['district']
    except Exception as e:
        print('数据错误')
        return
    default = {
        'source_id':source_id,
        "projectname": projectname,
        "province": province,
        "city": city,
        "district": district,
    }
    # 创建工程
    project, isnew = Project.objects.get_or_create(source_id=source_id,defaults=default)
    print('创建工程',project.projectname) if isnew else print(project.projectname,'已存在未创建')
    # 导入板子
    all_device = len(data['data'])
    for ammeter in data['data']:
        default = {
            "ammeter_app_code": ammeter['ammeter_app_code'],
            "ammeter_addr": ammeter['location'] if ammeter['location'] is not None else '--',
            "domain": ammeter['ammeter_distination']  # 原来的单元号，电瓶车项目的板子号
        }
        amt,isnew=Ammeters.objects.update_or_create(source_id=source_id,ammeter_app_code=ammeter['ammeter_app_code'],defaults=default)
        if isnew:
            device_cnt += 1

    print('设备总数：',all_device,'成功导入：',device_cnt)

class Command(BaseCommand):

    def handle(self, *args, **options):
        syncbd()
