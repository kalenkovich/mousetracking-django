# Generated by Django 2.2.13 on 2020-07-07 13:21

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0028_participant_de_anonymization_code'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrialExtra',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('side', models.CharField(max_length=6)),
                ('polarity', models.CharField(max_length=8)),
                ('object_number', models.IntegerField()),
                ('order', models.CharField(max_length=14)),
                ('orientation', models.CharField(max_length=7)),
                ('configuration', models.CharField(max_length=14)),
                ('target_cell', models.CharField(max_length=6)),
                ('lure_cell', models.CharField(max_length=6)),
                ('objects_list', models.CharField(max_length=66)),
                ('location', models.CharField(max_length=6)),
                ('target', models.CharField(max_length=10)),
                ('lure', models.CharField(max_length=10)),
                ('trial', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='experiment.Trial')),
            ],
        ),
    ]
