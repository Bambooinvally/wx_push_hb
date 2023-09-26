import datetime
import json
import logging
import os
import socket
import sys
import time
import traceback
from multiprocessing import Process, Queue

import requests
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.models import Q

from app.configutils import getconfig, ACCESS_TOKEN
from app.models import Ammeters, ConfirmedUser, PushHistory, SuperUser, get_or_none
from app.wxHandler import handlerSendWarningMessage
from service.UrlService import get_urls
from service.utils import generateMD5, SignHextoDec
from service.wxconfig import TEMPLATE_ID
from service.wxutils import WxMessageUtil

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
            print('Socket 连接成功 sourceId：',self.sourceId)
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
                    "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(int(data[8]) / 1000))),
                    "value": data[7],
                    "ammeterId": SignHextoDec(data[3]),
                    "location": "--",
                    "valueAttach": data[6],
                    "source_id": self.sourceId,
                    "ammeter_distination": data[4]
                }
                print(app)
                self.warnData.put(app)


def getHDUApp(warnData):
    """
    功能定义：通过tcp长连接方式获取接入或者移除的信息
    :param warnData:
    :return:
    """
    tcpClientHDU = TcpClient(sourceId=1, ADDRESS=ADDRESS, PORT=PORT, warnData=warnData, Token="HDUPROD")
    tcpClientHDU.connect()
    tcpClientHDU.getMessage()


def getXMUApp(warnData):
    """
    功能定义：通过tcp长连接方式获取接入或者移除的信息
    :param warnData:
    :return:
    """
    tcpClientXMU = TcpClient(sourceId=2, ADDRESS=ADDRESS, PORT=PORT, warnData=warnData, Token="XMUPROD")
    tcpClientXMU.connect()
    tcpClientXMU.getMessage()


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
                    data = requests.post(url, data={"type": i, 'source': 'wx_push', 'timestamp': timestamp,
                                                    'sign': signed})

                    if data.status_code == 200:
                        # print(i, ' 连接成功')
                        dataLst = json.loads(data.content.decode())
                        for j in dataLst:
                            # j["source_id"] = j["source_id"]   # source_id
                            warnData.put(j)
                    else:
                        print(i, ' 连接失败，正在重试...')
            time.sleep(20)
        except Exception as e:
            print('get warn error:', e)
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
        night_state = 0
        try:
            data = warnData.get(True)
            if data is None:
                continue
            try:
                t1 = '23:00'
                t2 = '23:59'
                t3 = '00:00'
                t4 = '05:59'
                now = datetime.datetime.now().strftime("%H:%M")
                if t1 <= now <= t2 or t3 <= now <= t4:
                    print('晚上了', now)
                    # print(data['location'], data['value'])
                    # continue
                    night_state = 1
            except Exception as e:
                print('过滤出错' + str(e))
                continue
            commonUsers = None
            superUsers = None

            if data['type'] == 'WHOLE_APP':
                # 筛选设备下的所有绑定用户
                commonUsers = ConfirmedUser.objects.filter(ammeter__source=data['source_id'],
                                                           ammeter__ammeter_app_code=data['ammeterId'],
                                                           ammeter__ammeter_sensorId=data['ammeter_distination'])
            elif data['type'] != 'LIMIT_APP' and data['type'] != 'WHOLE_APP':
                # 筛选设备下的所有绑定用户
                commonUsers = ConfirmedUser.objects.filter(ammeter__source=data['source_id'],
                                                           ammeter__ammeter_app_code=data['ammeterId'],
                                                           ammeter__ammeter_sensorId=data['ammeter_distination'])
                # 有权限的管理员
                superUsers = SuperUser.objects.filter(Q(source_id='all') |
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
            elif data['type'] == 'LIMIT_APP':
                superUsers = SuperUser.objects.filter(Q(source_id='all') |
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

            # if commonUsers or superUsers:
            access_token = getconfig(ACCESS_TOKEN, "")
            if commonUsers:
                print(commonUsers.count(),'个普通用户')
                for user in commonUsers:
                    template_data = handlerSendWarningMessage(data, user, 0)
                    # print('开始取用户')
                    print('名称', user.name)
                    preparedData = {
                        "access_token": access_token,
                        "open_id": user.openId,
                        "template_id": TEMPLATE_ID,
                        "template_data": template_data,
                        "miniProgramParams": None,
                        "username": user.name,
                        "type": data['type'],
                        "isSuperuser": 0,
                        "device": get_or_none(Ammeters, source_id=data['source_id'],
                                              ammeter_app_code=data['ammeterId'],
                                              ammeter_sensorId=data['ammeter_distination']),
                        "app_push": user.apppush,
                        "night_push": user.nightpush,
                        "night_state": night_state
                        #     'source:'+str(data['source_id'])+'app_code_id:'+str(data['ammeterId'])+
                        # "distination:"+str(data['ammeter_distination'])
                    }
                    if superUsers is not None:
                        if superUsers.filter(openId=user.openId).first() is not None:
                            preparedData["night_push"] = False
                    pushData.put(preparedData)
            print('开始判断管理员')
            if superUsers:
                template_data = handlerSendWarningMessage(data,
                                                          ConfirmedUser.objects.filter(
                                                              ammeter__source=data['source_id'],
                                                              ammeter__ammeter_app_code=data['ammeterId'],
                                                              ammeter__ammeter_sensorId=data[
                                                                  'ammeter_distination']).first(), 1)
                for user in superUsers:
                    if commonUsers is not None:
                        if commonUsers.filter(openId=user.openId).first() is not None:
                            print("管理员已在普通用户中，不重复推送")
                        else:
                            preparedData = {
                                "access_token": access_token,
                                "open_id": user.openId,
                                "template_id": TEMPLATE_ID,
                                "template_data": template_data,
                                "miniProgramParams": None,
                                "username": user.name,
                                "type": data['type'],
                                "isSuperuser": 1,
                                "device": get_or_none(Ammeters, source_id=data['source_id'],
                                                      ammeter_app_code=data['ammeterId'],
                                                      ammeter_sensorId=data['ammeter_distination']),
                                "night_push": False,  # 管理员夜间一定要推送！
                                "night_state": night_state
                            }
                            pushData.put(preparedData)
                    else:
                        preparedData = {
                            "access_token": access_token,
                            "open_id": user.openId,
                            "template_id": TEMPLATE_ID,
                            "template_data": template_data,
                            "miniProgramParams": None,
                            "username": user.name,
                            "type": data['type'],
                            "isSuperuser": 1,
                            "device": get_or_none(Ammeters, source_id=data['source_id'],
                                                  ammeter_app_code=data['ammeterId'],
                                                  ammeter_sensorId=data['ammeter_distination']),
                            "night_push": False,  # 管理员夜间一定要推送！
                            "night_state": night_state
                        }
                        pushData.put(preparedData)
        except Exception as e:
            exc_type, exc_value, exc_obj = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_obj, limit=2, file=sys.stdout)
            print("prepareData Exception:", e)


def pushWx(pushData):
    while True:
        # print('进入pushWx')
        close_old_connections()
        try:
            data = pushData.get(True)
            isPush = 0  # 时候成功推到微信公众号上

            '''******用电器接入/移除判断模块******'''
            check = 0  # 用电器接入/移除标志位
            check_valid = 0  # 用电器接入/移除推送有效标志位
            shortTime_same_device_in = None
            shortTime_same_device_out = None
            # print('进入用电器接入/移除判断模块...')
            username = data.get('username', '')
            if data["template_data"].keyword1['value'] == '用电器接入提醒' or data["template_data"].keyword1[
                'value'] == '用电器移除提醒':
                # 用电器接入/移除标志位 置1
                check = 1
                # 分离用电器
                mass = data["template_data"].keyword3['value'].split(' ')[0]
                # 相同设备推送时间间隔限制
                limit_time = datetime.datetime.now() - datetime.timedelta(seconds=30)

                '''******用电器推送限制核心模块******'''
                # 检测用电器是否为接入状态
                # print('进入用电器推送限制核心模块...')
                if "接入" in data["template_data"].keyword3['value']:
                    # 如果筛选openId,name,type,massage包含电器的最新一条记录中massage包含'接入'，则不推送
                    check_massage = PushHistory.objects.filter(touser=data["open_id"], name=username, type=data['type'],
                                                               massage__icontains=mass).last()
                    if check_massage is not None:
                        if '接入' in check_massage.massage:
                            print("重复接入相同设备不推送")
                        elif '移除' in check_massage.massage:
                            # 判断上一次接入有效推送是否在5秒内
                            shortTime_same_device_in = PushHistory.objects.filter(touser=data["open_id"], name=username,
                                                                                  type=data['type'],
                                                                                  massage__icontains=mass + ' 已接入',
                                                                                  pushtime__gte=limit_time,
                                                                                  isPush=1).last()
                            if shortTime_same_device_in is not None:
                                check_valid = 0
                                print("短时间极速推送，不允许！")
                            else:
                                check_valid = 1
                                isPush = 1
                    else:
                        # 首次接入得推送
                        check_valid = 1
                        isPush = 1
                # 检测用电器是否为移除状态
                elif "移除" in data["template_data"].keyword3['value']:
                    # 如果筛选openId,name,type,massage包含用电器的最新一条记录中massage包含'移除'，则不推送
                    check_massage = PushHistory.objects.filter(touser=data["open_id"], name=username, type=data['type'],
                                                               massage__icontains=mass).last()
                    if check_massage is not None:
                        if '移除' in check_massage.massage:
                            # 没有接入就不推送
                            print("上次没有接入，不能移除")
                        elif '接入' in check_massage.massage:
                            # 有接入才有移除推送
                            # 推送时间逻辑限制
                            lasttime_string = check_massage.massage.split(')')[-1]
                            lasttime_object = datetime.datetime.strptime(str(lasttime_string), "%Y-%m-%d %H:%M:%S")
                            datetime_object = datetime.datetime.strptime(
                                str(data["template_data"].keyword5['value']), "%Y-%m-%d %H:%M:%S")
                            if datetime_object <= lasttime_object:
                                print('本次移除时间在上次设备接入之前，不推送')
                            else:
                                # 判断上一次移除有效推送是否在5秒内
                                shortTime_same_device_out = PushHistory.objects.filter(touser=data["open_id"],
                                                                                       name=username,
                                                                                       type=data['type'],
                                                                                       massage__icontains=mass + ' 已移除',
                                                                                       pushtime__gte=limit_time,
                                                                                       isPush=1).last()
                                if shortTime_same_device_out is not None:
                                    check_valid = 0
                                    print("短时间极速推送，不允许！")
                                else:
                                    check_valid = 1
                                    isPush = 1
                    else:
                        print('首次运行不能有移除')

            '''******重复推送内容存储限制模块******'''
            # 一小时内本次推送的和前几次完全雷同
            # print('进入重复推送内容存储限制模块...')
            hour = datetime.datetime.now() - datetime.timedelta(hours=1)
            # same_content_user = None
            same_content_user = PushHistory.objects.filter(touser=data["open_id"],
                                                           name=username, type=data['type'],
                                                           massage=str(data['device'].ammeter_unit) + '号楼' + str(
                                                               data['device'].ammeter_addr) + str(
                                                               data["template_data"].keyword1['value']) +
                                                                   '(' + str(
                                                               data["template_data"].keyword3['value']) + ')' +
                                                                   str(data["template_data"].keyword5['value']),
                                                           pushtime__gte=hour).count()
            #  一定时间内 内容雷同的不可存储
            if same_content_user != 0:
                continue

            '''******用电器推送模块******'''
            # 确定用电器包且要推送
            # print('进入用电器推送模块...')
            if check == 1:
                if check_valid == 1:
                    if data["app_push"] == 1:
                        if data["night_state"] == 0:  # 白天
                            print("即将推送:", data)
                            result = WxMessageUtil.send_message_by_openid(data["access_token"], data["open_id"],
                                                                          data["template_id"],
                                                                          data["miniProgramParams"],
                                                                          data["template_data"], data['device'])
                            if result != '推送失败':
                                print("推送成功")
                                isPush = 1
                            else:
                                print("推送失败")
                        elif data["night_state"] == 1:  # 夜间
                            if data["night_push"] is True:
                                print("即将推送:", data)
                                result = WxMessageUtil.send_message_by_openid(data["access_token"], data["open_id"],
                                                                              data["template_id"],
                                                                              data["miniProgramParams"],
                                                                              data["template_data"], data['device'])
                                if result != '推送失败':
                                    print("夜间推送成功")
                                    isPush = 1
                                else:
                                    print("夜间推送失败")
                            else:
                                print("用户设置夜间不推送")
                    elif data["app_push"] == 0:
                        print('用户设置不推送用电器')

            '''******危险报警推送模块******'''
            # 开始判断要不要推送
            # 1.判断前面是不是用电器接入/移除，是就不推了
            # print('进入危险报警推送模块...')
            if check == 0:
                result = '推送失败'
                # 不是用电器，那就是危险报警了！！！
                limit_time = datetime.datetime.now() - datetime.timedelta(seconds=90)
                if data["night_state"] == 0:  # 白天
                    # 短时间内相同报警信息推送限制
                    shortTime_same_device = PushHistory.objects.filter(touser=data["open_id"], name=username,
                                                                       type=data['type'],
                                                                       massage__icontains=str(
                                                                           data["template_data"].keyword1['value']),
                                                                       pushtime__gte=limit_time,
                                                                       isPush=1).last()
                    if shortTime_same_device is not None:
                        print("短时间极速推送，不允许！")
                    else:
                        print("即将推送:", data)
                        result = WxMessageUtil.send_message_by_openid(data["access_token"], data["open_id"],
                                                                      data["template_id"], data["miniProgramParams"],
                                                                      data["template_data"], data['device'])
                        if result != '推送失败':
                            print("推送成功")
                            isPush = 1
                        else:
                            print("推送失败")
                elif data["night_state"] == 1:  # 夜间
                    if data["night_push"] is True:
                        # 短时间内相同报警信息推送限制
                        shortTime_same_device = PushHistory.objects.filter(touser=data["open_id"], name=username,
                                                                           type=data['type'],
                                                                           massage__icontains=str(
                                                                               data["template_data"].keyword1['value']),
                                                                           pushtime__gte=limit_time,
                                                                           isPush=1).last()
                        if shortTime_same_device is not None:
                            print("短时间极速推送，不允许！")
                        else:
                            print("即将推送:", data)
                            result = WxMessageUtil.send_message_by_openid(data["access_token"], data["open_id"],
                                                                          data["template_id"],
                                                                          data["miniProgramParams"],
                                                                          data["template_data"], data['device'])
                            if result != '推送失败':
                                print("夜间推送成功")
                                isPush = 1
                            else:
                                print("夜间推送失败")
                    elif data["night_push"] is False:
                        print("用户设置夜间不报警")
                print(data['username'], result)

            '''******数据库记录模块******'''
            # print('进入数据库记录模块...')
            # 2.不管三七二十一，都记在数据库里再说
            PushHistory.objects.create(touser=data["open_id"], name=username, type=data['type'],
                                       massage=str(data['device'].ammeter_unit) + '号楼' + str(
                                           data['device'].ammeter_addr) + str(
                                           data["template_data"].keyword1['value']) +
                                               '(' + str(data["template_data"].keyword3['value']) + ')' +
                                               str(data["template_data"].keyword5['value']),
                                       isPush=isPush)

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
        phduapp = Process(target=getHDUApp, args=(warnData,))
        pxmuapp = Process(target=getXMUApp, args=(warnData,))
        phduapp.start()
        pxmuapp.start()
        pwarn.start()
        ppreparedata.start()
        ppush.start()
