# Generated by Django 4.2.5 on 2024-08-20 06:42

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_initial_permissions"),
    ]

    operations = [
        migrations.AlterField(
            model_name="role",
            name="features",
            field=models.ManyToManyField(related_name="roles", to="core.feature"),
        ),
    ]