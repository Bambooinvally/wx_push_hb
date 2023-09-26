class TemplateIdParams03:

    def __init__(self, value, color="#173177"):
        self.value = value
        self.color = color


class TemplateContent03:

    def __init__(self, first, remark, *keywordArgs):
        self.first = first.__dict__
        self.remark = remark.__dict__
        """
        报修对象
        {{keyword1.DATA}}

        报修时间
        {{keyword2.DATA}}

        报修内容
        {{keyword3.DATA}}

        """
        self.keyword1 = keywordArgs[0].__dict__
        self.keyword2 = keywordArgs[1].__dict__
        self.keyword3 = keywordArgs[2].__dict__

    def getKeywords03(self):
        return [self.keyword1, self.keyword2, self.keyword3]


if __name__ == '__main__':
    first = TemplateIdParams03("报修处理通知")
    remark = TemplateIdParams03('remark')
    keywordArgs = [
        TemplateIdParams03('1'),
        TemplateIdParams03('2'),
        TemplateIdParams03('3'),
    ]
    tp = TemplateContent03(first, remark, *keywordArgs)
    print(tp.getKeywords03())
