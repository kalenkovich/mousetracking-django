# Generated by Django 2.2.12 on 2020-06-05 05:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0022_auto_20200604_1305'),
    ]

    operations = [
        migrations.RenameField(
            model_name='participant',
            old_name='next_block_number',
            new_name='current_block_number',
        ),
    ]