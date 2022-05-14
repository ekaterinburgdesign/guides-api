# Generated by Django 4.0 on 2022-05-12 17:40

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="PageTreeNode",
            fields=[
                ("id", models.TextField(primary_key=True, serialize=False)),
                ("properties", models.JSONField()),
                ("last_edited", models.DateTimeField()),
                ("child_nodes", models.ManyToManyField(to="app.PageTreeNode")),
                (
                    "child_page",
                    models.ForeignKey(
                        default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to="app.pageelement"
                    ),
                ),
            ],
        ),
    ]