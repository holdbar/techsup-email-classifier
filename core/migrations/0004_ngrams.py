# Generated by Django 3.0.5 on 2020-04-21 16:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_constituencytemplate_frequency'),
    ]

    operations = [
        migrations.CreateModel(
            name='Ngrams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('frequency', models.IntegerField(default=0)),
                ('type', models.IntegerField(default=1)),
            ],
        ),
    ]
