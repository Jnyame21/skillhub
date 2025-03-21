# Generated by Django 5.0 on 2025-03-20 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Workshop',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255, null=True, verbose_name='Title')),
                ('description', models.TextField(null=True, verbose_name='Title')),
                ('date', models.DateField(null=True, verbose_name='Date')),
                ('start_time', models.TimeField(null=True, verbose_name='Start Time')),
                ('end_time', models.TimeField(null=True, verbose_name='End Time')),
                ('location', models.CharField(max_length=255, null=True, verbose_name='Location')),
                ('max_participants', models.PositiveIntegerField(blank=True, null=True, verbose_name='Maximum number of participants')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
