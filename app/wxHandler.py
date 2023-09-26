import datetime
import time

from app.configutils import setconfiga, ACCESS_TOKEN, getconfigattached
from app.models import Config, WxUser
from service.Template import TemplateIdParams, TemplateContent
from service.Template03 import TemplateIdParams03, TemplateContent03
from service.utils import getWarnLevel
from service.wxutils import WxMessageUtil, get_access_token


def dispatch_message(xml_recv):
    """
    分发从微信服务器推送过来的消息
    :param xml_recv:
    :return:
    """
    try:
        fromUserName = xml_recv.find('ToUserName').text  # 开发者微信号
        toUserName = xml_recv.find('FromUserName').text  # 发送方帐号（一个OpenID）
        msgType = xml_recv.find('MsgType').text  # 消息类型
        if msgType == "text":
            reply = handlerText(xml_recv, toUserName, fromUserName)
        elif msgType == "event":
            reply = handlerEvent(xml_recv, toUserName, fromUserName)
        else:
            reply = "success"
        return reply
    except Exception as e:
        print(e)


def handlerText(xml_recv, toUserName, fromUserName):
    """
    处理文本消息
    :param xml_recv:
    :param toUserName:
    :param fromUserName:
    :return:
    """
    content = xml_recv.find('Content').text
    return WxMessageUtil.reply_text_message(toUserName, fromUserName, content)


def handlerEvent(xml_recv, toUserName, fromUserName):
    """
    处理关注和取消关注事件，点击菜单事件
    :param xml_recv:
    :param toUserName:
    :param fromUserName:
    :return:
    """
    eventType = xml_recv.find("Event").text
    if "subscribe" == eventType or "unsubscribe" == eventType:
        # 订阅/取消订阅事件
        createTime = xml_recv.find('CreateTime').text
        res = handlerSubscribe(createTime, eventType, toUserName)
        if res:
            reply = WxMessageUtil.reply_text_message(toUserName, fromUserName, "您好！欢迎订阅")
        else:
            reply = "success"
    elif "CLICK" == eventType:
        # 点击菜单事件
        eventKey = xml_recv.find("EventKey").text
        reply = handlerClick(toUserName, fromUserName, eventKey)
    elif "VIEW" == eventType:
        # 跳转事件
        eventKey = xml_recv.find("EventKey").text
        reply = handlerView(toUserName, fromUserName, eventKey)
    else:
        reply = "success"
    return reply


def handlerSubscribe(createTime, eventType, toUserName):
    """
    处理订阅以及取消订阅
    :param createTime: 推送消息时间
    :param eventType: 时间类型 subscribe 或者 unsubscribe
    :return: 订阅为True，取消订阅为False
    """
    if "subscribe" == eventType:
        defaults = {"subscribe_time": createTime, "subscribe": True}
        xuser, created = WxUser.objects.get_or_create(openId=toUserName, defaults=defaults)
        if not created:
            xuser.subscribe = True
            xuser.save()
        return True
    else:
        WxUser.objects.filter(openId=toUserName).update(subscribe=False, subscribe_time=createTime)
        return False


def handlerClick(toUserName, fromUserName, eventKey):
    if eventKey == "VIEW_PROFILE":
        return WxMessageUtil.reply_text_message(toUserName, fromUserName, "魔眼行为智慧用电系统，为您的用电安全保驾护航！")
    else:
        return "success"


def handlerView(toUserName, fromUserName, eventKey):
    """
    若为跳转事件直接返回openid
    :param toUserName:
    :param fromUserName:
    :param eventKey:
    :return:
    """
    return "success"


def handlerAccessToken():
    """
    刷新数据库中的access_token
    :return:
    """
    temp = get_access_token()
    accessToken = temp[0]
    expireTime = int(temp[1]) - 300
    nowStamp = int(time.time())
    if accessToken == "":
        print("error")
    else:
        setconfiga(ACCESS_TOKEN, accessToken, expireTime + nowStamp)
    return expireTime


def handlerSendWarningMessage(msg, user=None, isSuperuser=0):
    """
    处理获取的报警信息，转为微信下发数据
    :param WarnMessage:
    :return:
    """
    type = msg["type"]
    if type == "POWER":
        tip = "功率过大报警"
        deviceName = msg['location'] + "设备"
        tipMore = "报警功率为" + str(msg["value"])
        level = getWarnLevel(msg['source_id'], msg['ammeter_distination'], msg['ammeterId'])
        try:
            warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        except:
            warntime = msg['time']
        name = '--'
        code = '--'
        # if user is not None:
        #     name = user.name
        #     code = user.code
        # if isSuperuser == 1:
        #     other = '用户：' + str(name) + ' 学号：' + str(code) + '\n点击查看详情'
        # else:
        other = None
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime, other)
    elif type == "REMAIN_CUR":
        tip = "剩余电流危险报警"
        deviceName = msg['location'] + "魔眼设备"
        tipMore = "电路存在漏电风险！" if msg["value"] else "--"
        level = "三级"
        try:
            warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        except:
            warntime = msg['time']
        name = '--'
        code = '--'
        # if user is not None:
        #     name = user.name
        #     code = user.code
        # if isSuperuser == 1:
        #     other = '用户：' + str(name) + ' 学号：' + str(code) + '\n点击查看详情'
        # else:
        other = None
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime, other)
    elif type == "ARC":
        tip = "故障电弧危险报警"
        deviceName = msg['location'] + "设备"
        tipMore = '电弧异常！'  # + str(msg["value"]) + '次每三十秒'
        level = getWarnLevel(msg['source_id'], msg['ammeter_distination'], msg['ammeterId'])
        try:
            warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        except:
            warntime = msg['time']
        name = '--'
        code = '--'
        # if user is not None:
        #     name = user.name
        #     code = user.code
        # if isSuperuser == 1:
        #     other = '用户：' + str(name) + ' 学号：' + str(code) + '\n点击查看详情'
        # else:
        other = None
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime, other)
    elif type == "SMOKE":
        tip = "烟雾报警"
        deviceName = msg['location'] + "魔眼设备"
        tipMore = "正常" if msg["value"] else "异常"
        level = "三级"
        try:
            warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        except:
            warntime = msg['time']
        name = '--'
        code = '--'
        # if user is not None:
        #     name = user.name
        #     code = user.code
        # if isSuperuser == 1:
        #     other = '用户：' + str(name) + ' 学号：' + str(code) + '\n点击查看详情'
        # else:
        other = None
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime, other)
    elif type == "LIMIT_APP":
        # tip = "用电器长时间接入报警"
        # deviceName = msg['location'] + "魔眼设备"
        # tipMore = msg['valueAttach'] + "已接入" + \
        #           str(int((time.time() - int(msg["time"])) / 60)) + "分钟"
        # level = "三级"
        # warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        tip = "违规电器[" + msg['value'] + "]接入报警"
        deviceName = msg['location'] + "设备"
        tipMore = "用电器功率：" + msg['valueAttach'] + 'W'
        level = getWarnLevel(msg['source_id'], msg['ammeter_distination'], msg['ammeterId'])
        try:
            warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        except:
            warntime = msg['time']
        name = '--'
        code = '--'
        # if user is not None:
        #     name = user.name
        #     code = user.code
        # if isSuperuser == 1:
        #     other = '用户：' + str(name) + ' 学号：' + str(code) + '\n点击查看详情'
        # else:
        other = None
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime, other)
    elif type == "LINE_TEMP":
        tip = "线温异常报警"
        deviceName = msg['location'] + "魔眼设备"
        tipMore = '线温达到' + str(msg['value']) + "摄氏度"
        level = "三级"
        try:
            warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        except:
            warntime = msg['time']
        name = '--'
        code = '--'
        # if user is not None:
        #     name = user.name
        #     code = user.code
        # if isSuperuser == 1:
        #     other = '用户：' + str(name) + '学号：' + str(code) + '\n点击查看详情'
        # else:
        other = None
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime, other)

    elif type == "APP":
        tip = "大功率用电器长时间接入报警"
        deviceName = msg['location'] + "设备"
        tipMore = msg['value'] + '已接入' + str(int((time.time() - int(msg["time"])) / 60)) + "分钟"
        level = getWarnLevel(msg['source_id'], msg['ammeter_distination'], msg['ammeterId'])
        try:
            warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        except:
            warntime = msg['time']
        name = '--'
        code = '--'
        # if user is not None:
        #     name = user.name
        #     code = user.code
        # if isSuperuser == 1:
        #     other = '用户：' + str(name) + ' 学号：' + str(code) + '\n点击查看详情'
        # else:
        other = None
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime, other)

    elif type == "WHOLE_APP":
        type_check = int(float(msg['valueAttach']))
        if type_check >= 0:
            tip = "用电器接入提醒"
            deviceName = msg['location']
            tipMore = msg['value'] + ' 已接入'
        else:
            tip = "用电器移除提醒"
            deviceName = msg['location']
            tipMore = msg['value'] + ' 已移除'
        level = '--'
        try:
            warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        except:
            warntime = msg['time']
        name = '--'
        code = '--'
        # if user is not None:
        #     name = user.name
        #     code = user.code
        # if isSuperuser == 1:
        #     other = '用户：' + str(name) + ' 学号：' + str(code) + '\n点击查看详情'
        # else:
        other = None
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime, other)


def handlerSendReparingMessage(amt_unit, amt_addr, text):
    """
    处理获取的报修信息，转为微信下发数据
    :param RepairMessage:
    :return:
    """
    ammeter = str(amt_unit) + "号楼 " + str(amt_addr) + "室"
    repair_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    repair_text = text
    other = '请尽快前往处理！'
    return createSendReparingMsg(ammeter, repair_time, repair_text, other)


def createSendWarningMsg(tip, deviceName, tipMore, level, warntime, other=''):
    first = TemplateIdParams("🔺设备报警")
    if tip == "用电器接入提醒" or tip == "用电器移除提醒":
        first = TemplateIdParams("设备接入/移除通知")
    remark = TemplateIdParams(other)
    keywordArgs = [
        TemplateIdParams(tip),
        TemplateIdParams(deviceName),
        TemplateIdParams(tipMore),
        TemplateIdParams(level),
        TemplateIdParams(warntime)
    ]
    return TemplateContent(first, remark, *keywordArgs)


def createSendReparingMsg(ammeter, repair_time, text, other=''):
    first = TemplateIdParams03("您有一条新的设备报修信息！")
    remark = TemplateIdParams03(other)
    keywordArgs = [
        TemplateIdParams03(ammeter),
        TemplateIdParams03(repair_time),
        TemplateIdParams03(text)
    ]
    return TemplateContent03(first, remark, *keywordArgs)
