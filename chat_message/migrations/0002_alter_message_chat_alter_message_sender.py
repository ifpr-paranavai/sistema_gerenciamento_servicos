# Generated by Django 4.2.5 on 2024-12-01 21:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("authentication", "0008_remove_user_is_staff"),
        ("chat_message", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="message",
            name="chat",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="messages",
                to="chat_message.chat",
            ),
        ),
        migrations.AlterField(
            model_name="message",
            name="sender",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="authentication.user"
            ),
        ),
    ]
