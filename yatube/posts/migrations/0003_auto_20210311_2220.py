# Generated by Django 2.2.9 on 2021-03-11 19:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0002_auto_20210310_1227'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ['-pub_date']},
        ),
        migrations.DeleteModel(
            name='Event',
        ),
    ]
