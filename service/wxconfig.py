'''
url 地址
'''

# 获取access_token的地址
from urllib import parse

from wx_push import specsetting
from wx_push.specsetting import RESGER_URL, MODIFY_INFO_URL, SUPERUSER_MODIFY_INFO_URL, SUPERUSER_LOGIN_URL, \
    HISTORY_EVENT_URL, FAULT_REPAIR_URL, SUPER_WARN_URL, JUMP_PAGE_URL

ACCESS_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
SEND_TEMPLATE_MESSAGE_URL = "https://api.weixin.qq.com/cgi-bin/message/templates/send"

'''
公众号的参数
'''
# APPID = "wx3a5e509fc7d8f24e"
# SECTET = "c46978154407b950fca19c0154194777"
# TEMPLATE_ID = 'ZG0EfC3ZpNrNtvLU6FM-sFIklOBoKheU6bc5MI0Xzyg'
APPID = "wx179a6296f724d40f"
SECTET = "c6274cc6daf329797170046b712a180d"
TEMPLATE_ID = '0ZP2vzOjx3UpQgIMZYdHsR6SxGuZbGW2Tmtrv3RY5xw'
TEMPLATE_REPAIR_ID = 'u0kuMZyvGn3Cu8KZOpVKWErSGAh7g3ylayQ25ynDS08'
TEMPLATEMAP = {
    "deviceWarn": "0ZP2vzOjx3UpQgIMZYdHsR6SxGuZbGW2Tmtrv3RY5xw",
    "userPushDown": "MsyFYiLvtbMDjT6jqnEJqQpHZL-NPTJHWVOgBmTUKaY"
}

'''
小程序的参数
'''

'''
网页参数
'''
WEBURL = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
         + APPID + "&" + \
         "redirect_uri=%s" \
         "&response_type=code" \
         "&scope=snsapi_base" \
         "&state=123#wechat_redirect"

GET_OPENID_URL = "https://api.weixin.qq.com/sns/oauth2/access_token?appid="\
        + APPID + "&" + \
        "secret=" + SECTET + \
        "&code=%s" + \
        "&grant_type=authorization_code"

# 获取openid
# GET_CODE = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
#            + APPID + "&" \
#            "redirect_uri=" + RESGER_URL + \
#            "&response_type=code" \
#            "&scope=snsapi_base&" \
#            "state=123#wechat_redirect"
GET_CODE = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
           + APPID + "&" \
           "redirect_uri=" + JUMP_PAGE_URL + \
           "&response_type=code" \
           "&scope=snsapi_base&" \
           "state=regedit#wechat_redirect"

# 获取历史扣分信息
# GET_HISTORY = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
#            + APPID + "&" \
#            "redirect_uri=" + HISTORY_EVENT_URL + \
#            "&response_type=code" \
#            "&scope=snsapi_base&" \
#            "state=123#wechat_redirect"
GET_HISTORY = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
           + APPID + "&" \
           "redirect_uri=" + JUMP_PAGE_URL + \
           "&response_type=code" \
           "&scope=snsapi_base&" \
           "state=get_history#wechat_redirect"

# 障碍报修信息
# FAULT_REPAIR = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
#            + APPID + "&" \
#            "redirect_uri=" + FAULT_REPAIR_URL + \
#            "&response_type=code" \
#            "&scope=snsapi_base&" \
#            "state=123#wechat_redirect"
FAULT_REPAIR = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
           + APPID + "&" \
           "redirect_uri=" + JUMP_PAGE_URL + \
           "&response_type=code" \
           "&scope=snsapi_base&" \
           "state=repair#wechat_redirect"


# 修改个人信息
MODIFY_INFO = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
           + APPID + "&" \
           "redirect_uri=" + MODIFY_INFO_URL + \
           "&response_type=code" \
           "&scope=snsapi_base&" \
           "state=123#wechat_redirect"

SUPERUSER_LOGIN = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
           + APPID + "&" \
           "redirect_uri=" + SUPERUSER_LOGIN_URL + \
           "&response_type=code" \
           "&scope=snsapi_base&" \
           "state=123#wechat_redirect"
           
# SIMULATE = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
#            + APPID + "&" \
#            "redirect_uri=http://wxpushky.piercingeyes.cn/super/warn/simulate"  + \
#            "&response_type=code" \
#            "&scope=snsapi_base&" \
#            "state=123#wechat_redirect"
SIMULATE = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
           + APPID + "&" \
           "redirect_uri=" + SUPER_WARN_URL + \
           "&response_type=code" \
           "&scope=snsapi_base&" \
           "state=123#wechat_redirect"


'''后台数据请求接口'''
# WARNMESSAGEPUSH = "http://36.134.182.28:15019/api/dangerouselec.json"
WARNMESSAGEPUSH = "http://127.0.0.1:8000/api/dangerouselec.json"
# WARNMESSAGEPUSH = "http://36.134.182.28:15019/api/dangerouselec.json"