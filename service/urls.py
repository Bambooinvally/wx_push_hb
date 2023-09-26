"""wx_push URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

import os, django

from service import studentService

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mysite.settings")

django.setup()
from django.conf.urls import url
import app.views as aviews
import superuser.views as suview
from django.views import static  ##新增
from django.conf import settings  ##新增
from django.conf.urls import url  ##新增

urlpatterns = [
    # path('admin/', admin.site.urls),
    # wx 使用
    url("^MP_verify_dlUHfQ1hxd6SwBwe.txt$", aviews.verify),
    url("^wxrecv/", aviews.recv_message, name='wx-recv-message'),
    url("^menu/create$", aviews.create_menu, name='wx-menu-create'),
    url("^menu/supercreate$", aviews.create_superMenu, name='wx-supermenu-create'),
    url("^menu/delete$", aviews.del_menu, name='wx-menu-delete'),
    url("^app/params$", aviews.getAppParams, name='wx-app-params'),
    url("^user/register$", aviews.register, name='wx-register'),
    url("^get/ammeters$", aviews.getAmmeters, name='get-ammeter'),


    # 普通学生
    url("^user/historyEvent$", studentService.historyEvent, name='wx-historyEvent'),
    url("^user/faultRepair$", studentService.deviceRepair, name='wx-faultRepair'),
    # 测试路径
    # url("^kylinz/test$",aviews.test, name='test'),

    ##　以下是新增
    url(r'^static/(?P<path>.*)$', static.serve,
        {'document_root': settings.STATIC_ROOT}, name='static'),

    # 管理员

    url("^logout", suview.my_logout, name='my_logout'),
    url("^login", suview.wx_login, name='wx_login'),
    url("^super/modify/user", suview.modify_user_info, name='modify-user'),
    url("^super/verify/user", suview.verify_user_info, name='verify-user'),
    url("^super/search/user", suview.search_user, name='search-user'),
    url("^super/show/user", suview.confirmed_user_info, name='show-user'),
    url("^super/warn/detail", suview.warn_detail, name='warn-detail'),
    url("^super/warn/simulate", suview.simulateWarning, name='warn-simulate'),

]
