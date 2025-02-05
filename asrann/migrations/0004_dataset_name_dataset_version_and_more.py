# Generated by Django 5.0.6 on 2024-05-21 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('asrann', '0003_alter_dataset_is_compressed'),
    ]

    operations = [
        migrations.AddField(
            model_name='dataset',
            name='name',
            field=models.CharField(default='unknown', max_length=200),
        ),
        migrations.AddField(
            model_name='dataset',
            name='version',
            field=models.CharField(default='0.1.0', max_length=50),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='data_folder',
            field=models.CharField(default='.', max_length=200),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='is_compressed',
            field=models.CharField(choices=[('gzip', 'gzip'), ('zip', 'zip'), ('tar', 'tar'), ('rar', 'rar'), ('bzip2', 'bzip2'), ('wim', 'wim'), ('xz', 'xz'), ('7z', '7z'), ('none', 'none')], default='none', max_length=5),
        ),
    ]
