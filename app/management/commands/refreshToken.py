import json
import time

import requests
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command
from multiprocessing import Process, Queue
import logging

from app.configutils import getconfig, ACCESS_TOKEN
from app.models import WxUser, get_or_none
from app.wxHandler import handlerSendWarningMessage, handlerAccessToken
from service.wxutils import WxMessageUtil

logger = logging.getLogger(__name__)


def refresh():
    while True:
        expireTime = handlerAccessToken()
        time.sleep(expireTime)

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        prefresh = Process(target=refresh, args=())
        prefresh.start()