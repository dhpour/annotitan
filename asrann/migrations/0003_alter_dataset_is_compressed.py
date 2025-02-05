# Generated by Django 5.0.6 on 2024-05-21 17:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asrann', '0002_alter_dataset_is_compressed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='dataset',
            name='is_compressed',
            field=models.CharField(choices=[('gzip', 'gzip'), ('zip', 'zip'), ('tar', 'tar'), ('rar', 'rar'), ('bzip2', 'bzip2'), ('wim', 'wim'), ('xz', 'xz'), ('7z', '7z'), ('none', 'none')], default=None, max_length=5),
        ),
    ]
