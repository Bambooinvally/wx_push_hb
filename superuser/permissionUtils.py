from functools import wraps

from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect

from app.configutils import getconfig
from app.models import SuperUser, Ammeters, get_or_none
from service.wxutils import WxUserTagUtil
from wx_push.specsetting import ADMIN_TAG


def getAdminPermission(request):
    admin = SuperUser.objects.get(openId=request.session.get('openid'))
    source_permit = admin.source_id
    domain_permit = admin.domain
    # 获取source权限
    if source_permit == 'all':
        source_permit = []
        for id in Ammeters.objects.distinct().values('source_id'):
            source_permit.append(id['source_id'])
    else:
        source_permit = str(source_permit).split(',')
    # 获取对应source下的domain权限
    if domain_permit == 'all':
        domain_permit = []
        for id in Ammeters.objects.filter(source__in=source_permit).distinct().values('domain'):
            domain_permit.append(id['domain'])
    else:
        domain_permit = str(domain_permit).split(',')
    return source_permit,domain_permit


def getAdminAmmeter(request):
    """暂时将楼号作为domain"""
    admin = SuperUser.objects.get(openId=request.session.get('openid'))
    source_permit = admin.source_id
    domain_permit = admin.domain
    # 获取管辖ammeter_id
    ammeter_permit_ = []
    # 获取source权限
    domain_permit_ = []
    # 如果管理员管理所有项目
    if source_permit == 'all':
        # 如果管理员管理项目中的所有区域
        if domain_permit == 'all':
            # 将所有设备号加入数组
            for ammeter in Ammeters.objects.filter().exclude(ammeter_addr="实验室测试").exclude(ammeter_addr="--").all():
                ammeter_permit_.append(ammeter.id)
        else:
            # 将管辖区域号加入数组
            domain_permit_ = str(domain_permit).split(',')
            for ammeter in Ammeters.objects.filter(ammeter_unit__in=domain_permit_).exclude(ammeter_addr="实验室测试").exclude(ammeter_addr="--").all():
                ammeter_permit_.append(ammeter.id)
    # 如果管理员管理指定项目
    else:
        source_permit_ = []
        # 将指定项目号加入数组
        source_permit_ = str(source_permit).split(',')
        # 如果管理员管理项目中的所有区域
        if domain_permit == 'all':
            # 将所有设备号加入数组
            for ammeter in Ammeters.objects.filter(source_id__in=source_permit_).exclude(ammeter_addr="实验室测试").exclude(ammeter_addr="--").all():
                ammeter_permit_.append(ammeter.id)
        else:
            # 将管辖区域号加入数组
            domain_permit_ = str(domain_permit).split(',')
            for ammeter in Ammeters.objects.filter(source_id__in=source_permit_, ammeter_unit__in=domain_permit_).exclude(
                    ammeter_addr="实验室测试").exclude(ammeter_addr="--").all():
                ammeter_permit_.append(ammeter.id)
    return ammeter_permit_


def adminCheck(openid):
    local_check = get_or_none(SuperUser, openId=openid)
    tag_check = WxUserTagUtil.getUserTag(getconfig("access_token", ""), openid)
    # 行政性放开权限
    # if local_check is None and ADMIN_TAG in tag_check:
    #     SuperUser.objects.create(openId=openid, source_id='all', domain='all', name='后台授权用户')
    # if local_check is not None and ADMIN_TAG in tag_check:
    #     return True
    # else:
    #     return False
    if local_check is not None:
        return True
    else:
        return False


def admin_required(func):
    """管理员登录装饰器"""
    @wraps(func)
    def decorate(request, *args, **kwargs):
        openid = request.session.get('openid')
        if openid is not None:
            # 以下两行决定是否采用二次验证
            # is_admin = adminCheck(openid)
            # if is_admin:
                return func(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('wx_login'))
    return decorate