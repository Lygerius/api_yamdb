# Generated by Django 3.0.5 on 2020-10-04 14:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0030_auto_20201004_1354'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='review',
            unique_together=set(),
        ),
    ]