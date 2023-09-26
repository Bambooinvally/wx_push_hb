import datetime
import hashlib
import json
import os
import time

import requests

from app.models import URLSource
from wx_push.specsetting import Url_Map


def getWarnLevel(source_id, distination,app_code_id):
    """
    根据报警内容返回报警级别
    :param app:
    :param arc:
    :param power:
    :return:
    """
    level = ['三级','二级','一级']
    i = 0
    power = getWarnByType(source_id,distination,app_code_id,'POWER')
    app = getWarnByType(source_id,distination,app_code_id,'APP')
    arc = getWarnByType(source_id,distination,app_code_id,'ARC')
    if power and arc:
        return level[2]
    if arc:
        i += 1
    if app:
        i += 1
    return level[i]

def getWarnByType(source_id, distination,app_code_id,type):
    url = URLSource.objects.get(id=source_id).url
    timestamp = int(time.time())
    # 生成签名，暂未加入user和password校验
    signed = generateMD5(timestamp, source_id)
    data = requests.post(url, data={"type": type, 'distination':distination,"ammeter_app_code":app_code_id,'source': 'wx_push', 'timestamp': timestamp,
                                    'sign': signed})
    if data.status_code == 200:
        dataLst = json.loads(data.content.decode())
        return dataLst
    else:
        return False


def simuWarn(power,arc,remain_cur,line_temp,kettle,dpc):
    level = ['三级', '二级', '一级']
    content = ['模拟报警', '本次报警为模拟数据']
    main = ''
    i = -1
    if 'on' not in [power,arc,remain_cur,line_temp,kettle,dpc]:
        return None
    if power and arc:
        content.append('严重线路故障:功率过大，电弧异常！')
        content.append('模拟设备')
        content.append('--')
        content.append(level[2])
        content.append(str(datetime.datetime.now()))
        return content
    if kettle or dpc:
        i += 2
        app = ''
        if kettle:
            app = '电水壶'
        if dpc:
            app += '电瓶车'
        main = '违规电器[' + app + ']接入报警'
        if arc:
            i += 2
        if remain_cur:
            i += 1

    if not (kettle or dpc):
        if arc :
            i += 2
            main = '故障电弧危险报警'
        if remain_cur:
            i += 1
            if 'on' not in [arc,  power]:
                main = '剩余电流危险报警'
        if line_temp:
            i += 1
            if 'on' not in [arc,remain_cur,power]:
                main = '线温异常报警'
        if power:
            i += 1
            main = '功率过大报警'
    lv = level[i if i <= 2 else 2]
    content.append(main)
    content.append('模拟设备')
    content.append('--')
    content.append(lv)
    content.append(str(datetime.datetime.now()))
    return content

def generateMD5(timestamp, sourceId):
    """

    :param timestamp:
    :param sourceId:
    :return: source+timestamp+key -------> md5
    """
    wxPushSecret = "wx_push_cad431_eyemonitor"
    source = 'wx_push'
    md5_str = "source" + source + "sourceId" +str(sourceId) + "timeStamp" + str(timestamp) + wxPushSecret
    h1 = hashlib.md5()
    h1.update(md5_str.encode(encoding='utf-8'))
    signed = h1.hexdigest()
    return signed

def SignHextoDec(Hex):
    '''有符号16进制数转10进制'''
    width = 32
    dec_temp = int(Hex, 16)
    if dec_temp > 2 ** (width - 1) - 1:
        dec_temp = 2 ** width - dec_temp
        Dec = 0 - dec_temp
        return Dec
    else:
        return dec_temp


def SignDectoHex(Dec):
    '''有符号10进制数转16进制'''
    width = 32
    if Dec < 0:
        Dec_temp = 2 ** width + Dec
        Hex = hex(Dec_temp)
        return Hex
    else:
        return hex(Dec)


def ChooseUrl(sourceId,type):
    """选择对应的Url"""
    for key,value in Url_Map.items():
        target = value["SOURCE"]
        if target == int(sourceId):
            return value[type]
    return None




if __name__ == '__main__':
    print(getWarnLevel(1,22))