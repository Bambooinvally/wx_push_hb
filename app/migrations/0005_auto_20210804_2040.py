# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_auto_20210804_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmeduser',
            name='phone',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='superuser',
            name='phone',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
        migrations.AddField(
            model_name='unconfirmuser',
            name='phone',
            field=models.CharField(max_length=100, blank=True, null=True),
        ),
    ]
