# Generated by Django 2.2.12 on 2020-06-03 09:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0018_auto_20200603_1120'),
    ]

    operations = [
        migrations.AddField(
            model_name='trial',
            name='kind',
            field=models.CharField(choices=[('TR', 'training'), ('EXP', 'experiment')], default='EXPERIMENT', max_length=3),
            preserve_default=False,
        ),
    ]
