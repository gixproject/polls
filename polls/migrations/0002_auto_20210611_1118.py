# Generated by Django 3.2.3 on 2021-06-11 11:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='user_agent',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='poll',
            name='multi_selection',
            field=models.BooleanField(default=False),
        ),
    ]
