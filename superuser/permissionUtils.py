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


def adminCheck(openid):
    local_check = get_or_none(SuperUser, openId=openid)
    tag_check = WxUserTagUtil.getUserTag(getconfig("access_token", ""), openid)
    # if local_check is None and ADMIN_TAG in tag_check:
    #     SuperUser.objects.create(openId=openid)
    if local_check is not None and ADMIN_TAG in tag_check:
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