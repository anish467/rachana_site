# Generated by Django 5.1 on 2025-06-14 05:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='image',
            field=models.ImageField(default='category_images/default.jpg', upload_to='category_images/'),
        ),
    ]
