from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    dependencies = [
        ("appointment", "0005_review_user"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="review",
            name="service",
        ),
        migrations.AddField(
            model_name="review",
            name="appointment",
            field=models.ForeignKey(
                null=True,  # Permite valores nulos temporariamente
                on_delete=django.db.models.deletion.CASCADE,
                related_name="reviews",
                to="appointment.appointment",
            ),
        ),
    ]
