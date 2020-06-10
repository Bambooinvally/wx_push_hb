import datetime
import json
import random
from functools import wraps

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404

from app.configutils import getconfig, Ammeters, ConfirmedUser, Project
from service.wxutils import WxUserTagUtil
# Create your views here.
from django.contrib.auth import logout, authenticate

from app.models import UnconfirmUser, WxUser, get_or_none, SuperUser
from superuser.permissionUtils import getAdminPermission, admin_required, adminCheck
from wx_push.specsetting import ADMIN_TAG



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
                return HttpResponseRedirect(reverse('manage-login'))
            else:
                return HttpResponseRedirect('没有权限')
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
        openId = request.POST.get('openid','')
        if adminCheck(openId):
            result = {'status':'success'}
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
        user = get_object_or_404(WxUser, pk=pk)
        return render_to_response("userInfo.html", {"user": user, "request": request})

@admin_required
def search_user(request):
    if request.method == "POST":
        qdata = request.POST.get("qdata", "")
        qtype = request.POST.get("qtype", "")
        users = []
        if qtype == "name":
            users = ConfirmedUser.objects.filter(name__startswith=qdata)
        elif qtype == "phone":
            users = ConfirmedUser.objects.filter(phone__startswith=qdata)
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
            uusers.delete()
            print('delte user')
            return HttpResponse(json.dumps(
                {"data": serializers.serialize('json', UnconfirmUser.objects.all()), "state": True, "msg": "ok"}),
                content_type="json/html; charset=UTF-8")
        print(openId,len(openId),verify,uusers)
        if len(uusers) == 1:
            source_permit, domain_permit = getAdminPermission(request)
            # source_permit, domain_permit = [1, 2, 3, 4], [1, 2, 3, 4]
            uuser = uusers.first()
            # print(uuser.ammeter.values())
            wxuser = get_or_none(ConfirmedUser, openId=uuser.openId)
            # print(wxuser)
            if wxuser is None:
                try:
                    wxuser = ConfirmedUser.objects.create(openId=uuser.openId,name=uuser.name,phone=uuser.phone,
                                                 address=uuser.address,IDcard=uuser.IDcard,extraInfo=uuser.extraInfo)
                    for amt in uuser.ammeter.all():
                        wxuser.ammeter.add(amt)
                    uuser.delete()
                except Exception as e:
                    print(e)
            else:
                wxuser.phone = uuser.phone
                wxuser.name = uuser.name
                wxuser.IDcard = uuser.IDcard
                wxuser.address = uuser.address
                wxuser.ammeter.clear()
                for amt in uuser.ammeter.all():
                    wxuser.ammeter.add(amt)
                wxuser.save()
                uuser.delete()
            return HttpResponse(json.dumps(
                {"data": serializers.serialize('json', UnconfirmUser.objects.filter(ammeter__source__in=source_permit,ammeter__domain__in=domain_permit)), "state": True, "msg": "ok"}),
                content_type="json/html; charset=UTF-8")
        else:
            print('here')
            return HttpResponse(json.dumps({"msg": "无此用户", "state": False}),
                                content_type="json/html; charset=UTF-8")

    #  获取页面
    else:
        source_permit, domain_permit = getAdminPermission(request)
        # source_permit, domain_permit = [1, 2, 3, 4], [1, 2, 3, 4]
        uncofirmUsers = UnconfirmUser.objects.filter(ammeter__source__in=source_permit,ammeter__domain__in=domain_permit)
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
        previous_code = request.POST.get('previous_code')
        print(openId,sourceId,code,previous_code)
        # 生效修改
        try:
            user = ConfirmedUser.objects.get(openId=openId)
            user.ammeter.filter(source_id=sourceId,ammeter_app_code=previous_code).delete()
            amt = Ammeters.objects.get(source_id=sourceId,ammeter_app_code=code)
            user.ammeter.add(amt)
        except Exception as e:
            print('error')
        return HttpResponse(json.dumps(
            { "state": True, "msg": "ok"}),
            content_type="json/html; charset=UTF-8")
            
def warn_detail(request):
    source_id = request.GET.get('source_id')
    app_code_id = request.GET.get('ammeterid')
    return render_to_response('warnDetail.html')