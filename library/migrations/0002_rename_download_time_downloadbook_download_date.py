# Generated by Django 5.0 on 2024-07-13 08:50

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="downloadbook",
            old_name="download_time",
            new_name="download_date",
        ),
    ]