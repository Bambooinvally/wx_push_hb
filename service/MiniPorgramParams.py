# 小程序的appid与路径封装
class MiniPorgramParams:
    
    def __init__(self, appid, pagepath):
        self.appid = appid
        self.pagepath = pagepath
    
    def getAppid(self):
        return self.appid
    
    def getPagepath(self):
        return self.pagepath
