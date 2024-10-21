# Generated by Django 4.2.5 on 2024-10-21 04:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("service", "0002_alter_service_id"),
        ("appointment", "0006_remove_review_service_review_appointment"),
    ]

    operations = [
        migrations.AlterField(
            model_name="appointment",
            name="services",
            field=models.ManyToManyField(
                related_name="appointments", to="service.service"
            ),
        ),
        migrations.AlterField(
            model_name="review",
            name="appointment",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reviews",
                to="appointment.appointment",
            ),
            preserve_default=False,
        ),
    ]
