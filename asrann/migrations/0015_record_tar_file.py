# Generated by Django 5.0.6 on 2024-07-31 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asrann', '0014_delete_seen'),
    ]

    operations = [
        migrations.AddField(
            model_name='record',
            name='tar_file',
            field=models.SmallIntegerField(blank=True, default=0, null=True),
        ),
    ]
