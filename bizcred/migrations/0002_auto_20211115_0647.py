# Generated by Django 3.0.4 on 2021-11-15 06:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bizcred', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='metadata',
            name='account_type',
            field=models.SmallIntegerField(choices=[('', 'Select'), (1, 'Individual'), (2, 'Institution'), (3, 'Lender'), (4, 'Dealer')], default=1),
        ),
    ]
