# Generated by Django 2.2 on 2019-10-09 21:27

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='author',
            field=models.ForeignKey(default=None, on_delete='Article', to=settings.AUTH_USER_MODEL),
        ),
    ]
