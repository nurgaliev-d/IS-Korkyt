import random
from decimal import Decimal
from django.core.management.base import BaseCommand
from analytics.models import Author, Book, Department, Employee


class Command(BaseCommand):
    help = "Зертханаға арналған 1 000 кітап және 12 000 қызметкер жасайды."

    def handle(self, *args, **options):
        if Author.objects.exists() or Employee.objects.exists():
            self.stdout.write(self.style.WARNING("Деректер бар. Қайта толтыру орындалмады."))
            return
        authors = Author.objects.bulk_create([Author(name=f"Автор {i}") for i in range(1, 101)])
        Book.objects.bulk_create([
            Book(title=f"Кітап {i}", author=authors[(i - 1) % len(authors)], published_year=2000 + i % 25)
            for i in range(1, 1001)
        ])
        departments = Department.objects.bulk_create([Department(name=f"Бөлім {i}") for i in range(1, 21)])
        random.seed(42)
        Employee.objects.bulk_create([
            Employee(
                name=f"Қызметкер {i}", department=departments[(i - 1) % len(departments)],
                salary=Decimal(random.randint(180_000, 1_200_000)),
            ) for i in range(1, 12001)
        ], batch_size=1000)
        self.stdout.write(self.style.SUCCESS("100 автор, 1 000 кітап, 20 бөлім, 12 000 қызметкер жасалды."))
