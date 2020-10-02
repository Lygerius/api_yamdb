# Generated by Django 3.0.5 on 2020-10-01 17:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0021_auto_20201001_2033"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="role",
            field=models.CharField(
                choices=[
                    ("user", "user"),
                    ("moderator", "moderator"),
                    ("admin", "admin"),
                ],
                default="user",
                max_length=10,
            ),
        ),
    ]
