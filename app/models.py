from django.db import models


# Create your models here.

class Config(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    textValue = models.TextField(null=True)
    value = models.CharField(max_length=255, null=True)
    valueAttached = models.CharField(max_length=255, null=True)
    
    class Meta:
        db_table = 'Config'


class WxUser(models.Model):
    """
    
    """
    openId = models.CharField("微信的openid", max_length=255, primary_key=True)
    nickname = models.CharField("微信名字", max_length=255, null=True, blank=True)
    # 0是女，1是男
    sex = models.NullBooleanField(null=True, blank=True)
    city = models.CharField("所在城市", max_length=100, null=True, blank=True)
    country = models.CharField("所在国家", max_length=100, null=True, blank=True)
    subscribe_time = models.BigIntegerField()  # 订阅或者取消订阅的时间
    subscribe = models.BooleanField()  # 是否订阅，1为订阅
    subscribe_scene = models.CharField(max_length=50, null=True, blank=True)  # 订阅场景
    ammeter_id = models.BigIntegerField(null=True, blank=True)  # ammeter的id号
    
    # 需要重建额外信息
    name = models.CharField("注册时的名字", max_length=100, null=True, blank=True)
    phone = models.CharField("注册时的手机", max_length=100, null=True, blank=True)
    IDcard = models.CharField("注册时的身份证", max_length=255, null=True, blank=True)
    
    class Meta:
        db_table = 'wxUser'


class Menu(models.Model):
    submenu_id = models.BigIntegerField(null=True, blank=True)
    name = models.CharField(null=True, blank=True, max_length=60)
    type = models.CharField(null=True, blank=True, max_length=100)
    key = models.CharField(null=True, blank=True, max_length=128)
    url = models.TextField(null=True, blank=True)
    media_id = models.CharField(null=True, blank=True, max_length=255)
    appid = models.CharField(null=True, blank=True, max_length=100)
    pagepath = models.TextField(null=True, blank=True)
    
    class Meta:
        db_table = 'menu'
    
    """
    1、click：点击推事件用户点击click类型按钮后，微信服务器会通过消息接口推送消息类型为event的结构给开发者（参考消息接口指南），并且带上按钮中开发者填写的key值，开发者可以通过自定义的key值与用户进行交互；
    2、view：跳转URL用户点击view类型按钮后，微信客户端将会打开开发者在按钮中填写的网页URL，可与网页授权获取用户基本信息接口结合，获得用户基本信息。
    3、miniprogram：小程序类型
    4、scancode_push：扫码推事件用户点击按钮后，微信客户端将调起扫一扫工具，完成扫码操作后显示扫描结果（如果是URL，将进入URL），且会将扫码的结果传给开发者，开发者可以下发消息。
    5、scancode_waitmsg：扫码推事件且弹出“消息接收中”提示框用户点击按钮后，微信客户端将调起扫一扫工具，完成扫码操作后，将扫码的结果传给开发者，同时收起扫一扫工具，然后弹出“消息接收中”提示框，随后可能会收到开发者下发的消息。
    6、pic_sysphoto：弹出系统拍照发图用户点击按钮后，微信客户端将调起系统相机，完成拍照操作后，会将拍摄的相片发送给开发者，并推送事件给开发者，同时收起系统相机，随后可能会收到开发者下发的消息。
    7、pic_photo_or_album：弹出拍照或者相册发图用户点击按钮后，微信客户端将弹出选择器供用户选择“拍照”或者“从手机相册选择”。用户选择后即走其他两种流程。
    8、pic_weixin：弹出微信相册发图器用户点击按钮后，微信客户端将调起微信相册，完成选择操作后，将选择的相片发送给开发者的服务器，并推送事件给开发者，同时收起相册，随后可能会收到开发者下发的消息。
    9、location_select：弹出地理位置选择器用户点击按钮后，微信客户端将调起地理位置选择工具，完成选择操作后，将选择的地理位置发送给开发者的服务器，同时收起位置选择工具，随后可能会收到开发者下发的消息。
    10、media_id：下发消息（除文本消息）用户点击media_id类型按钮后，微信服务器会将开发者填写的永久素材id对应的素材下发给用户，永久素材类型可以是图片、音频、视频、图文消息。请注意：永久素材id必须是在“素材管理/新增永久素材”接口上传后获得的合法id。
    11、view_limited：跳转图文消息URL用户点击view_limited类型按钮后，微信客户端将打开开发者在按钮中填写的永久素材id对应的图文消息URL，永久素材类型只支持图文消息。请注意：永久素材id必须是在“素材管理/新增永久素材”接口上传后获得的合法id。
    """
    TYPE_ENUM = ("view", "click", "miniprogram", "scancode_push",
                 "scancode_waitmsg", "pic_sysphoto", "pic_photo_or_album",
                 "pic_weixin", "location_select", "media_id", "view_limited")


class UnconfirmUser(models.Model):
    name = models.CharField(null=True, blank=True, max_length=100)  # 姓名
    phone = models.CharField(null=True, blank=True, max_length=100)  # 手机号
    address = models.CharField(null=True, blank=True, max_length=255)  # 需要推送的地址
    openId = models.CharField("微信的openid", max_length=255, primary_key=True)
    
    # 可以考虑加一下时间
    # createTime = models.BigIntegerField(null=True)
    
    class Meta:
        db_table = 'unconfirmUser'


def get_or_none(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        return None
