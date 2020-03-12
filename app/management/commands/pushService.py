import json

import requests
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from multiprocessing import Process, Queue
import logging
import time
from app.configutils import getconfig, ACCESS_TOKEN
from app.models import WxUser, get_or_none
from app.wxHandler import handlerSendWarningMessage
from service.wxutils import WxMessageUtil

logger = logging.getLogger(__name__)


def getWarn(warnData):
    type = ["POWER", "REMAIN_CUR", "ARC", "SMOKE", "APP", "LINE_TEMP"]
    url = "https://www.zjzwfwtech.com/api/dangerlist.json/"
    while True:
        for i in type:
            data = requests.post(url, data={"type": i})
            if data.status_code == 200:
                dataLst = json.loads(data.content.decode())
                print(dataLst)
                for i in dataLst:
                    warnData.put(i)
        time.sleep(5 * 60)


def prepareData(warnData, pushData):
    while True:
        try:
            data = warnData.get(True)
            wxUsers = WxUser.objects.filter(ammeter_id=data["ammeterId"], subscribe=True)
            if len(wxUsers) > 0:
                access_token = getconfig(ACCESS_TOKEN, "")
                template_data = handlerSendWarningMessage(data)
                for user in wxUsers:
                    preparedData = {
                        "access_token": access_token,
                        "open_id": user.openId,
                        "template_id": "0ZP2vzOjx3UpQgIMZYdHsR6SxGuZbGW2Tmtrv3RY5xw",
                        "template_data": template_data,
                        "miniProgramParams": None
                    }
                    pushData.put(preparedData)
        except Exception as e:
            print("prepareData Exception:", e)


def pushWx(pushData):
    while True:
        try:
            data = pushData.get(True)
            WxMessageUtil.send_message_by_openid(data["access_token"], data["open_id"],
                                                 data["template_id"], data["miniProgramParams"],
                                                 data["template_data"])
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
