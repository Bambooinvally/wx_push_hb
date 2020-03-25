import datetime

import wx_push.urls
import json
import os
import requests
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from multiprocessing import Process, Queue
import logging
import time
from app.configutils import getconfig, ACCESS_TOKEN
from app.models import Ammeters, ConfirmedUser, PushHistory, SuperUser, get_or_none
from app.wxHandler import handlerSendWarningMessage
from service.UrlService import get_urls
from service.wxutils import WxMessageUtil
from django.db.models import Q
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wx_push_for_tz.settings")

logger = logging.getLogger(__name__)

"""
需要重新测试：添加了source_id
"""


def getWarn(warnData):
    # type = ["POWER", "REMAIN_CUR", "ARC", "SMOKE", "APP", "LINE_TEMP"]
    type = ["POWER",  "ARC",  "APP"]
    # url = "https://www.zjzwfwtech.com/api/dangerlist.json/"
    while True:
        # 获取所有的url
        url_map = get_urls()
        for source_id in url_map:
            url = url_map[source_id]
            for i in type:
                data = requests.post(url, data={"type": i})
                if data.status_code == 200:
                    dataLst = json.loads(data.content.decode())
                    for j in dataLst:
                        j["source_id"] = source_id
                        warnData.put(j)
        time.sleep(10)


def prepareData(warnData, pushData):
    """
    电弧、功率向普通用户开放，违禁电器仅发给有权限的管理员
    :param warnData:
    :param pushData:
    :return:
    """
    while True:
        try:
            data = warnData.get(True)
            if data['type'] != 'APP':
                # 用户本人
                commonUsers = ConfirmedUser.objects.filter(ammeter__source=data['source_id'],ammeter__ammeter_app_code=data['ammeterId'])
                # 有权限的管理员
                # &
                # Q(domain__iregex=','+str(data['domain'])+','))
                superUsers = SuperUser.objects.filter(Q(source_id='all')|
                                                      (Q(source_id__iregex=('^'+str(data['source_id'])+',')+'|'+(','+str(data['source_id'])+',')
                                                                           + '|' +(','+str(data['source_id'])+'$'))))
                wxUsers = commonUsers|superUsers
            else:
                wxUsers = SuperUser.objects.filter(Q(source_id='all')|(Q(source_id__iregex=('^'+str(data['source_id'])+',')+'|'+(','+str(data['source_id'])+',')
                                                                                           + '|' +(','+str(data['source_id'])+'$'))))
            if len(wxUsers) > 0:
                access_token = getconfig(ACCESS_TOKEN, "")
                template_data = handlerSendWarningMessage(data,wxUsers[0])
                for user in wxUsers:
                    print(user.name)
                    preparedData = {
                        "access_token": access_token,
                        "open_id": user.openId,
                        "template_id": "0ZP2vzOjx3UpQgIMZYdHsR6SxGuZbGW2Tmtrv3RY5xw",
                        "template_data": template_data,
                        "miniProgramParams": None,
                        "username":user.name,
                        "type":data['type'],
                        "device":'source:'+str(data['source_id'])+'app_code_id:'+str(data['ammeterId'])
                    }
                    pushData.put(preparedData)
        except Exception as e:
            print("prepareData Exception:", e)


def pushWx(pushData):
    while True:
        try:
            data = pushData.get(True)
            # 获取推送时间间隔，单位：分钟
            push_delta = int(getconfig('push_delta',30))
            canPushTime = datetime.datetime.now() - datetime.timedelta(seconds=60*push_delta)
            hour = datetime.datetime.now() - datetime.timedelta(hours=1)
            # 推过不久的用户
            user = PushHistory.objects.filter(touser=data["open_id"],pushtime__gte=canPushTime)
            # 一小时内本次推送的和前几次完全雷同
            same_content_user = PushHistory.objects.filter(touser=data["open_id"],
                                                           name=data['username'],type=data['type'],
                                           massage=str(data['device'])+str(data["template_data"].keyword1)+
                                           str(data["template_data"].keyword5),pushtime__gte=hour)
            # # 30分钟内推过的不可推送
            # if user:
            #     continue
            #  一小时内内容雷同的不可推送
            if same_content_user:
                continue
            WxMessageUtil.send_message_by_openid(data["access_token"], data["open_id"],
                                                 data["template_id"], data["miniProgramParams"],
                                                 data["template_data"])
            PushHistory.objects.create(touser=data["open_id"],name=data['username'],type=data['type'],
                                       massage=str(data['device'])+str(data["template_data"].keyword1)+
                                       str(data["template_data"].keyword5))
        except Exception as e:
            print("pushWx Exception:", e)


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        warnData = Queue()
        pushData = Queue()
        pwarn = Process(target=getWarn, args=(warnData,))
        ppreparedata = Process(target=prepareData, args=(warnData, pushData,))
        ppush = Process(target=pushWx, args=(pushData,))
        pwarn.start()
        ppreparedata.start()
        ppush.start()
