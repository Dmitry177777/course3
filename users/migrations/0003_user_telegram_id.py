# Generated by Django 4.2.5 on 2023-10-08 18:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_user_managers_remove_user_username_user_avatar_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='telegram_id',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='id телеграмм'),
        ),
    ]