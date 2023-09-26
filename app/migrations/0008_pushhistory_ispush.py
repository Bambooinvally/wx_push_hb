# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0007_auto_20210908_1454'),
    ]

    operations = [
        migrations.AddField(
            model_name='pushhistory',
            name='isPush',
            field=models.BooleanField(default=True),
        ),
    ]
