# Generated by Django 4.2.3 on 2023-09-08 07:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0004_filtereddata'),
    ]

    operations = [
        migrations.AddField(
            model_name='filtereddata',
            name='ip_address',
            field=models.GenericIPAddressField(default='0.0.0.0'),
        ),
    ]
