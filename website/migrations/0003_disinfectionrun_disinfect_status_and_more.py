# Generated by Django 4.2.3 on 2023-08-09 10:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0002_alter_disinfectionrun_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='disinfectionrun',
            name='disinfect_status',
            field=models.CharField(default='Pending', max_length=255),
        ),
        migrations.AddField(
            model_name='disinfectionrun',
            name='run_status',
            field=models.CharField(default='Pending', max_length=255),
        ),
    ]
