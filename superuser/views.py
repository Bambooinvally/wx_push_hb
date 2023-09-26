import datetime
import json
import random
import re
import time
from functools import wraps

import requests
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core import serializers
from django.core.urlresolvers import reverse
from django.db.models import Q
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404

from app.configutils import getconfig, Ammeters, ConfirmedUser, Project, ACCESS_TOKEN
from service.Template import TemplateContent, TemplateIdParams
from service.Template02 import TemplateContent02, TemplateIdParams02
from service.utils import simuWarn, generateMD5, ChooseUrl
from service.wxconfig import TEMPLATE_ID
from service.wxutils import WxUserTagUtil, WxMessageUtil
# Create your views here.
from django.contrib.auth import logout, authenticate

from app.models import UnconfirmUser, WxUser, get_or_none, SuperUser, URLSource
from superuser.permissionUtils import getAdminPermission, admin_required, adminCheck, getAdminAmmeter
from wx_push.specsetting import ADMIN_TAG, HDU_SOURCE_URL, HISTORY_EVENT_HDU_URL, SUPER_REPAIR_URL


class PasswordError(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class LoginBackend(object):
    def authenticate(self, username, password):
        user = User.objects.get(username=username)
        if user.password == password:
            return user
        else:
            raise PasswordError('密码错误')

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


def my_login(request):
    if request.method == 'GET':
        vrf = random.uniform(10, 20)
        pagedatas = {
            'request': request,
            'vrf': vrf
        }
        request.session['vrf'] = vrf
        # print(vrf)
        return render_to_response('login.html', pagedatas)
    elif request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        vrf = request.POST.get('vrf', '')
        if str(request.session['vrf']) != vrf:
            return HttpResponse("gundanba")
        try:
            user = authenticate(username=username, password=password)
        except PasswordError:
            return HttpResponseRedirect(reverse('manage-login') + '?err=true&msg=密码不正确!')
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse('manage-login') + '?err=true&msg=账号不存在!')
        else:
            request.session['username'] = username
            login(request, user)
            if user.is_superuser:
                return HttpResponseRedirect(reverse('permission-assign'))
            else:
                return HttpResponse('没有权限')
    else:
        return HttpResponse("gundan")


def wx_login(request):
    """
    使用微信的openid进行管理员认证
    :param request:
    :return:
    """
    if request.method == 'GET':
        return render_to_response('wxlogin.html')
    elif request.method == 'POST':
        openId = request.POST.get('openid', '')
        if adminCheck(openId):
            result = {'status': 'success'}
            request.session['openid'] = openId
        else:
            result = {'status': 'failed'}
        return HttpResponse(json.dumps(result, ensure_ascii=True), content_type='text/json; charset=utf-8')


@admin_required
def my_logout(request):
    request.session.clear()
    return HttpResponse('本次登录已注销')


"""
2. 管理员功能：
    2.1 管理员修改用户信息
    2.2 管理员审核的注册信息（同意就开通用户推送）
"""


@admin_required
def modify_user_info(request):
    pk = int(request.GET.get("pk", "-1"))
    if request.method == "POST":
        if pk < 0:
            pk = int(request.POST.get("pk", "-1"))
        users = WxUser.objects.filter(pk=pk)
        if len(users) == 1:
            user = users.first()
            user.name = request.POST.get("name", user.name)
            user.phone = request.POST.get("phone", user.phone)
            user.IDcard = request.POST.get("IDcard", user.IDcard)
            user.address = request.POST.get("address", user.address)
            user.save()
            return render_to_response("userInfo.html", {"user": user, "request": request})
        else:
            return HttpResponse("error")
    else:
        # user = get_object_or_404(WxUser, pk=pk)
        # return render_to_response("userInfo.html", {"user": user, "request": request})
        user = ConfirmedUser.objects.filter(id=pk).first()
        if user is not None:
            requestBody = {"ammeter": []}
            # ammeters = user.ammeter.through.objects.all()
            ammeters = user.ammeter.all()
            print(ammeters)
            # TODO *********************此处增加了报警信息和分数查询*********************
            for ammeter in ammeters:
                ammeter_app_code = ammeter.ammeter_app_code
                ammeter_sensorId = ammeter.ammeter_sensorId
                ammeter_info = {"ammeter_app_code": ammeter_app_code, "ammeter_sensorId": ammeter_sensorId,
                                "ammeter_info_": ammeter.ammeter_info,
                                "ammeter_unit": ammeter.ammeter_unit}
                requestBody["ammeter"].append(ammeter_info)
            print(requestBody)
            # re = requests.post(HISTORY_EVENT_HDU_URL, json=requestBody)
            re = requests.post(HISTORY_EVENT_HDU_URL, json=requestBody)
            re = re.content.decode('utf-8')  # 这是一个string类型
            re = json.loads(re)  # 将字符串转为字典类型
            # 合并两个字典
            data = requestBody.copy()
            data.update(re)
            print(data)
            # return HttpResponse(re.content, content_type="json/html; charset=UTF-8")
            return render_to_response("userInfo.html", {"user": user, 'data': data, "request": request})
            # TODO ****************************END*****************************
        else:
            return render_to_response('userInfo.html', {"user": '', 'data': '', "request": request})


@admin_required
def search_user(request):
    if request.method == "POST":
        qdata = request.POST.get("qdata", "")
        qtype = request.POST.get("qtype", "")
        users = []
        if qtype == "name":
            users = ConfirmedUser.objects.filter(name__startswith=qdata)
        elif qtype == "code":
            users = ConfirmedUser.objects.filter(code__startswith=qdata)
        if len(users) > 0:
            return render_to_response("searchUser.html", {"users": users, "request": request})
    return render_to_response("searchUser.html", {"request": request})


@admin_required
def verify_user_info(request):
    """
    已加入权限
    :param request:
    :return:
    """
    if request.method == "POST":
        openId = request.POST.get("openId", "")
        verify = True if request.POST.get("verify", -1) == '1' else False
        uusers = UnconfirmUser.objects.filter(openId=openId)
        if verify is False:
            for uuserss in uusers:
                access_token = getconfig('access_token', '')
                WxMessageUtil.send_reg_message(access_token=access_token,
                                               openId=openId,
                                               templateId='GHqdDOjO5SeQ0LWnGqWPaHjQ0XIp9DQTCUEBpB3w-o0',
                                               miniPorgramParams=None,
                                               template_data=TemplateContent02(TemplateIdParams02('状态更新提醒'),
                                                                               TemplateIdParams02('您的注册审核未通过，请重新申请!'),
                                                                               TemplateIdParams02(uuserss.code),
                                                                               TemplateIdParams02(str(uuserss.name)),
                                                                               TemplateIdParams02('审核未通过'),
                                                                               TemplateIdParams02(str(uuserss.createTime))))
            uusers.delete()  # 删除记录
            print('delte user')
            # 返回剩余未审核用户
            return HttpResponse(json.dumps(
                {"data": serializers.serialize('json', UnconfirmUser.objects.all()), "state": True, "msg": "ok"}),
                content_type="json/html; charset=UTF-8")
        # return HttpResponse(json.dumps(
        #     {"data": serializers.serialize('json', UnconfirmUser.objects.all()), "state": True, "msg": "ok"}),
        #     content_type="json/html; charset=UTF-8")
        print(openId, len(openId), verify, uusers)
        if len(uusers) == 1:
            source_permit, domain_permit = getAdminPermission(request)
            # source_permit, domain_permit = [1, 2, 3, 4], [1, 2, 3, 4]
            uuser = uusers.first()
            # print(uuser.ammeter.values())
            wxuser = get_or_none(ConfirmedUser, openId=uuser.openId)
            # print(wxuser)
            # 判断用户是否已经审核通过
            if wxuser is None:
                try:
                    wxuser = ConfirmedUser.objects.create(openId=uuser.openId, name=uuser.name, phone=uuser.phone,
                                                          address=uuser.address, IDcard=uuser.IDcard, createTime=uuser.createTime,
                                                          extraInfo=uuser.extraInfo, code=uuser.code)
                    print(uuser.code)
                    for amt in uuser.ammeter.all():
                        wxuser.ammeter.add(amt)  # 将设备与用户绑定
                    # TODO 将信息上传到对应项目的后台，将学生和设备绑定并获取状态
                    ammeter_app_code = wxuser.ammeter.all()[0].ammeter_app_code
                    ammeter_sensorId = wxuser.ammeter.all()[0].ammeter_sensorId
                    source_id = wxuser.ammeter.all()[0].source_id
                    # urls = chooseUrls(source_id)
                    urls = ChooseUrl(source_id,"SOURCE_URL")
                    data = requests.get(urls, params={'name': wxuser.name, 'code': wxuser.code,
                                                      'ammeter_app_code': ammeter_app_code,
                                                      'ammeter_sensorId': ammeter_sensorId})
                    data = json.loads(data.content.decode('utf-8'))
                    print('data:', data)
                    # print('name:', wxuser.name)
                    # print('code:', wxuser.code)
                    access_token = getconfig('access_token', '')
                    print(access_token)
                    WxMessageUtil.send_reg_message(access_token=access_token,
                                                   openId=openId,
                                                   templateId='GHqdDOjO5SeQ0LWnGqWPaHjQ0XIp9DQTCUEBpB3w-o0',
                                                   miniPorgramParams=None,
                                                   template_data=TemplateContent02(TemplateIdParams02('状态更新提醒'),
                                                                                   TemplateIdParams02('您的注册审核已通过'),
                                                                                   TemplateIdParams02(wxuser.code),
                                                                                   TemplateIdParams02(str(wxuser.name)),
                                                                                   TemplateIdParams02('审核通过'),
                                                                                   TemplateIdParams02(str(uuser.createTime))))
                    uuser.delete()  # 删除待审核记录
                except Exception as e:
                    print(e)
            else:
                # 更新用户
                wxuser.phone = uuser.phone
                wxuser.name = uuser.name
                wxuser.IDcard = uuser.IDcard
                wxuser.address = uuser.address
                wxuser.code = uuser.code
                wxuser.ammeter.clear()
                for amt in uuser.ammeter.all():
                    wxuser.ammeter.add(amt)  # 将设备与用户绑定
                wxuser.save()
                # TODO 将信息上传到hdu后台，将学生和设备绑定更新并获取状态
                ammeter_app_code = wxuser.ammeter.all()[0].ammeter_app_code
                ammeter_sensorId = wxuser.ammeter.all()[0].ammeter_sensorId
                source_id = wxuser.ammeter.all()[0].source_id
                # urls = chooseUrls(source_id)
                urls = ChooseUrl(source_id,"SOURCE_URL")
                data = requests.get(urls, params={'name': wxuser.name, 'code': wxuser.code,
                                                  'ammeter_app_code': ammeter_app_code,
                                                  'ammeter_sensorId': ammeter_sensorId})
                data = json.loads(data.content.decode('utf-8'))
                print('data:', data)
                access_token = getconfig('access_token', '')
                print(access_token)
                WxMessageUtil.send_reg_message(access_token=access_token,
                                               openId=openId,
                                               templateId='GHqdDOjO5SeQ0LWnGqWPaHjQ0XIp9DQTCUEBpB3w-o0',
                                               miniPorgramParams=None,
                                               template_data=TemplateContent02(TemplateIdParams02('状态更新提醒'),
                                                                               TemplateIdParams02('您的信息更新审核通过'),
                                                                               TemplateIdParams02(wxuser.code),
                                                                               TemplateIdParams02(str(wxuser.name)),
                                                                               TemplateIdParams02('审核通过'),
                                                                               TemplateIdParams02(str(uuser.createTime))))
                uuser.delete()
            # return HttpResponse(json.dumps(
            #     {"data": serializers.serialize('json', UnconfirmUser.objects.filter(ammeter__source__in=source_permit,
            #                                                                         ammeter__domain__in=domain_permit)),
            #      "state": True, "msg": "ok"}),
            #     content_type="json/html; charset=UTF-8")
            return HttpResponse(json.dumps(
                {"data": serializers.serialize('json', UnconfirmUser.objects.all()), "state": True, "msg": "ok"}),
                content_type="json/html; charset=UTF-8")
        else:
            print('here')
            return HttpResponse(json.dumps({"msg": "无此用户", "state": False}),
                                content_type="json/html; charset=UTF-8")

    #  获取页面
    else:
        source_permit, domain_permit = getAdminPermission(request)
        # source_permit, domain_permit = [1, 2, 3, 4], [1, 2, 3, 4]
        # 获取管理员所管辖的所有未审核用户
        uncofirmUsers = UnconfirmUser.objects.filter(ammeter__source__in=source_permit,
                                                     ammeter__domain__in=domain_permit)
        return render_to_response("verifyUser.html", {"uncofirmUsers": uncofirmUsers})


@admin_required
def confirmed_user_info(request):
    """已通过审核的用户"""
    source_permit, domain_permit = getAdminPermission(request)
    # source_permit, domain_permit = [1,2,3,4], [0,1,2,3,4,5,6,7,8,9,10]
    confirmedUsers = ConfirmedUser.objects.filter(ammeter__source__in=source_permit,
                                                  ammeter__domain__in=domain_permit)
    if request.method == 'GET':
        currentSource = request.GET.get('source_id', source_permit[0])
        allProject = Project.objects.filter(source_id__in=source_permit)
        if len(source_permit) == 1:
            project = Project.objects.get(source_id=source_permit[0])
        else:
            project = Project.objects.get(source_id=currentSource)
        confirmedUsers = confirmedUsers.filter(ammeter__source=currentSource)
        # 这里的project指的是被选中的项目
        return render_to_response("showUser.html", {"confirmedUsers": confirmedUsers,
                                                    "project": project, "allProject": allProject})
    elif request.method == 'POST':
        # {"openId": openId.replace( /\s + / g, ""), "source_id": source_id, "ammeter_app_code": ammeter_app_code}
        openId = request.POST.get('openid')
        sourceId = request.POST.get('source_id')
        code = request.POST.get('ammeter_app_code')
        sensorId = request.POST.get('sensorId')
        previous_code = request.POST.get('previous_code')
        previous_sensor = request.POST.get('previous_sensor')
        print(openId, sourceId, code, previous_code)
        # 生效修改
        amt_nw = Ammeters.objects.get(source_id=sourceId, ammeter_app_code=code, ammeter_sensorId=sensorId)
        amt_bf = Ammeters.objects.get(source_id=sourceId, ammeter_app_code=previous_code,
                                      ammeter_sensorId=previous_sensor)
        user = ConfirmedUser.objects.get(openId=openId, ammeter__source_id=sourceId,
                                         ammeter__ammeter_app_code=previous_code,
                                         ammeter__ammeter_sensorId=previous_sensor)
        if user is not None:
            if amt_nw == amt_bf:
                return HttpResponse(json.dumps({"state": True, "msg": "ok"}),
                                    content_type="json/html; charset=UTF-8")
            # urls = chooseUrls(int(sourceId))
            urls = ChooseUrl(int(sourceId),"SOURCE_URL")
            print(urls)
            data = requests.get(urls, params={'name': user.name, 'code': user.code,
                                              'ammeter_app_code': amt_nw.ammeter_app_code,
                                              'ammeter_sensorId': amt_nw.ammeter_sensorId})
            data = json.loads(data.content.decode('utf-8'))
            print(data)
            if data.get('status'):
                user.ammeter.add(amt_nw)
                user.ammeter.remove(amt_bf)
                user.save()
                return HttpResponse(json.dumps({"state": True, "msg": "ok"}),
                                    content_type="json/html; charset=UTF-8")
            else:
                return HttpResponse(json.dumps({"state": False, "msg": "ok"}),
                                    content_type="json/html; charset=UTF-8")
        else:
            return HttpResponse(json.dumps({"state": False, "msg": "ok"}),
                                content_type="json/html; charset=UTF-8")


@admin_required
def repair_info(request):
    """用户设备报修信息"""
    if request.method == 'GET':
        # TODO 1、获取所有管辖设备id
        ammeter_id = getAdminAmmeter(request)
        print(ammeter_id)
        print('获取管辖设备id成功')
        # TODO 2、列出对应的设备号和环号
        ammeters = Ammeters.objects.filter(id__in=ammeter_id).all()
        ammeter_infos = []
        for amt in ammeters:
            ammeter_info = {}
            ammeter_info['app_code'] = amt.ammeter_app_code
            ammeter_info['sensorId'] = amt.ammeter_sensorId
            ammeter_infos.append(ammeter_info)
        print(ammeter_infos)
        print('获取对应设备号环号成功')
        # 获取所有设备报修信息
        repairinfo = requests.post(SUPER_REPAIR_URL, data=json.dumps({"ammeterinfo": ammeter_infos}))
        repairinfo = json.loads(repairinfo.content.decode('utf-8'))
        print(repairinfo)
        return render_to_response("repairinfo.html", {"repairinfos": repairinfo})
    elif request.method == 'POST':
        # 获取需要处理的报修id
        repairId = request.POST.get('repairId')
        print(repairId)
        states = requests.get(SUPER_REPAIR_URL, params={'repairId': repairId})
        if states is not None:
            states = json.loads(states.content.decode('utf-8'))
            print(states)
            return HttpResponse(json.dumps({"state": states, "msg": "ok"}), content_type="json/html; charset=UTF-8")
        else:
            return HttpResponse(json.dumps({"state": False, "msg": "ok"}), content_type="json/html; charset=UTF-8")


def assign_permission(request):
    # 为管理员分配权限
    print('进入assign')
    if request.method == 'GET':
        result = []
        projects = Project.objects.all()
        for project in projects:
            msg = {
                'project': project.projectname + '(source_id:' + str(project.source_id) + ')',
                'domains': str(
                    Ammeters.objects.filter(source_id=project.source_id).values('domain').distinct()).replace('{', '')
                    .replace('\'domain\': ', '').replace('}', '')
            }
            result.append(msg)
        superUsers = SuperUser.objects.all()
        return render_to_response('assignPermission.html', {'superUsers': superUsers,
                                                            'map': result})

def warn_detail(request):
    if request.method == 'GET':
        source_id = request.GET.get('source_id')
        distination = request.GET.get('distination')
        app_code_id = request.GET.get('ammeterid')
        warn_content = request.GET.get('warn_content')
        warn_level = request.GET.get('warn_level')
        openId = request.GET.get('hash')
        coord = request.GET.get('coord')
        location = request.GET.get('location')
        rule = re.compile(r'\[(.*?)]',re.S)
        app = re.findall(rule,str(warn_content))
        data = {
            'source_id': source_id,
            'app_code_id': app_code_id,
            'distination': distination,
            'warn_content': warn_content,
            'warn_level': warn_level,
            'coord': coord,
            'location': location,
            'hash': openId,
            'insert_app': app if app else '无'
        }
        return render_to_response('warnDetail.html', data)

    elif request.method == 'POST':
        source_id = request.POST.get('source_id')
        app_code_id = request.POST.get('ammeterid')
        distination = request.POST.get('distination')
        openId = request.POST.get('hash')
        # print('in view:',source_id,distination,app_code_id,openId)
        url = URLSource.objects.get(id=source_id).url
        ammeter = get_or_none(ConfirmedUser,openId=openId, ammeter__source=source_id, ammeter__domain=distination,
                                             ammeter__ammeter_app_code=app_code_id)
        # 匹配有权限的管理员
        superusers = SuperUser.objects.filter(Q(openId=openId)&
                                              (Q(source_id='all')|Q(source_id__iregex=('^' + str(
                                                          source_id) + ',') + '|' + (',' + str(
                                                          source_id) + ',')
                                                                           + '|' + (',' + str(source_id) + '$')))&
                                              (Q(domain='all')|Q(domain__iregex=('^' + str(
                                                          distination) + ',') + '|' + (',' + str(
                                                          distination) + ',')
                                                                           + '|' + (',' + str(distination) + '$'))))

        # 检查该用户是否有权限
        if ammeter is not None or len(superusers)>0:
            timestamp = int(time.time())
            # 生成签名，暂未加入user和password校验
            signed = generateMD5(timestamp, source_id)
            data = requests.post(url, data={"type": 'ALL', 'ammeter_app_code':app_code_id,'distination': distination,
                                            'source': 'wx_push', 'timestamp': timestamp,
                                            'sign': signed
                                            })
            # print(data.content,data.status_code)
            # print('distin:',distination,'  code:',app_code_id)
            if data.status_code == 200:
                return HttpResponse(data.content,
                    content_type="json/html; charset=UTF-8")
        else:
            return HttpResponse(json.dumps({
                "code": 1001,
                "msg": 'no privilege'
            }), content_type="json/html; charset=UTF-8")


def simulateWarning(request):
    if request.method == 'GET':
        return render_to_response("simuWarn.html")

    elif request.method == 'POST':
        # 生成模拟警报数据
        power = request.POST.get('power')
        arc = request.POST.get('arc')
        remain_cur = request.POST.get('remain_cur')
        line_temp = request.POST.get('line_temp')
        kettle = request.POST.get('kettle')
        dpc = request.POST.get('dpc')
        warn_content = simuWarn(power,arc,remain_cur,line_temp,kettle,dpc)
        access_token = getconfig(ACCESS_TOKEN, "")
        superUsers = SuperUser.objects.all()
        if warn_content:
            for su in superUsers:
                WxMessageUtil.send_message_by_openid(access_token=access_token, openId=su.openId,
                                                     templateId=TEMPLATE_ID,
                                                     miniPorgramParams=None,
                                                     template_data=TemplateContent(TemplateIdParams(warn_content[0]),
                                                                                   TemplateIdParams(warn_content[1]),
                                                                                   TemplateIdParams(warn_content[2]),
                                                                                   TemplateIdParams(warn_content[3]),
                                                                                   TemplateIdParams(warn_content[4]),
                                                                                   TemplateIdParams(warn_content[5]),
                                                                                   TemplateIdParams(warn_content[6])),
                                                     device='source:'+'0'+'app_code_id:'+'-1')
        return HttpResponseRedirect(reverse('warn-simulate'))

def getWarnMessage(request):
    return "ok"

def getHandleHistory(request):
    return "ok"

def chooseUrls(source_id):
    if source_id == 1:
        return HDU_SOURCE_URL