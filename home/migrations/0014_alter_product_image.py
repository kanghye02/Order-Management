# Generated by Django 4.2.5 on 2023-10-06 00:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_review'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.ImageField(blank=True, default='homepage/image404.png', help_text='Product image', null=True, upload_to='product_images/'),
        ),
    ]
