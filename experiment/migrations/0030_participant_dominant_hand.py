# Generated by Django 2.2.13 on 2020-07-08 07:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0029_trialextra'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='dominant_hand',
            field=models.CharField(choices=[('R', 'правая'), ('L', 'левая')], default='R', max_length=1),
            preserve_default=False,
        ),
    ]
