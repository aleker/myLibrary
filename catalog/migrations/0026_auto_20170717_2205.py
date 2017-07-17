# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-17 20:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0025_bookinstance_comment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='book',
            name='genre',
            field=models.ManyToManyField(blank=True, help_text='Select a genre for this book', to='catalog.Genre'),
        ),
    ]