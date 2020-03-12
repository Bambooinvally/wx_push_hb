'''
url 地址
'''

# 获取access_token的地址
from urllib import parse

from wx_push import specsetting
from wx_push.specsetting import RESGER_URL, MODIFY_INFO_URL, SUPERUSER_MODIFY_INFO_URL

ACCESS_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
SEND_TEMPLATE_MESSAGE_URL = "https://api.weixin.qq.com/cgi-bin/message/templates/send"

'''
公众号的参数
'''
APPID = "wx179a6296f724d40f"
SECTET = "c6274cc6daf329797170046b712a180d"

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

