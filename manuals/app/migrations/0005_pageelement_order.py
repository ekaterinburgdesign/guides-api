# Generated by Django 4.0 on 2022-06-06 16:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0004_pagetreenode_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="pageelement",
            name="order",
            field=models.IntegerField(db_index=True, default=0),
        ),
    ]
