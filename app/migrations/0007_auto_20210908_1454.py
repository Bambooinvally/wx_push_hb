# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_auto_20210805_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='confirmeduser',
            name='apppush',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='confirmeduser',
            name='nightpush',
            field=models.BooleanField(default=False),
        ),
    ]
