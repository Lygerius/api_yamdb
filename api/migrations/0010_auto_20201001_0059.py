# Generated by Django 3.0.5 on 2020-09-30 21:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0009_auto_20201001_0057'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='rating',
            new_name='score',
        ),
    ]