class TemplateIdParams02:

    def __init__(self, value, color="#173177"):
        self.value = value
        self.color = color


class TemplateContent02:

    def __init__(self, first, remark, *keywordArgs):
        self.first = first.__dict__
        self.remark = remark.__dict__
        """
        编号
        {{keyword1.DATA}}

        姓名
        {{keyword2.DATA}}

        类别
        {{keyword3.DATA}}
        
        申请时间
        {{keyword4.DATA}}

        """
        self.keyword1 = keywordArgs[0].__dict__
        self.keyword2 = keywordArgs[1].__dict__
        self.keyword3 = keywordArgs[2].__dict__
        self.keyword4 = keywordArgs[3].__dict__

    def getKeywords02(self):
        return [self.keyword1, self.keyword2, self.keyword3, self.keyword4]


if __name__ == '__main__':
    first = TemplateIdParams02("状态通知")
    remark = TemplateIdParams02('remark')
    keywordArgs = [
        TemplateIdParams02('1'),
        TemplateIdParams02('2'),
        TemplateIdParams02('3'),
        TemplateIdParams02('4'),
    ]
    tp = TemplateContent02(first, remark, *keywordArgs)
    print(tp.getKeywords02())