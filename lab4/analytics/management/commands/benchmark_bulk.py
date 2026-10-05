import time
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from analytics.models import Department, Employee


class Command(BaseCommand):
    help = "20 000 жазбаны save() және bulk_create() әдістерімен салыстырады."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=20_000, help="Жасалатын жазба саны")

    def handle(self, *args, **options):
        count = options["count"]
        department, _ = Department.objects.get_or_create(name="Bulk сынақ бөлімі")
        Employee.objects.filter(department=department).delete()
        started = time.perf_counter()
        with transaction.atomic():
            for i in range(count):
                Employee(name=f"Жеке сақтау {i}", department=department, salary=Decimal("250000")).save()
        save_time = (time.perf_counter() - started) * 1000
        Employee.objects.filter(department=department).delete()
        started = time.perf_counter()
        Employee.objects.bulk_create([
            Employee(name=f"Жаппай сақтау {i}", department=department, salary=Decimal("250000"))
            for i in range(count)
        ], batch_size=1000)
        bulk_time = (time.perf_counter() - started) * 1000
        self.stdout.write(f"save(): {count} жазба, {save_time:.2f} мс")
        self.stdout.write(f"bulk_create(): {count} жазба, {bulk_time:.2f} мс")
        self.stdout.write(f"Жеделдету: {save_time / bulk_time:.2f} есе")
