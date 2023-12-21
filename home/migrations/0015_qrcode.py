# Generated by Django 5.0 on 2023-12-18 01:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0014_alter_product_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='QRCode',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_number', models.IntegerField(unique=True)),
                ('qr_code_data', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]