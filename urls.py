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
from django.conf.urls import url
import app.views as aviews
import superuser.views as suview

urlpatterns = [
    # path('admin/', admin.site.urls),
    # wx 使用
    url("^MP_verify_CoynMqa4m1dQm42K.txt$",aviews.verify),
    url("^wxrecv/", aviews.recv_message, name='wx-recv-message'),
    url("^menu/create$", aviews.create_menu, name='wx-menu-create'),
    url("^menu/delete$", aviews.del_menu, name='wx-menu-delete'),
    url("^app/params$", aviews.getAppParams, name='wx-app-params'),
    url("^user/register$", aviews.register, name='wx-register'),
    
    
    # 管理员
    
    url("^/logout", suview.logout, name='logout'),
    url("^/login", suview.login, name='login'),
    url("^/super/modify/user", suview.modefy_user_info, name='login'),
    url("^/super/verify/user", suview.login, name='login'),
    url("^/super/search/user", suview.login, name='login'),

]