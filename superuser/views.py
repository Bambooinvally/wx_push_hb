import datetime
import json
import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core import serializers
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response, get_object_or_404

# Create your views here.
from django.contrib.auth import logout, authenticate

from app.models import UnconfirmUser, WxUser, get_or_none


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
            return HttpResponseRedirect(reverse('my_login') + '?err=true&msg=密码不正确!')
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse('my_login') + '?err=true&msg=账号不存在!')
        else:
            request.session['username'] = username
            login(request, user)
            if user.is_superuser:
                return HttpResponseRedirect(reverse('verify-user'))
            else:
                return HttpResponseRedirect(reverse('my_login'))
    else:
        return HttpResponse("gundan")


@login_required()
def my_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


"""
2. 管理员功能：
    2.1 管理员修改用户信息
    2.2 管理员审核的注册信息（同意就开通用户推送）
"""


def modefy_user_info(request):
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


def search_user(request):
    if request.method == "POST":
        qdata = request.POST.get("qdata", "")
        qtype = request.POST.get("qtype", "")
        users = []
        if qtype == "name":
            users = WxUser.objects.filter(name__startswith=qdata)
        elif qtype == "phone":
            users = WxUser.objects.filter(phone__startswith=qdata)
        if len(users) > 0:
            return render_to_response("searchUser.html", {"users": users, "request": request})
    return render_to_response("searchUser.html", {"request": request})


def verify_user_info(request):
    """
    未加入权限
    :param request:
    :return:
    """
    if request.method == "POST":
        openId = request.POST.get("openId", "")
        verify = bool(request.POST.get("verify", "False"))
        uusers = UnconfirmUser.objects.filter(openId=openId)
        if verify is False:
            uusers.delete()
            return HttpResponse(json.dumps(
                {"data": serializers.serialize('json', UnconfirmUser.objects.all()), "state": True, "msg": "ok"}),
                content_type="json/html; charset=UTF-8")
        if len(uusers) == 1:
            uuser = uusers.first()
            wxuser = get_or_none(WxUser, {"openId": uuser.openId})
            if wxuser is None:
                defult = {"phone": uuser.phone,
                          "name": uuser.name, "subscribe_time": -1, "subscribe": False}
                WxUser.objects.create(openId=openId, defult=defult)
            else:
                wxuser.phone = uuser.phone
                wxuser.name = uuser.name
                wxuser.IDcard = uuser.IDcard
                wxuser.save()
            return HttpResponse(json.dumps(
                {"data": serializers.serialize('json', UnconfirmUser.objects.all()), "state": True, "msg": "ok"}),
                content_type="json/html; charset=UTF-8")
        else:
            return HttpResponse(json.dumps({"msg": "无此用户", "state": False}),
                                content_type="json/html; charset=UTF-8")
    else:
        uncofirmUsers = UnconfirmUser.objects.all()
        return render_to_response("verifyUser.html", {"uncofirmUsers": uncofirmUsers})
