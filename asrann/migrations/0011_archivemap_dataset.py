# Generated by Django 5.0.6 on 2024-07-31 00:05

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asrann', '0010_appconfig'),
    ]

    operations = [
        migrations.AddField(
            model_name='archivemap',
            name='dataset',
            field=models.ForeignKey(default='41ba3e56-7373-4881-a44b-2794e0687a33', on_delete=django.db.models.deletion.DO_NOTHING, to='asrann.dataset'),
            preserve_default=False,
        ),
    ]
