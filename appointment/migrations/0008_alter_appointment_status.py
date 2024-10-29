# Generated by Django 4.2.5 on 2024-10-29 00:24

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("appointment", "0007_alter_appointment_services_alter_review_appointment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="status",
            field=models.CharField(
                choices=[
                    ("Agendado", "Pending"),
                    ("Em andamento", "In Progress"),
                    ("Cancelado", "Canceled"),
                    ("Concluido", "Completed"),
                ],
                default="Agendado",
                max_length=20,
            ),
        ),
    ]
