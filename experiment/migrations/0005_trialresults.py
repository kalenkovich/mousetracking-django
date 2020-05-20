# Generated by Django 2.2.12 on 2020-05-19 09:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('experiment', '0004_auto_20200518_1524'),
    ]

    operations = [
        migrations.CreateModel(
            name='TrialResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_pressed', models.DateTimeField()),
                ('frame_presented', models.DateTimeField()),
                ('audio_started', models.DateTimeField()),
                ('response_selected', models.DateTimeField()),
                ('selected_response', models.CharField(max_length=40)),
                ('trajectory', models.TextField()),
                ('trial', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='experiment.Trial')),
            ],
        ),
    ]
