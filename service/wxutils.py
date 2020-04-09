import datetime
import json
import time

import requests

from app.models import ConfirmedUser, Ammeters, get_or_none
from service.Template import TemplateIdParams, TemplateContent
from service.wxconfig import TEMPLATEMAP, APPID, SECTET


#  'appid': 'wx179a6296f724d40f'

def get_access_token():
    """
    获取token
    :return:
    """
    re = requests.get('https://api.weixin.qq.com/cgi-bin/token',
                      params={'appid': APPID,
                              'secret': SECTET,
                              'grant_type': 'client_credential'})
    msg = json.loads(re.content.decode('utf-8'))
    access_token = msg.get("access_token", "")
    expires_in = msg.get("expires_in", 7200)
    return (access_token, expires_in)


class News:

    def __init__(self, title, desc, picurl, url):
        self.title = title
        self.desc = desc
        self.picurl = picurl
        self.url = url


class WxMenuUtil:
    @staticmethod
    def create_menu(access_token, menu):
        """
        创建菜单
        :param access_token:
        :param menu
        :return:
        """
        # menu = {
        #     "button": [
        #         {
        #             "type": "click",
        #             "name": "今日1歌曲",
        #             "key": "V1001_TODAY_MUSIC"
        #         },
        #         {
        #             "name": "菜单",
        #             "sub_button": [
        #                 {
        #                     "type": "view",
        #                     "name": "搜索",
        #                     "url": "http://www.soso.com/"
        #                 },
        #                 {
        #                     "type": "click",
        #                     "name": "赞一下我们",
        #                     "key": "V1001_GOOD"
        #                 }]
        #         }
        #     ]
        # }
        re = requests.post("https://api.weixin.qq.com/cgi-bin/menu/create",
                           params={"access_token": access_token},
                           data=json.dumps(menu, ensure_ascii=False).encode('utf-8'))
        return re.content

    @staticmethod
    def create_addconditionalMenu(access_token, menu):
        """
        创建菜单
        :param access_token:
        :param menu
        :return:
        """
        re = requests.post("https://api.weixin.qq.com/cgi-bin/menu/addconditional",
                           params={"access_token": access_token},
                           data=json.dumps(menu, ensure_ascii=False).encode('utf-8'))
        return re.content

    @staticmethod
    def del_menu(access_token):
        """
        删除菜单
        :param access_token:
        :return:
        """
        re = requests.get("https://api.weixin.qq.com/cgi-bin/menu/delete",
                          params={"access_token": access_token})
        return re.content


class WxMessageUtil:

    @staticmethod
    def send_message_by_openid(access_token, openId, templateId, miniPorgramParams, template_data, device):
        """
        定向推送消息
        :param access_token:
        :param openId:
        :param templateId:
        :param miniPorgramParams:
        :param template_data:
        :return:
        """
        if miniPorgramParams is None:
            miniPorgramParams = ""
        else:
            miniPorgramParams = miniPorgramParams.__dict__
        # print('device:', str(device).split('app_code_id:'))
        device_data = str(device).split('app_code_id:')
        ammeter = get_or_none(Ammeters,source_id=device_data[0].split(':')[1], ammeter_app_code=device_data[1])
        if ammeter is None:
            ammeter.coordinate = ''
            ammeter.ammeter_addr = ''
        re = requests.post("https://api.weixin.qq.com/cgi-bin/message/template/send",
                           params={"access_token": access_token},
                           data=json.dumps({
                               "touser": openId,
                               "template_id": templateId,
                               "url": "https://apis.map.qq.com/uri/v1/marker?"
                                      "marker=coord:" + str(ammeter.coordinate) + ";"
                                      "title:"+ str(ammeter.ammeter_addr) +";"
                                      "addr:报警地点" 
                                      "&referer=myapp",
                               # "topcolor": "#FF0000",
                               # "miniprogram": miniPorgramParams,
                               "data": template_data.__dict__
                           }))
        print(re.content)
        return re.content

    @staticmethod
    def __reply_message(toUser, fromUser, msgType, extr=""):
        """
        :param toUser:
        :param fromUser:
        :param msgType: 消息类型
        :param extr: 额外的xml内容
        :return:
        """
        message = """<xml>
                        <ToUserName><![CDATA[{0}]]></ToUserName>
                        <FromUserName><![CDATA[{1}]]></FromUserName>
                        <CreateTime>{2}</CreateTime>
                        <MsgType><![CDATA[{3}]]></MsgType>
                        {4}
                    </xml>"""
        return message.format(toUser, fromUser, str(int(time.time())), msgType, extr)

    @staticmethod
    def reply_text_message(toUser, fromUser, content):
        """
        回复文本消息
        :param toUser:
        :param fromUser:
        :param content: 回复的文本信息
        :return:
        """
        text = "<Content><![CDATA[{}]]></Content>".format(content)
        return WxMessageUtil.__reply_message(toUser, fromUser, 'text', text)

    @staticmethod
    def reply_img_message(toUser, fromUser, media_id):
        """
        回复图片消息
        :param toUser:
        :param fromUser:
        :param media_id: 通过素材管理中的接口上传多媒体文件，得到的id
        :return:
        """
        img = """
        <Image>
           <MediaId><![CDATA[{}]]></MediaId>
        </Image>
        """.format(media_id)
        return WxMessageUtil.__reply_message(toUser, fromUser, 'image', img)

    @staticmethod
    def reply_voice_message(toUser, fromUser, media_id):
        """
        回复语音消息
        :param toUser:
        :param fromUser:
        :param media_id: 通过素材管理中的接口上传多媒体文件，得到的id
        :return:
        """
        voice = """
            <Voice>
                <MediaId><![CDATA[{}]]></MediaId>
            </Voice>
            """.format(media_id)
        return WxMessageUtil.__reply_message(toUser, fromUser, 'voice', voice)

    @staticmethod
    def reply_video_message(toUser, fromUser, title, desc, media_id):
        """
        回复视频消息
        :param toUser:
        :param fromUser:
        :param title:视频消息的标题
        :param desc:视频消息的描述
        :param media_id:通过素材管理中的接口上传多媒体文件，得到的id
        :return:
        """
        video = """
                <Video>
                    <MediaId><![CDATA[{}]]></MediaId>
                    <Title><![CDATA[{}]]></Title>
                    <Description><![CDATA[{}]]></Description>
                </Video>
                """.format(media_id, title, desc)
        return WxMessageUtil.__reply_message(toUser, fromUser, 'video', video)

    @staticmethod
    def reply_music_message(toUser, fromUser, title, desc, musicUrl, hqMusicUrl, media_id):
        """
        回复音乐消息
        :param toUser:
        :param fromUser:
        :param title:音乐标题
        :param desc:音乐描述
        :param musicUrl:音乐链接
        :param hqMusicUrl:高质量音乐链接，WIFI环境优先使用该链接播放音乐
        :param media_id:缩略图的媒体id，通过素材管理中的接口上传多媒体文件，得到的id
        :return:
        """
        music = """
                    <Music>
                        <Title><![CDATA[{}]]></Title>
                        <Description><![CDATA[{}]]></Description>
                        <MusicUrl><![CDATA[{}]]></MusicUrl>
                        <HQMusicUrl><![CDATA[{}]]></HQMusicUrl>
                        <ThumbMediaId><![CDATA[{}]]></ThumbMediaId>
                    </Music>
                    """.format(title, desc, musicUrl, hqMusicUrl, media_id)
        return WxMessageUtil.__reply_message(toUser, fromUser, 'music', music)

    @staticmethod
    def reply_text_img_message(toUser, fromUser, ArticleCount, *newsLst):
        """
        回复图文消息
        :param toUser:
        :param fromUser:
        :param ArticleCount: 图文消息个数；当用户发送文本、图片、视频、图文、地理位置这五种消息时，开发者只能回复1条图文消息；其余场景最多可回复8条图文消息
        :param newsLst: news的实例列表
        :return:
        """
        item = """
                <item>
                    <Title><![CDATA[{}]]></Title>
                    <Description><![CDATA[{}]]></Description>
                    <PicUrl><![CDATA[{}]]></PicUrl>
                    <Url><![CDATA[{}]]></Url>
                </item>
                """
        articles = []
        if newsLst:
            for news in newsLst:
                articles.append(item.format(news.title, news.desc, news.picurl, news.url))
        articlesStr = "".join(articles)
        n = """
                <ArticleCount>{}</ArticleCount>
                <Articles>
                    {}
                </Articles>
                        """.format(ArticleCount, articlesStr)
        return WxMessageUtil.__reply_message(toUser, fromUser, 'news', n)


class WxUserTagUtil:
    @staticmethod
    def createTag(access_token, name):
        """
        创建用户标签
        :param access_token:
        :param name:标签名
        :return:
        """
        re = requests.post(url='https://api.weixin.qq.com/cgi-bin/tags/create',
                           params={'access_token': access_token},
                           data=json.dumps({'tag': {'name': name}}))
        return re.content

    @staticmethod
    def getTag(access_token):
        """
        获得用户标签
        :param access_token:
        :return:
        """
        # tags = []
        re = requests.get(url='https://api.weixin.qq.com/cgi-bin/tags/get',
                          params={'access_token': access_token})
        tags = json.loads(re.content.decode('utf-8'))
        return tags['tags']

    @staticmethod
    def deleteTag(access_token, tagId):
        """
        删除用户标签
        :param access_token:
        :param name:标签名
        :return:
        """
        re = requests.post(url='https://api.weixin.qq.com/cgi-bin/tags/delete',
                           params={'access_token': access_token},
                           data=json.dumps({'tag': {'id': tagId}}))
        return re.content

    @staticmethod
    def editTag(access_token, tagId, newName):
        """
        编辑用户标签
        :param tagId:
        :param newName:
        :return:
        """
        re = requests.post(url='https://api.weixin.qq.com/cgi-bin/tags/update',
                           params={'access_token': access_token},
                           data=json.dumps({'tag': {'id': tagId,'name': newName}}))
        return re.content

    @staticmethod
    def getUserByTag(access_token,tagId,next_openid=''):
        """
        获得标签下的用户
        :param access_token:
        :param tagId:
        :param next_openid: 从哪个openid开始
        :return:标签下人数，成员
        """
        # tags = []
        re = requests.post(url='https://api.weixin.qq.com/cgi-bin/user/tag/get',
                          params={'access_token': access_token},
                          data=json.dumps({'tagid': tagId,'next_openid': next_openid}))
        result = json.loads(re.content, encoding='utf-8')
        count = result['count']
        members = result['data']['openid']
        return count, members

    @staticmethod
    def setUserTag(access_token, openid_list, tagId):
       """
       批量为用户打标签
       :param access_token: 
       :param tagId: 
       :param nopenid_list:
       :return: 
       """
       re = requests.post(url='https://api.weixin.qq.com/cgi-bin/tags/members/batchtagging',
                          params={'access_token': access_token},
                          data=json.dumps({'openid_list': openid_list,
                                           'tagid':tagId}))
       return re.content

    @staticmethod
    def cancelUserTag(access_token, openid_list, tagId):
        """
        批量为用户取消标签
        :param access_token:
        :param tagId:
        :param nopenid_list:
        :return:
        """
        re = requests.post(url='https://api.weixin.qq.com/cgi-bin/tags/members/batchuntagging',
                           params={'access_token': access_token},
                           data=json.dumps({'openid_list': openid_list,
                                            'tagid': tagId}))
        return re.content

    @staticmethod
    def getUserTag(access_token, openid):
        """
        获取某用户标签
        :param access_token:
        :param tagId:
        :param nopenid_list:
        :return:用户标签，可能不止一个
        """
        re = requests.post(url='https://api.weixin.qq.com/cgi-bin/tags/getidlist',
                           params={'access_token': access_token},
                           data=json.dumps({'openid': openid}))
        try:
            tag = json.loads(re.content.decode('utf-8'))["tagid_list"]
        except Exception as e:
            tag = ''
            print('get tag error\n',re.content,e)
        return tag


if __name__ == "__main__":
    access_token = '31_OwTELlcEygEuy1eO2cS2OEOTtIFmTq8HfY629dOt-fiHKOrEIlHNyPQQoUbO_5CcVoTz4Dg-hNtyVkbt2hPDq_V8-zaIHTvQAMt5zZfSJ_QKjknuveyurExwgmqyTygGUSboYuWAluXHSY1vTASeABAPWO'
    # print(WxMenuUtil)
    print(WxUserTagUtil.getTag(access_token))
