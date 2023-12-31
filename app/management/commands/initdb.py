from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

import logging

from app.models import WxUser, SuperUser, Config,URLSource

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        # 创建root和admin
        User.objects.get_or_create(username='root',
                                   defaults={'is_superuser': 1, 'is_active': 1, 'password': 'wxpushroot'})
        User.objects.get_or_create(username='admin',
                                   defaults={'is_superuser': 1, 'is_active': 1, 'password': 'wxpushadmin'})
        # 推送间隔
        Config.objects.get_or_create(name='push_delta',defaults={
            'name':'push_delta',
            'value':30
        })
        # 添加自己的微信openid
        # SuperUser.objects.get_or_create(openId="o-XSVwRj5uPsuu4C3ckFLpsxqPsc", name='周天宇',source_id='all',
        #                                 domain='all')
        SuperUser.objects.get_or_create(openId="o-XSVwU3K3EvJrtzIXLjYwkBJee8", name='陆启镐',source_id='all',
                                        domain='all')

        URLSource.objects.get_or_create(url='http://hdu.piercingeyes.cn/api/dangerlist.json',desc='杭电魔眼',
                                        vaild=1)
