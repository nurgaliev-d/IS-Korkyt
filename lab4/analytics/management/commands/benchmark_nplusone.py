import time
from django.core.management.base import BaseCommand
from django.test.utils import CaptureQueriesContext
from django.db import connection
from analytics.models import Book


def measure(queryset):
    """Сұраныс саны мен орындалу уақытын өлшейді."""
    started = time.perf_counter()
    with CaptureQueriesContext(connection) as queries:
        names = [book.author.name for book in queryset]
    elapsed = (time.perf_counter() - started) * 1000
    return len(names), len(queries), elapsed, queries.captured_queries


class Command(BaseCommand):
    help = "N+1 қатесін және select_related оңтайландыруын өлшейді."

    def handle(self, *args, **options):
        count, sql_count, elapsed, sql = measure(Book.objects.all())
        self.stdout.write(f"N+1: {count} кітап, {sql_count} SQL сұраныс, {elapsed:.2f} мс")
        self.stdout.write("Алғашқы 3 SQL:\n" + "\n".join(item["sql"] for item in sql[:3]))
        count, sql_count, elapsed, sql = measure(Book.objects.select_related("author"))
        self.stdout.write(f"select_related: {count} кітап, {sql_count} SQL сұраныс, {elapsed:.2f} мс")
        self.stdout.write("Оңтайландырылған SQL:\n" + sql[0]["sql"])
