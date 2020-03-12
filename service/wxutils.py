import datetime
import json
import time

import requests

from service.Template import TemplateIdParams, TemplateContent
from service.wxconfig import TEMPLATEMAP


#  'appid': 'wx179a6296f724d40f'


def get_access_token():
    """
    获取token
    :return:
    """
    re = requests.get('https://api.weixin.qq.com/cgi-bin/token',
                      params={'appid': 'wx179a6296f724d40f',
                              'secret': 'c6274cc6daf329797170046b712a180d',
                              'grant_type': 'client_credential'})
    msg = json.loads(re.content.decode())
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
    def send_message_by_openid(access_token, openId, templateId, miniPorgramParams, template_data):
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
        re = requests.post("https://api.weixin.qq.com/cgi-bin/message/templates/send",
                           params={"access_token": access_token},
                           data=json.dumps({
                               "touser": openId,
                               "template_id": templateId,
                               "url": "http://weixin.qq.com/download",
                               "topcolor": "#FF0000",
                               "miniprogram": miniPorgramParams,
                               "data": template_data.__dict__
                           }))
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


if __name__ == "__main__":
    access_token = get_access_token()
    print(access_token)
