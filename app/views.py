import datetime
import hashlib
import json
import time

from xml.etree import ElementTree as ET

import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.configutils import getconfig, Project
from app.models import WxUser, UnconfirmUser, get_or_none, Ammeters, ConfirmedUser, SuperUser
from app.wxHandler import dispatch_message
from service.Template import TemplateContent, TemplateIdParams
from service.Template02 import TemplateContent02, TemplateIdParams02
from service.utils import ChooseUrl
from service.wxconfig import WEBURL, APPID, SECTET, GET_OPENID_URL, GET_CODE, SUPERUSER_LOGIN, GET_HISTORY, FAULT_REPAIR
from service.wxutils import WxMenuUtil, WxMessageUtil, get_access_token
from urllib import parse

from wx_push import specsetting
from wx_push.specsetting import SUPERUSER_LOGIN_URL, ADMIN_TAG, VERIFY_STU_HDU_URL


def recv_message(request):
    """
    接收微信推送来的消息，并回复
    :param request:
    :return:
    """
    token = "ping"
    signature = request.GET.get('signature', '')
    timestamp = request.GET.get('timestamp', '')
    nonce = request.GET.get('nonce', '')
    echostr = request.GET.get('echostr', 'success')
    s = [timestamp, nonce, token]
    s.sort()
    s = ''.join(s)
    if request.method == "POST":
        if hashlib.sha1(s.encode('utf-8')).hexdigest() == signature:
            data = request.body
            xml_recv = ET.fromstring(data)
            xml_response = dispatch_message(xml_recv)
            # print(data)
            return HttpResponse(xml_response,
                                content_type="text/html; charset=UTF-8")
    elif request.method == "GET":
        if hashlib.sha1(s.encode('utf-8')).hexdigest() == signature:
            return HttpResponse(echostr,
                                content_type="text/html; charset=UTF-8")
    return HttpResponse(echostr,
                        content_type="text/html; charset=UTF-8")


def create_menu(request):
    """
    创建菜单
    :param request:
    :return:
    """
    access_token = getconfig("access_token", "")
    menu = {
        "button": [
            {
                "type": "click",
                "name": "查看简介",
                "key": "VIEW_PROFILE"
            },
            {
                "name": "菜单",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "绑定账号",
                        "url": GET_CODE
                    },
                    {
                        "type": "view",
                        "name": "查看历史扣分记录",
                        "url": GET_HISTORY
                    },
                    {
                        "type": "view",
                        "name": "障碍报修",
                        "url": FAULT_REPAIR
                    },
                    # 小程序暂时不关联
                    # {
                    #     "type": "miniprogram",
                    #     "name": "wxa",
                    #     "url": "http://mp.weixin.qq.com",
                    #     "appid": "wx286b93c14bbf93aa",
                    #     "pagepath": "pages/lunar/index"
                    # },
                    # {
                    #     "type": "click",
                    #     "name": "赞一下我们",
                    #     "key": "V1001_GOOD"
                    # }
                ]
            }
        ],
    }
    # print('in create menu access token is:'+str(access_token))
    return HttpResponse(WxMenuUtil.create_menu(access_token, menu).decode())


def create_superMenu(request):
    """
    创建菜单
    :param request:
    :return:
    """
    access_token = getconfig("access_token", "")
    menu = {
        "button": [
            {
                "type": "click",
                "name": "查看简介",
                "key": "VIEW_PROFILE"
            },
            {
                "name": "菜单",
                "sub_button": [
                    {
                        "type": "view",
                        "name": "绑定账号",
                        "url": GET_CODE
                    },
                    # {
                    #     "type": "view",
                    #     "name": "修改个人信息",
                    #     "url": GET_CODE
                    # },
                    {
                        "type": "view",
                        "name": "管理员登录",
                        "url": SUPERUSER_LOGIN,
                        "key": 'admin_login'
                    },
                    # {
                    #     "type": "view",
                    #     "name": "测试功能",
                    #     "url": SUPERUSER_LOGIN,
                    #     "key": 'test'
                    # },
                    {
                        "type": "view",
                        "name": "查看历史扣分记录",
                        "url": GET_HISTORY
                    },
                    {
                        "type": "view",
                        "name": "障碍报修",
                        "url": FAULT_REPAIR
                    },
                    # 小程序暂时不关联
                    # {
                    #     "type": "miniprogram",
                    #     "name": "wxa",
                    #     "url": "http://mp.weixin.qq.com",
                    #     "appid": "wx286b93c14bbf93aa",
                    #     "pagepath": "pages/lunar/index"
                    # },
                    # {
                    #     "type": "click",
                    #     "name": "赞一下我们",
                    #     "key": "V1001_GOOD"
                    # }
                ]
            }

        ],
        "matchrule": {
            "tag_id": ADMIN_TAG
        }
    }
    # print('in create menu access token is:'+str(access_token))
    return HttpResponse(WxMenuUtil.create_addconditionalMenu(access_token, menu).decode())


def del_menu(request):
    """
    删除菜单
    :param request:
    :return:
    """
    access_token = getconfig("access_token", "")
    return HttpResponse(WxMenuUtil.del_menu(access_token).decode())


def getAppParams(request):
    if request.method == 'POST':
        code = request.POST.get('code', -1)
        if code != -1:
            req = requests.get(GET_OPENID_URL % code)
            msg = json.loads(req.content.decode())
            user_openId = msg.get('openid', '')
            data = {
                'openid': user_openId
            }
            return HttpResponse(json.dumps(data),
                                content_type="json/html; charset=UTF-8")
    return HttpResponse("{}",
                        content_type="json/html; charset=UTF-8")


def register(request):
    """
    微信上传认证的界面
    :param request:
    :return:
    """
    if request.method == 'POST':
        name = request.POST.get("name")
        phone = request.POST.get("phone")
        code = request.POST.get("code")
        address = request.POST.get("address")
        openId = request.POST.get("openId")
        source_id = request.POST.get('source_id')
        distination = request.POST.get('distination')
        ammeter_app_code = request.POST.get('board_id')
        statue = '请使用微信打开'
        print("ammeter_app_code:", ammeter_app_code, "name:", name, "code:", code, "phone:", phone,
              "address:", address, "openId:", openId, "distination:", distination)

        if openId and name and code:
            print("进入了创建")
            # TODO **************首先先进行判断是否存在此人，如果不存在直接返回失败***************
            data = {"name": name, "code": code, "ammeter_app_code": ammeter_app_code}
            print(data)
            print("source_id is",source_id)
            url = ChooseUrl(source_id, "VERIFY_STU_URL")
            print("url is",url)
            student = requests.get(url, json=data)
            student = student.content.decode('utf-8')
            student = json.loads(student)
            print(student)
            if student['status'] is False:
                statue = '身份信息有误，请重新输入'
            else:
                time = datetime.datetime.now()
                print(time)
                # users = UnconfirmUser.objects.filter(openId=openId).first()
                # if users is not None:
                #     print("创建失败")
                #     statue = '您已提交过绑定申请，无需再次提交'
                # else:
                #     user = UnconfirmUser.objects.create(name=name, code=code, address=address, createTime=time,
                #                                         openId=openId)
                #     print("创建成功")
                #     user.ammeter.add(Ammeters.objects.get(source_id=source_id, ammeter_app_code=ammeter_app_code))
                #     statue = '提交成功，请等待管理员审核'
                ischeck = ConfirmedUser.objects.filter(openId=openId).first()
                if ischeck is None:
                    obj, iscreate = UnconfirmUser.objects.get_or_create(openId=openId,
                                                                        defaults={"name": name, "code": code,
                                                                                  "address": address,
                                                                                  "createTime": time,
                                                                                  "openId": openId})
                    if iscreate:
                        print('source_id:', source_id)
                        print('ammeter_app_code:', ammeter_app_code)
                        obj.ammeter.add(Ammeters.objects.get(source_id=source_id, id=ammeter_app_code))
                        print("创建成功")
                        statue = '提交成功，请等待管理员审核'
                        access_token = getconfig('access_token', '')
                        WxMessageUtil.send_reg_message(access_token=access_token,
                                                       openId=openId,
                                                       templateId='GHqdDOjO5SeQ0LWnGqWPaHjQ0XIp9DQTCUEBpB3w-o0',
                                                       miniPorgramParams=None,
                                                       template_data=TemplateContent02(TemplateIdParams02('状态更新提醒'),
                                                                                       TemplateIdParams02('您的注册申请已提交'),
                                                                                       TemplateIdParams02(obj.code),
                                                                                       TemplateIdParams02(obj.name),
                                                                                       TemplateIdParams02('待审核'),
                                                                                       TemplateIdParams02(str(obj.createTime))))
                        return HttpResponse(json.dumps({'statue': statue}), content_type="json/html; charset=UTF-8")
                    else:
                        print("创建失败")
                        statue = '您已提交过绑定申请，无需再次提交'
                else:
                    print("创建失败")
                    statue = '您已绑定，请勿重复操作'
            # TODO ******************************END********************************
        return HttpResponse(json.dumps({'statue': statue}),
                            content_type="json/html; charset=UTF-8")
    elif request.method == 'GET':
        status = 'uncheck'
        openId = request.GET.get('openId', -1)
        print(openId)
        # code = request.GET.get('code', -1)
        # if code != -1:
        #     req = requests.get(GET_OPENID_URL % code)
        #     msg = json.loads(req.content.decode())
        #     openId = msg.get('openid', '')
        #     print(openId)
        if openId != -1:
            cf_ischeck = ConfirmedUser.objects.filter(openId=openId).first()
            if cf_ischeck is not None:
                status = 'checked'
            else:
                ucf_ischeck = UnconfirmUser.objects.filter(openId=openId).first()
                if ucf_ischeck is not None:
                    status = 'wait'
                else:
                    is_root = SuperUser.objects.filter(openId=openId).first()
                    if is_root is not None:
                        status = 'uncheck'
            print('status:', status)
            projects = Project.objects.all()
            data = []
            province_city = {}
            provinces = [x['province'] for x in projects.values('province').distinct()]
            projectName = [x['projectname'] for x in projects.values('projectname')]
            source_id = [x['source_id'] for x in projects.values('source_id')]
            for province in provinces:
                # 获取省下面的市
                province_city[province] = {x['city']: None for x in projects.filter(province=province).values('city')}
                print(province_city)
                for city in province_city[province].keys():
                    city_projects = [{x['source_id']: x['projectname']} for x in
                                     projects.filter(province=province, city=city).values('source_id', 'projectname')]
                    if province_city[province][city] is None:
                        province_city[province][city] = []
                    province_city[province][city].append(city_projects)
                data.append({province: province_city[province]})
                print(data)
            return render_to_response('register.html', {'data': data, 'status': status, 'openId': openId})
        else:
            return render_to_response('404.html')

# def getAmmeters(request):
#     source_id = request.POST.get('source_id')
#     ammeters = Ammeters.objects.filter(source_id = source_id)
#     data = []
#     for ammeter in ammeters:
#         message = {
#             'addr':ammeter.ammeter_addr,
#             'ammeter_app_code':ammeter.ammeter_app_code,
#             'domain':ammeter.domain
#         }
#         data.append(message)
#     # print(source_id,data)
#     return HttpResponse(json.dumps(data),content_type="json/html; charset=UTF-8")


def getAmmeters(request):
    """获取设备号"""
    source_id = request.POST.get('source_id')
    print('source_id:', source_id)
    # ammeters = Ammeters.objects.values("ammeter_unit").filter(source_id = source_id).values("ammeter_unit","ammeter_info","ammeter_app_code","ammeter_sensorId")
    # ammeters = Ammeters.objects.filter(source_id=source_id)
    data = []
    units = Ammeters.objects.filter(source_id=source_id).values("ammeter_unit").distinct()
    for unit in units:
        unit_info = {}
        # 获取到某一幢楼的所有设备
        unit_id = unit.get('ammeter_unit')
        if unit_id is not None:
            print('unit_id:', unit_id)
            unit_info['label'] = str(unit_id) + "幢"
            unit_info['value'] = str(unit_id) + "幢"
            unit_info['children'] = []
            ammeters = Ammeters.objects.filter(source_id=source_id, ammeter_unit=unit.get('ammeter_unit')).order_by(
                "ammeter_info")
            # 用于储存设备的信息
            ammeter_dict = {}
            # 遍历一遍，获得设备信息，按照层号分
            for ammeter in ammeters:
                # label，value
                # 用一个dict 存储
                room = ammeter.ammeter_info
                print('room:', room)
                # 房间号格式为 4-404 如果不是这样会出错
                if room != '--' and room != '实验室测试' and room != None:
                    temp = room.split('-')
                    roomStorey = temp[0]
                    roomNumber = temp[1]
                    if not ammeter_dict.__contains__(roomStorey):
                        ammeter_dict[roomStorey] = []
                    ammeter_dict[roomStorey].append({"roomNumber": roomNumber, "ammeter_id": ammeter.pk,
                                                     "app_code": ammeter.ammeter_app_code,
                                                     "sensorId": ammeter.ammeter_sensorId})
            for info in ammeter_dict:
                ret = {"label": str(info) + "楼", "value": str(info) + "楼", "children": []}
                rooms = ammeter_dict.get(info)
                for room in rooms:
                    ret["children"].append({"label": room['roomNumber'], 'value': room['ammeter_id'],
                                            'app_code': room['app_code'], 'sensorId': room['sensorId']})
                unit_info['children'].append(ret)
            data.append(unit_info)

    # for ammeter in ammeters:
    #
    #
    #
    #     message = {
    #         'ammeter_info':ammeter.ammeter_info,
    #         'ammeter_unit':ammeter.ammeter_unit,
    #         'ammeter_app_code':ammeter.ammeter_app_code,
    #     }
    #     data.append(message)
    # # print(source_id,data)
    print(data)
    return HttpResponse(json.dumps(data), content_type="json/html; charset=UTF-8")


def verify(request):
    return HttpResponse('dlUHfQ1hxd6SwBwe')


def test(request):
    access_token = getconfig('access_token', '')
    WxMessageUtil.send_message_by_openid(access_token=access_token, openId='o-XSVwRj5uPsuu4C3ckFLpsxqPsc',
                                         templateId='0ZP2vzOjx3UpQgIMZYdHsR6SxGuZbGW2Tmtrv3RY5xw',
                                         miniPorgramParams=None,
                                         template_data=TemplateContent(TemplateIdParams('xxx报警'),
                                                                       TemplateIdParams('备注'),
                                                                       TemplateIdParams('xxx电弧危险'),
                                                                       TemplateIdParams('xxx小区xxx室'),
                                                                       TemplateIdParams('123'),
                                                                       TemplateIdParams('高'),
                                                                       TemplateIdParams('2020年3月18日20:33')))
    return HttpResponse('ok')


"""
需要添加3个功能：
1. 个人信息的修改操作：用户可以修改自己的信息（注意是否审核过，分两种情况显示）
2. 管理员功能：
    2.1 管理员修改用户信息
    2.2 管理员审核的注册信息（同意就开通用户推送）

"""
