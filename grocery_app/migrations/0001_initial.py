# Generated by Django 5.2.1 on 2025-05-31 18:13

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='GroceryItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('category', models.CharField(choices=[('Fruits & Vegetables', 'Fruits & Vegetables'), ('Dairy & Eggs', 'Dairy & Eggs'), ('Meat & Seafood', 'Meat & Seafood'), ('Bakery', 'Bakery'), ('Pantry Staples', 'Pantry Staples'), ('Frozen Foods', 'Frozen Foods'), ('Beverages', 'Beverages'), ('Snacks', 'Snacks'), ('Health & Beauty', 'Health & Beauty'), ('Household Items', 'Household Items'), ('Other', 'Other')], default='Other', max_length=50)),
                ('quantity', models.IntegerField(default=1)),
                ('unit', models.CharField(choices=[('pieces', 'Pieces'), ('kg', 'Kilograms'), ('grams', 'Grams'), ('liters', 'Liters'), ('ml', 'Milliliters'), ('packets', 'Packets'), ('bottles', 'Bottles'), ('cans', 'Cans'), ('boxes', 'Boxes'), ('loaf', 'Loaf'), ('cups', 'Cups'), ('block', 'Block')], default='pieces', max_length=20)),
                ('price', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('expiry_date', models.DateTimeField(blank=True, null=True)),
                ('last_purchased', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('notes', models.TextField(blank=True)),
                ('barcode', models.CharField(blank=True, max_length=50)),
                ('brand', models.CharField(blank=True, max_length=100)),
                ('store', models.CharField(blank=True, max_length=100)),
                ('nutritional_info', models.JSONField(blank=True, default=dict)),
            ],
            options={
                'ordering': ['name'],
                'indexes': [models.Index(fields=['name'], name='grocery_app_name_add48d_idx'), models.Index(fields=['category'], name='grocery_app_categor_b10bb5_idx'), models.Index(fields=['expiry_date'], name='grocery_app_expiry__91b194_idx')],
            },
        ),
    ]
