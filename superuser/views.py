import random

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth.views import login
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, render_to_response

# Create your views here.
from django.contrib.auth import logout, authenticate

from app.models import UnconfirmUser, WxUser


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
        print(pagedatas['board'])
        return render_to_response('login.html', pagedatas)
    elif request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        vrf = request.POST.get('vrf', '')
        print(vrf)
        if str(request.session['vrf']) != vrf:
            return HttpResponse("gundanba")
        try:
            user = authenticate(username=username, password=password)
        except PasswordError:
            return HttpResponseRedirect(reverse('login') + '?err=true&msg=密码不正确!')
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse('login') + '?err=true&msg=账号不存在!')
        else:
            request.session['username'] = username
            # logger.debug("set session of username")
            login(request, user)
            if user.is_superuser:
                return HttpResponseRedirect(reverse('dashboard:terminals'))
            else:
                return HttpResponseRedirect(reverse('runner:index'))
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
    if request.method == "POST":
        pass


def search_user(request):
    if request.method == "POST":
        qdata = request.POST.get("qdata", "")
        qtype = request.POST.get("qtype", "")
        users = []
        if qtype=="name":
            users = WxUser.objects.filter(name__startswith=qdata)
        elif qtype=="phone":
            users = WxUser.objects.filter(phone__startswith=qdata)
        if len(users)>0:
            return render_to_response("searchUser.html", {"users": users})
    return render_to_response("searchUser.html")


def verify_user_info(request):
    if request.method == "POST":
        pass
    else:
        uncofirmUsers = UnconfirmUser.objects.all().values_list("name", "phone", "address", "openId")
        render_to_response("", {"uncofirmUsers": uncofirmUsers})
