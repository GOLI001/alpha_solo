# Generated by Django 4.0.6 on 2022-09-10 10:35

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0004_alter_order_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='Delivery_address',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('firstname', models.CharField(max_length=50)),
                ('lastname', models.CharField(max_length=50, null=True)),
                ('addressfield_1', models.CharField(max_length=250)),
                ('addressfield_2', models.CharField(max_length=50, null=True)),
                ('city', models.CharField(max_length=50)),
                ('state', models.CharField(max_length=50)),
                ('country', models.CharField(max_length=50)),
                ('post_code', models.CharField(max_length=50)),
                ('phonenumber', models.CharField(max_length=50)),
                ('email', models.EmailField(max_length=50)),
                ('user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]