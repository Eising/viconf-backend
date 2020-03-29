# Generated by Django 3.0.4 on 2020-03-24 08:10

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=255, null=True)),
                ('password', models.CharField(max_length=255, null=True)),
                ('enable_password', models.CharField(max_length=255, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Node',
            fields=[
                ('hostname', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('ipv4', models.CharField(blank=True, max_length=255, null=True)),
                ('ipv6', models.CharField(blank=True, max_length=255, null=True)),
                ('driver', models.CharField(choices=[('eos', 'Arista EOS'), ('junos', 'Juniper JUNOS'), ('iosxr', 'Cisco IOS-XR'), ('nxos', 'Cisco NXOS'), ('ios', 'Cisco IOS'), ('none', 'No driver')], max_length=255)),
                ('comment', models.TextField(null=True)),
                ('site', models.CharField(max_length=255)),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='configuration.Group')),
            ],
        ),
        migrations.CreateModel(
            name='ResourceService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('defaults', django.contrib.postgres.fields.jsonb.JSONField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('node', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='configuration.Node')),
            ],
        ),
        migrations.CreateModel(
            name='ResourceTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('description', models.CharField(max_length=255, null=True)),
                ('platform', models.CharField(max_length=255, null=True)),
                ('up_contents', models.TextField()),
                ('down_contents', models.TextField()),
                ('fields', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('labels', django.contrib.postgres.fields.jsonb.JSONField(null=True)),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('resource_services', models.ManyToManyField(to='configuration.ResourceService')),
            ],
        ),
        migrations.CreateModel(
            name='ServiceOrders',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reference', models.CharField(max_length=255)),
                ('customer', models.CharField(max_length=255, null=True)),
                ('location', models.CharField(max_length=255, null=True)),
                ('speed', models.IntegerField(null=True)),
                ('template_fields', django.contrib.postgres.fields.jsonb.JSONField()),
                ('deleted', models.BooleanField(default=False)),
                ('created', models.DateTimeField(auto_now=True)),
                ('modified', models.DateTimeField(auto_now=True)),
                ('service', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='configuration.Service')),
            ],
        ),
        migrations.AddField(
            model_name='resourceservice',
            name='resource_templates',
            field=models.ManyToManyField(to='configuration.ResourceTemplate'),
        ),
    ]