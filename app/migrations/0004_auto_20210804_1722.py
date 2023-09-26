# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20210804_1701'),
    ]

    operations = [
        migrations.RenameField(
            model_name='confirmeduser',
            old_name='phone',
            new_name='code',
        ),
    ]
