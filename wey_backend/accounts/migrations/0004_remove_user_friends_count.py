# Generated by Django 4.2.6 on 2023-10-22 13:20

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0003_user_friends_count_alter_friendshiprequest_status"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="user",
            name="friends_count",
        ),
    ]
