# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-17 16:48
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0022_auto_20170716_2304'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover',
            field=models.ImageField(blank=True, default='images/None/no-img.jpg', null=True, upload_to='images/'),
        ),
    ]