# Generated by Django 3.0.4 on 2020-04-05 08:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0002_auto_20200324_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='node',
            name='ipv4',
            field=models.GenericIPAddressField(blank=True, null=True, protocol='IPv4'),
        ),
        migrations.AlterField(
            model_name='node',
            name='ipv6',
            field=models.GenericIPAddressField(blank=True, null=True, protocol='IPv6'),
        ),
    ]
