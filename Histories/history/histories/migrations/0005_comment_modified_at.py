# Generated by Django 4.2.4 on 2023-09-02 13:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('histories', '0004_history_modified_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
