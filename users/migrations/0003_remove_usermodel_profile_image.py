# Generated by Django 5.0 on 2024-07-21 09:28

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_delete_checkemail"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="usermodel",
            name="profile_image",
        ),
    ]