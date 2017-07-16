# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-16 11:37
from __future__ import unicode_literals

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0014_auto_20170716_1332'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookinstance',
            name='id',
            field=models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular book across whole library', primary_key=True, serialize=False),
        ),
    ]
