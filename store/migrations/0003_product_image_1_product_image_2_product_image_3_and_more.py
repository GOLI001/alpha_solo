# Generated by Django 4.0.6 on 2022-08-12 04:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_variation'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='image_1',
            field=models.ImageField(blank=True, upload_to='photos/products'),
        ),
        migrations.AddField(
            model_name='product',
            name='image_2',
            field=models.ImageField(blank=True, upload_to='photos/products'),
        ),
        migrations.AddField(
            model_name='product',
            name='image_3',
            field=models.ImageField(blank=True, upload_to='photos/products'),
        ),
        migrations.AddField(
            model_name='product',
            name='image_4',
            field=models.ImageField(blank=True, upload_to='photos/products'),
        ),
    ]