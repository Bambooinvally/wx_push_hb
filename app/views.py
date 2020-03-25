import hashlib
import json
import time

from xml.etree import ElementTree as ET

import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response

from app.configutils import getconfig, Project
from app.models import WxUser, UnconfirmUser, get_or_none, Ammeters
from app.wxHandler import dispatch_message
from service.Template import TemplateContent, TemplateIdParams
from service.wxconfig import WEBURL, APPID, SECTET, GET_OPENID_URL, GET_CODE, SUPERUSER_LOGIN
from service.wxutils import WxMenuUtil, WxMessageUtil, get_access_token
from urllib import parse

from wx_push import specsetting
from wx_push.specsetting import SUPERUSER_LOGIN_URL


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
                    # {
                    #     "type": "view",
                    #     "name": "修改个人信息",
                    #     "url": GET_CODE
                    # },
                    # 小程序暂时不关联
                    # {
                    #     "type": "miniprogram",
                    #     "name": "wxa",
                    #     "url": "http://mp.weixin.qq.com",
                    #     "appid": "wx286b93c14bbf93aa",
                    #     "pagepath": "pages/lunar/index"
                    # },
                    {
                        "type": "click",
                        "name": "赞一下我们",
                        "key": "V1001_GOOD"
                    }]
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
                    {
                        "type": "view",
                        "name": "修改个人信息",
                        "url": GET_CODE
                    },
                    {
                        "type": "view",
                        "name": "管理员登录",
                        "url": SUPERUSER_LOGIN,
                        "key": 'admin_login'
                    },
                    # 小程序暂时不关联
                    # {
                    #     "type": "miniprogram",
                    #     "name": "wxa",
                    #     "url": "http://mp.weixin.qq.com",
                    #     "appid": "wx286b93c14bbf93aa",
                    #     "pagepath": "pages/lunar/index"
                    # },
                    {
                        "type": "click",
                        "name": "赞一下我们",
                        "key": "V1001_GOOD"
                    }]
            }

        ],
        "matchrule": {
            "tag_id": "101"
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
        address = request.POST.get("address")
        openId = request.POST.get("openId")
        source_id = request.POST.get('source_id')
        ammeter_app_code = request.POST.get('board_id')
        statue = '请使用微信打开'
        if openId and name and phone:
            obj, iscreate = UnconfirmUser.objects.get_or_create(openId=openId,
                                                                defaults={"name": name, "phone": phone, "address": address,
                                                                          "openId": openId})
            if iscreate:
                obj.ammeter.add(Ammeters.objects.get(source_id=source_id, ammeter_app_code=ammeter_app_code))
                statue = '提交成功，请等待管理员审核'
            else:
                statue = '您已提交过绑定申请，无需再次提交'

        return HttpResponse(json.dumps({'statue':statue}),
                                content_type="json/html; charset=UTF-8")
    else:
        projects = Project.objects.all()
        data = []
        province_city={}

        provinces =  [x['province'] for x in projects.values('province').distinct()]
        projectName = [x['projectname'] for x in projects.values('projectname')]
        source_id = [x['source_id'] for x in projects.values('source_id')]
        for province in provinces:
            # 获取省下面的市
            province_city[province] = {x['city']:None for x in projects.filter(province=province).values('city')}
            # print(province_city)
            for city in province_city[province].keys():
                city_projects = [{x['source_id']:x['projectname']} for x in projects.filter(province=province,city=city).values('source_id','projectname')]
                if province_city[province][city] is None:
                    province_city[province][city] = []
                province_city[province][city].append(city_projects)
            data.append({province:province_city[province]})

        return render_to_response('register.html',{'data':data})


def getAmmeters(request):
    source_id = request.POST.get('source_id')
    ammeters = Ammeters.objects.filter(source_id = source_id)
    data = []
    for ammeter in ammeters:
        message = {
            'addr':ammeter.ammeter_addr,
            'ammeter_app_code':ammeter.ammeter_app_code,
            'domain':ammeter.domain
        }
        data.append(message)
    # print(source_id,data)
    return HttpResponse(json.dumps(data),content_type="json/html; charset=UTF-8")

def verify(request):
    return HttpResponse('CoynMqa4m1dQm42K')


def test(request):
    access_token = getconfig('access_token','')
    WxMessageUtil.send_message_by_openid(access_token=access_token,openId='o-XSVwRj5uPsuu4C3ckFLpsxqPsc',
                                         templateId='0ZP2vzOjx3UpQgIMZYdHsR6SxGuZbGW2Tmtrv3RY5xw',miniPorgramParams=None,
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

