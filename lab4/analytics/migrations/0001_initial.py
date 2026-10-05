# Django 6.1.1 арқылы жасалған бастапқы миграция.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Author", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(db_index=True, max_length=120, verbose_name="Автор аты")),
        ]),
        migrations.CreateModel(name="Department", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=120, unique=True, verbose_name="Бөлім атауы")),
        ]),
        migrations.CreateModel(name="Book", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("title", models.CharField(max_length=200, verbose_name="Кітап атауы")),
            ("published_year", models.PositiveSmallIntegerField(verbose_name="Шыққан жылы")),
            ("author", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="books", to="analytics.author", verbose_name="Автор")),
        ], options={"indexes": [models.Index(fields=["author", "published_year"], name="кітап_автор_жыл")]}),
        migrations.CreateModel(name="Employee", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=120, verbose_name="Қызметкер аты")),
            ("salary", models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Жалақы")),
            ("version", models.PositiveIntegerField(default=1, verbose_name="Нұсқа")),
            ("department", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="employees", to="analytics.department", verbose_name="Бөлім")),
        ], options={"indexes": [models.Index(fields=["department", "-salary"], name="қызметкер_бөлім_жалақы")]}),
    ]
