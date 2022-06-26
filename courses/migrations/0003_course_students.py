# Generated by Django 4.0.1 on 2022-01-31 14:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('courses', '0002_module'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='students',
            field=models.ManyToManyField(blank=True, related_name='courses_enrolled', to='courses.StudentProfile'),
        ),
    ]
