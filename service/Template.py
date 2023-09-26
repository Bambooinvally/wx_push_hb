class TemplateIdParams:
    
    def __init__(self, value, color="#173177"):
        self.value = value
        self.color = color


class TemplateContent:
    
    def __init__(self, first, remark, *keywordArgs):
        self.first = first.__dict__
        self.remark = remark.__dict__
        """
        报警内容
        {{keyword1.DATA}}

        报警设备
        {{keyword2.DATA}}

        当前报警值
        {{keyword3.DATA}}

        报警级别
        {{keyword4.DATA}}

        报警时间
        {{keyword5.DATA}}

        """
        self.keyword1 = keywordArgs[0].__dict__
        self.keyword2 = keywordArgs[1].__dict__
        self.keyword3 = keywordArgs[2].__dict__
        self.keyword4 = keywordArgs[3].__dict__
        self.keyword5 = keywordArgs[4].__dict__

    def getKeywords(self):
        return [self.keyword1,self.keyword2,self.keyword3,self.keyword4,self.keyword5]

# if __name__ == '__main__':
#     first = TemplateIdParams("设备报警")
#     remark = TemplateIdParams('remark')
#     keywordArgs = [
#         TemplateIdParams('1'),
#         TemplateIdParams('2'),
#         TemplateIdParams('3'),
#         TemplateIdParams('4'),
#         TemplateIdParams('5')
#     ]
#     tp = TemplateContent(first, remark, *keywordArgs)
#     print(tp.getKeywords())