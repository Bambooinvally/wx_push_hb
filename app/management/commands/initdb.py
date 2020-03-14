from django.contrib.auth.models import User
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

import logging

from app.models import WxUser

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        # 创建root和admin
        User.objects.get_or_create(username='root',
                                   defaults={'is_superuser': 1, 'is_active': 1, 'password': 'wxpushroot'})
        User.objects.get_or_create(username='admin',
                                   defaults={'is_superuser': 1, 'is_active': 1, 'password': 'wxpushadmin'})
        # 添加自己的微信openid
        WxUser.objects.get_or_create(openId="o-XSVwQPdEYOUWcq6QD9F0V9K9DU", sex=True, subscribe_time=1, subscribe=1)
