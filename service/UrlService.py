#!/usr/bin/python3

"""
处理数据库中的url
"""
from app.models import URLSource

def reconstruct_to_map(urlsObj):
    """
    url为多个model
    :param url:
    :return:
    """
    url_map = {}
    for i in urlsObj:
        url_map[i.pk] = i.url
    return url_map

def get_urls():
    """
    重新构建url_map返回
    :return:
    """
    urls = URLSource.objects.filter(vaild=True)
    return reconstruct_to_map(urls)
    