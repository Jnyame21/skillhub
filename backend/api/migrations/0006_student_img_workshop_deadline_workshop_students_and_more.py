# Generated by Django 5.0 on 2025-03-20 20:36

import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_student_gender'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='img',
            field=models.ImageField(blank=True, max_length=255, null=True, upload_to=api.models.get_student_folder, verbose_name='Image'),
        ),
        migrations.AddField(
            model_name='workshop',
            name='deadline',
            field=models.DateField(null=True, verbose_name='Deadline for registration'),
        ),
        migrations.AddField(
            model_name='workshop',
            name='students',
            field=models.ManyToManyField(blank=True, to='api.student', verbose_name='Students'),
        ),
        migrations.DeleteModel(
            name='Registration',
        ),
    ]
