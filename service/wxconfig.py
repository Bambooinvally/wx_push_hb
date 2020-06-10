'''
url 地址
'''

# 获取access_token的地址
from urllib import parse

from wx_push import specsetting
from wx_push.specsetting import RESGER_URL, MODIFY_INFO_URL, SUPERUSER_MODIFY_INFO_URL, SUPERUSER_LOGIN_URL

ACCESS_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
SEND_TEMPLATE_MESSAGE_URL = "https://api.weixin.qq.com/cgi-bin/message/templates/send"

'''
公众号的参数
'''
APPID = "wx123ef55e533e969e"
SECTET = "8358893fc0fea700af2a36d8de87586b"
TEMPLATE_ID = 'BDO8geYLSiJx-tWmb_W4weJqhDGktJq0XbL1iBt4whQ'
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
GET_CODE = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
           + APPID + "&" \
           "redirect_uri=" + RESGER_URL + \
           "&response_type=code" \
           "&scope=snsapi_base&" \
           "state=123#wechat_redirect"

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
           
SIMULATE = "https://open.weixin.qq.com/connect/oauth2/authorize?appid=" \
           + APPID + "&" \
           "redirect_uri=http://wxpushky.piercingeyes.cn/super/warn/simulate"  + \
           "&response_type=code" \
           "&scope=snsapi_base&" \
           "state=123#wechat_redirect"
