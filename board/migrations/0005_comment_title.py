# Generated by Django 4.2.3 on 2023-08-01 10:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0004_remove_comment_created_at_remove_comment_updated_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='comment',
            name='title',
            field=models.CharField(default='', max_length=50),
        ),
    ]
