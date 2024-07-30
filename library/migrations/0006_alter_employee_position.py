# Generated by Django 5.0 on 2024-07-30 12:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("library", "0005_alter_employee_position"),
    ]

    operations = [
        migrations.AlterField(
            model_name="employee",
            name="position",
            field=models.CharField(
                choices=[("ທົ່ວໄປ", "ທົ່ວໄປ"), ("ຜູ້ອໍານວຍການ", "ຜູ້ອໍານວຍການ")],
                default="ທົ່ວໄປ",
                max_length=100,
            ),
        ),
    ]