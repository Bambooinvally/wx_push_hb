import datetime
import time

from app.configutils import setconfiga, ACCESS_TOKEN, getconfigattached
from app.models import Config, WxUser
from service.Template import TemplateIdParams, TemplateContent
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
        xuser,created = WxUser.objects.get_or_create(openId=toUserName, defaults=defaults)
        if not created:
            xuser.subscribe = True
            xuser.save()
        return True
    else:
        WxUser.objects.filter(openId=toUserName).update(subscribe=False, subscribe_time=createTime)
        return False


def handlerClick(toUserName, fromUserName, eventKey):
    if eventKey == "VIEW_PROFILE":
        return WxMessageUtil.reply_text_message(toUserName, fromUserName, "您好！这里是杭州华炳的简介")
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
    expireTime = int(temp[1])-10
    nowStamp = int(time.time())
    if accessToken == "":
        print("error")
    else:
        setconfiga(ACCESS_TOKEN, accessToken, expireTime + nowStamp)
    return expireTime


def handlerSendWarningMessage(msg):
    """
    处理获取的报警信息，转为微信下发数据
    :param WarnMessage:
    :return:
    """
    type = msg["type"]
    if type == "POWER":
        tip = "功率过大报警"
        deviceName = msg['location'] + "魔眼设备"
        tipMore = "报警功率为" + str(msg["value"])
        level = "三级"
        warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime)
    elif type == "REMAIN_CUR":
        tip = "剩余电流危险报警"
        deviceName = msg['location'] + "魔眼设备"
        tipMore = "正常" if msg["value"] else "异常"
        level = "三级"
        warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime)
    elif type == "ARC":
        tip = "故障电弧危险报警"
        deviceName = msg['location'] + "魔眼设备"
        tipMore = "正常" if msg["value"] else "异常"
        level = "三级"
        warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime)
    elif type == "SMOKE":
        tip = "烟雾报警"
        deviceName = msg['location'] + "魔眼设备"
        tipMore = "正常" if msg["value"] else "异常"
        level = "三级"
        warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime)
    elif type == "APP":
        tip = "用电器长时间接入报警"
        deviceName = msg['location'] + "魔眼设备"
        tipMore = msg['valueAttach'] + "已接入" + \
                  str(int((time.time() - int(msg["time"])) / 60)) + "分钟"
        level = "三级"
        warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime)
    elif type == "LINE_TEMP":
        tip = "线温报警危险"
        deviceName = msg['location'] + "魔眼设备"
        tipMore = msg['valueAttach'] + "已接入"
        level = "三级"
        warntime = datetime.datetime.fromtimestamp(int(msg["time"])).strftime("%Y-%m-%d %H:%M:%S")
        return createSendWarningMsg(tip, deviceName, tipMore, level, warntime)


def createSendWarningMsg(tip, deviceName, tipMore, level, warntime):
    first = TemplateIdParams("设备报警")
    remark = TemplateIdParams("查看详细信息")
    keywordArgs = [
        TemplateIdParams(tip),
        TemplateIdParams(deviceName),
        TemplateIdParams(tipMore),
        TemplateIdParams(level),
        TemplateIdParams(warntime)
    ]
    return TemplateContent(first, remark, *keywordArgs)
