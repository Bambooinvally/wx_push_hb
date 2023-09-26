import datetime
import socket

from django.db import connections
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
from service.utils import generateMD5, SignHextoDec, SignDectoHex
from service.wxconfig import TEMPLATE_ID
from service.wxutils import WxMessageUtil
from django.db.models import Q

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "wx_push_for_tz.settings")

logger = logging.getLogger(__name__)

"""
需要重新测试：添加了source_id
"""

ADDRESS = '127.0.0.1'
PORT = 10010


class TcpClient:
    '''接收设备接入和移除的tcp客户端'''

    def __init__(self, sourceId, ADDRESS, PORT, warnData, Token):
        self.Token = Token
        self.warnData = warnData
        self.Socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sourceId = sourceId
        self.ADDRESS = ADDRESS
        self.PORT = PORT

    def connect(self):
        try:
            self.Socket.connect((ADDRESS, PORT))
            self.Socket.settimeout(5000)
            self.Socket.send(self.Token.encode())
            print('Socket 连接成功')
            return 'connect sucess'
        except Exception as e:
            print('连接服务器失败' + str(e))
            return 'connect failed'

    def getMessage(self):
        while True:
            ret = self.Socket.recv(1024).decode("utf-8")
            data = ret.split('#')
            # 判断是否是电器识别包
            if data[0] == 'FFFF' and data[2] == 'distinguish' and data[9] == 'FEFE':
                app = {
                    "type": "WHOLE_APP",
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(int(data[8])/1000))),
                    "value": data[7],
                    "ammeterId": SignHextoDec(data[3]),
                    "location": "--",
                    "valueAttach": data[6],
                    "source_id": self.sourceId,
                    "ammeter_distination": data[4]
                }
                print(app)
                self.warnData.put(app)

def getApp(warnData):
    """
    功能定义：通过tcp长连接方式获取接入或者移除的信息
    :param warnData:
    :return:
    """
    tcpClient = TcpClient(sourceId=1, ADDRESS=ADDRESS, PORT=PORT, warnData=warnData, Token="HDUPROD")
    tcpClient.connect()
    tcpClient.getMessage()


def getWarn(warnData):
    """
    功能定义：APP->接入时间过长的电器
            LIMIT_APP->违禁电器
    :param warnData:
    :return:
    """
    type = ["POWER", "REMAIN_CUR", "ARC", "SMOKE", "APP", "LINE_TEMP", "LIMIT_APP"]
    # type = ["POWER",  "ARC",  "APP", "LIMIT_APP"]
    # url = "https://www.zjzwfwtech.com/api/dangerlist.json/"
    while True:
        try:
            close_old_connections()
            # 获取所有的url
            url_map = get_urls()
            for source_id in url_map:
                url = url_map[source_id]
                for i in type:
                    timestamp = int(time.time())
                    # 生成签名，暂未加入user和password校验
                    signed = generateMD5(timestamp, source_id)
                    data = requests.post(url, data={"type": i, 'source': 'wx_push', 'timestamp':timestamp,
                                                    'sign': signed})
                    # print(data)
                    if data.status_code == 200:
                        # print(i, ' 连接成功')
                        dataLst = json.loads(data.content.decode())
                        for j in dataLst:
                            # j["source_id"] = j["source_id"]   # source_id
                            warnData.put(j)
                            print(j)
                    else:
                        print(i, ' 连接失败，正在重试...')
            time.sleep(20)
        except Exception as e:
            print('get warn error:',e)
            time.sleep(20)


def prepareData(warnData, pushData):
    """
    电弧、功率向普通用户开放，违禁电器仅发给有权限的管理员
    :param warnData:
    :param pushData:
    :return:
    """
    while True:
        close_old_connections()
        night_no_push = 0
        try:
            data = warnData.get(True)
            print(data)
            if data is None:
                # print('无数据')
                continue
            # print('1 get data')
            try:
                t1 = '23:00'
                t2 = '23:59'
                t3 = '00:00'
                t4 = '06:00'
                now = datetime.datetime.now().strftime("%H:%M")
                if t1 <= now <= t2 or t3 <= now <= t4:
                    print('晚上不推送',now)
                    print(data['location'],data['value'])
                    # continue
                    night_no_push = 1
            except Exception as e:
                print('过滤出错' + str(e))
                continue
            commonUsers = None
            superUsers = None
            # if (data['type'] == 'ARC' and data['location'] not in ['演示箱',]) or (data['value'] == '电水壶' and data['location'] in ['外岙村3-70户','长沙村83号出租房']):
            #     continue
            if data['type'] == 'WHOLE_APP':
                # 用户本人
                commonUsers = ConfirmedUser.objects.filter(ammeter__source=data['source_id'],
                                                           ammeter__ammeter_app_code=data['ammeterId'],
                                                           ammeter__ammeter_sensorId=data['ammeter_distination'])
            elif data['type'] != 'LIMIT_APP' and data['type'] != 'WHOLE_APP':
                # print('2 data type is not app')
                # 用户本人
                commonUsers = ConfirmedUser.objects.filter(ammeter__source=data['source_id'],
                                                           ammeter__ammeter_app_code=data['ammeterId'],
                                                           ammeter__ammeter_sensorId=data['ammeter_distination'])
                # 有权限的管理员
                # &
                # Q(domain__iregex=','+str(data['domain'])+','))
                superUsers = SuperUser.objects.filter(Q(source_id='all')|
                                                      (Q(source_id__iregex=('^'+str(data['source_id'])+',')+'|'+(','+str(data['source_id'])+',')
                                                                           + '|' +(','+str(data['source_id'])+'$'))
                                                       &(Q(domain__iregex=('^'+str(data['ammeter_distination'])+',')+'|'+
                                                                         (','+str(data['ammeter_distination'])+',')
                                                                           + '|' +(','+str(data['ammeter_distination'])+'$'))
                                                       |Q(domain='all'))))
                # print('3 get users ok')
            elif data['type'] == 'LIMIT_APP':
                # print('4 get app pack')
                superUsers = SuperUser.objects.filter(Q(source_id='all')|
                                                      (Q(source_id__iregex=('^' + str(
                                                          data['source_id']) + ',') + '|' + (',' + str(
                                                          data['source_id']) + ',')
                                                                           + '|' + (',' + str(data['source_id']) + '$'))
                                                       & (Q(domain__iregex=('^' + str(
                                                                  data['ammeter_distination']) + ',') + '|' +
                                                                           (',' + str(
                                                                               data['ammeter_distination']) + ',')
                                                                           + '|' + (',' + str(
                                                                  data['ammeter_distination']) + '$'))
                                                          | Q(domain='all'))))
                                                      # (Q(source_id__iregex=('^'+str(data['source_id'])+',')+'|'+(','+str(data['source_id'])+',')
                                                      #                                      + '|' +(','+str(data['source_id'])+'$'))
                                                      #                     ))
                # print('5 get app push user ok')

            # if commonUsers or superUsers:
            access_token = getconfig(ACCESS_TOKEN, "")
            # print('6 before get temp data')

            # print('7 make temp ok')
            if commonUsers:
                print(commonUsers.count())
                # template_data = handlerSendWarningMessage(data,
                #                                           get_or_none(ConfirmedUser, ammeter__source=data['source_id'],
                #                                                       ammeter__ammeter_app_code=data['ammeterId'],
                #                                                       ammeter__domain=data['ammeter_distination']),0)
                for user in commonUsers:
                    template_data = handlerSendWarningMessage(data, user, 0)
                    print('开始取用户')
                    print('common',user.name)
                    preparedData = {
                        "access_token": access_token,
                        "open_id": user.openId,
                        "template_id": TEMPLATE_ID,
                        "template_data": template_data,
                        "miniProgramParams": None,
                        "username":user.name,
                        "type":data['type'],
                        "isSuperuser":0,
                        "device": get_or_none(Ammeters, source_id=data['source_id'],
                                                                      ammeter_app_code=data['ammeterId'],
                                                                      ammeter_sensorId=data['ammeter_distination']),
                        "night_no_push": night_no_push
                        #     'source:'+str(data['source_id'])+'app_code_id:'+str(data['ammeterId'])+
                        # "distination:"+str(data['ammeter_distination'])
                    }
                    pushData.put(preparedData)
            # print('7 prepared data complete')
            if superUsers:
                template_data = handlerSendWarningMessage(data,
                                                          ConfirmedUser.objects.filter(ammeter__source=data['source_id'],
                                                                      ammeter__ammeter_app_code=data['ammeterId'],
                                                                      ammeter__ammeter_sensorId=data['ammeter_distination']).first(), 1)
                for user in superUsers:
                    # print('开始取用户')
                    #print('super',user.name)
                    preparedData = {
                        "access_token": access_token,
                        "open_id": user.openId,
                        "template_id": TEMPLATE_ID,
                        "template_data": template_data,
                        "miniProgramParams": None,
                        "username":user.name,
                        "type":data['type'],
                        "isSuperuser": 0,
                        "device":get_or_none(Ammeters, source_id=data['source_id'],
                                                                      ammeter_app_code=data['ammeterId'],
                                                                      ammeter_sensorId=data['ammeter_distination']),
                        "night_no_push": night_no_push
                        #     'source:'+str(data['source_id'])+'app_code_id:'+str(data['ammeterId'])+
                        # "distination:"+str(data['ammeter_distination'])
                    }
                    # print('data is :',data)
                    # print(preparedData)
                    pushData.put(preparedData)
        except Exception as e:
            print("prepareData Exception:", e)
            # raise e


def pushWx(pushData):
    while True:
        close_old_connections()
        try:
            data = pushData.get(True)
            # # 获取推送时间间隔，单位：分钟
            # push_delta = int(getconfig('push_delta', 30))
            # canPushTime = datetime.datetime.now() - datetime.timedelta(seconds=60 * push_delta)
            # # 推过不久的用户
            # user = PushHistory.objects.filter(touser=data["open_id"], pushtime__gte=canPushTime)
            # # 30分钟内推过的不可推送
            # if user:
            #     continue

            check = 0
            username = data.get('username', '')
            hour = datetime.datetime.now() - datetime.timedelta(hours=1)
            if data["template_data"].keyword1['value'] == '用电器接入提醒' or data["template_data"].keyword1[
                'value'] == '用电器移除提醒':
                # 15秒内不在提醒
                hour = datetime.datetime.now() - datetime.timedelta(seconds=15)
                # 分离用电器
                mass = data["template_data"].keyword3['value'].split(' ')[0]
                # 检测用电器是否为接入状态
                if "接入" in data["template_data"].keyword3['value']:
                    # 如果筛选openId,name,type,massage包含电器的最新一条记录中massage包含'接入'，则不推送
                    check_massage = PushHistory.objects.filter(touser=data["open_id"], name=username, type=data['type'],
                                                               massage__icontains=mass).last()
                    if check_massage is not None:
                        if '接入' in check_massage.massage:
                            check = 1
                    else:
                        # 首次接入得推送
                        check = 0
                # 检测用电器是否为移除状态
                elif "移除" in data["template_data"].keyword3['value']:
                    # 如果筛选openId,name,type,massage包含用电器的最新一条记录中massage包含'移除'，则不推送
                    check_massage = PushHistory.objects.filter(touser=data["open_id"], name=username, type=data['type'],
                                                               massage__icontains=mass).last()
                    if check_massage is not None:
                        if '移除' in check_massage.massage:
                            # 没有接入就不推送
                            check = 1
                        elif '接入' in check_massage.massage:
                            # 有接入才有移除推送
                            # 推送时间逻辑限制
                            if data["night_no_push"] == 0:
                                lasttime_string = check_massage.massage.split(')')[-1]
                                lasttime_object = datetime.datetime.strptime(str(lasttime_string), "%Y-%m-%d %H:%M:%S")
                                datetime_object = datetime.datetime.strptime(str(data["template_data"].keyword5['value']), "%Y-%m-%d %H:%M:%S")
                                if datetime_object <= lasttime_object:
                                    check = 1
                                    print('由于本次移除时间在上次接入之前，故不推送')
                                else:
                                    check = 0
                            elif data["night_no_push"] == 1:
                                lasttime_string_1 = check_massage.massage.split(')')[-1]
                                lasttime_string_2 = lasttime_string_1.split('夜晚')[0]
                                lasttime_object = datetime.datetime.strptime(str(lasttime_string_2), "%Y-%m-%d %H:%M:%S")
                                datetime_object = datetime.datetime.strptime(str(data["template_data"].keyword5['value']),
                                                                    "%Y-%m-%d %H:%M:%S")
                                if datetime_object <= lasttime_object:
                                    check = 1
                                    print('由于本次移除时间在上次接入之前，故不推送')
                                else:
                                    check = 0
                    else:
                        # 首次运行不能有移除
                        check = 1
            if check == 1:
                continue

            # 一小时内本次推送的和前几次完全雷同
            same_content_user = PushHistory.objects.filter(touser=data["open_id"],
                                                           name=username, type=data['type'],
                                                           massage=str(data['device'].ammeter_unit) + '号楼' + str(
                                                               data['device'].ammeter_addr) + str(
                                                               data["template_data"].keyword1['value']) +
                                                                   '(' + str(
                                                               data["template_data"].keyword3['value']) + ')' +
                                                                   str(data["template_data"].keyword5['value']),
                                                           pushtime__gte=hour)
            #  一定时间内 内容雷同的不可推送
            if same_content_user:
                continue

            if data["night_no_push"] == 0:
                print("即将推送:", data)
                result = WxMessageUtil.send_message_by_openid(data["access_token"], data["open_id"],
                                                              data["template_id"], data["miniProgramParams"],
                                                              data["template_data"], data['device'])
                if result != '推送失败':
                    print("推送成功")
                    PushHistory.objects.create(touser=data["open_id"], name=username, type=data['type'],
                                               massage=str(data['device'].ammeter_unit) + '号楼' + str(
                                                   data['device'].ammeter_addr) + str(
                                                   data["template_data"].keyword1['value']) +
                                                       '(' + str(data["template_data"].keyword3['value']) + ')' +
                                                       str(data["template_data"].keyword5['value']))
                else:
                    print("推送失败")
            elif data["night_no_push"] == 1:
                PushHistory.objects.create(touser=data["open_id"], name=username, type=data['type'],
                                           massage=str(data['device'].ammeter_unit) + '号楼' + str(
                                               data['device'].ammeter_addr) + str(
                                               data["template_data"].keyword1['value']) +
                                                   '(' + str(data["template_data"].keyword3['value']) + ')' +
                                                   str(data["template_data"].keyword5['value']) + '夜晚')

            print(data['username'], result)
        except Exception as e:
            print("pushWx Exception:", e)
            # raise e


def close_old_connections():
    for conn in connections.all():
        conn.close_if_unusable_or_obsolete()


class Command(BaseCommand):

    def handle(self, *args, **options):
        warnData = Queue()
        pushData = Queue()
        pwarn = Process(target=getWarn, args=(warnData,))
        ppreparedata = Process(target=prepareData, args=(warnData, pushData,))
        ppush = Process(target=pushWx, args=(pushData,))
        # 获取接入或移除
        papp = Process(target=getApp, args=(warnData,))
        papp.start()
        pwarn.start()
        ppreparedata.start()
        ppush.start()
