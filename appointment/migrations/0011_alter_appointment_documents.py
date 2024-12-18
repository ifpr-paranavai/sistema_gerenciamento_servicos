# Generated by Django 4.2.5 on 2024-11-03 00:25

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("documents", "0007_remove_document_file_document_file_content_and_more"),
        ("appointment", "0010_appointment_observation"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="documents",
            field=models.ManyToManyField(
                related_name="appointments", to="documents.document"
            ),
        ),
    ]
