from django.db import models


class Author(models.Model):
    name = models.CharField("Автор аты", max_length=120, db_index=True)

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = "Авторлар"

    def __str__(self):
        return self.name


class Book(models.Model):
    title = models.CharField("Кітап атауы", max_length=200)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name="books", verbose_name="Автор")
    published_year = models.PositiveSmallIntegerField("Шыққан жылы")

    class Meta:
        verbose_name = "Кітап"
        verbose_name_plural = "Кітаптар"
        indexes = [models.Index(fields=["author", "published_year"], name="кітап_автор_жыл")]


class Department(models.Model):
    name = models.CharField("Бөлім атауы", max_length=120, unique=True)

    class Meta:
        verbose_name = "Бөлім"
        verbose_name_plural = "Бөлімдер"

    def __str__(self):
        return self.name


class Employee(models.Model):
    name = models.CharField("Қызметкер аты", max_length=120)
    department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name="employees", verbose_name="Бөлім")
    salary = models.DecimalField("Жалақы", max_digits=12, decimal_places=2)
    version = models.PositiveIntegerField("Нұсқа", default=1)

    class Meta:
        verbose_name = "Қызметкер"
        verbose_name_plural = "Қызметкерлер"
        indexes = [models.Index(fields=["department", "-salary"], name="қызметкер_бөлім_жалақы")]
