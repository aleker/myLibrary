# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-16 21:04
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0021_book_isbn_13'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='book',
            unique_together=set([('title', 'author')]),
        ),
    ]
