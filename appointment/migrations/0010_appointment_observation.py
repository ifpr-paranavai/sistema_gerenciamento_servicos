# Generated by Django 4.2.5 on 2024-10-29 03:53

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("appointment", "0009_alter_appointment_documents"),
    ]

    operations = [
        migrations.AddField(
            model_name="appointment",
            name="observation",
            field=models.TextField(blank=True, null=True),
        ),
    ]
