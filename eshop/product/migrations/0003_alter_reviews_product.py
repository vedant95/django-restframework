# Generated by Django 5.1.2 on 2024-10-27 10:49

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_reviews'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reviews',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='reviews', to='product.product'),
        ),
    ]