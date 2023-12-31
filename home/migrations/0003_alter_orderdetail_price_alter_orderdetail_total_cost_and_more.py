# Generated by Django 4.2.5 on 2023-09-11 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_category_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdetail',
            name='price',
            field=models.DecimalField(decimal_places=0, default=0, help_text='Price of product at order.', max_digits=12),
        ),
        migrations.AlterField(
            model_name='orderdetail',
            name='total_cost',
            field=models.DecimalField(decimal_places=0, default=0, help_text='total cost of order.', max_digits=12),
        ),
        migrations.AlterField(
            model_name='product',
            name='base_price',
            field=models.DecimalField(decimal_places=0, help_text='The origin price of the product.', max_digits=12),
        ),
    ]
