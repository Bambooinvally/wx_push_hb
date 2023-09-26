from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    
    def handle(self, *args, **options):
        try:
            # call_command('syncDatabase')
            call_command('pushService')
            call_command('refreshToken')
        except Exception as e:
            logger.exception(e)
