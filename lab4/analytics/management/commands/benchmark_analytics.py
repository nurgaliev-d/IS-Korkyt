import time
import tracemalloc
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Avg, F, Window
from django.db.models.functions import DenseRank
from django.test.utils import CaptureQueriesContext
from analytics.models import Employee


def orm_query():
    return Employee.objects.annotate(
        department_average=Window(Avg("salary"), partition_by=[F("department_id")]),
        salary_rank=Window(DenseRank(), partition_by=[F("department_id")], order_by=F("salary").desc()),
    ).filter(salary_rank__lte=3).order_by("department_id", "salary_rank")


RAW_SQL = """
SELECT id, name, department_id, salary, department_average, salary_rank,
       salary - department_average AS difference_from_average
FROM (
  SELECT e.id, e.name, e.department_id, e.salary,
         AVG(e.salary) OVER (PARTITION BY e.department_id) AS department_average,
         DENSE_RANK() OVER (PARTITION BY e.department_id ORDER BY e.salary DESC) AS salary_rank
  FROM analytics_employee e
) ranked
WHERE salary_rank <= 3
ORDER BY department_id, salary_rank
"""


def profile(callback):
    tracemalloc.start()
    started = time.perf_counter()
    rows = callback()
    elapsed = (time.perf_counter() - started) * 1000
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return len(rows), elapsed, peak / 1024


class Command(BaseCommand):
    help = "Терезелік функциясы бар ORM және Raw SQL сұраныстарын салыстырады."

    def handle(self, *args, **options):
        with CaptureQueriesContext(connection) as sql:
            orm_result = profile(lambda: list(orm_query()))
        raw_result = profile(lambda: list(Employee.objects.raw(RAW_SQL)))
        self.stdout.write(f"ORM: {orm_result[0]} жол, {orm_result[1]:.2f} мс, шың RAM {orm_result[2]:.1f} КиБ")
        self.stdout.write(f"Raw SQL: {raw_result[0]} жол, {raw_result[1]:.2f} мс, шың RAM {raw_result[2]:.1f} КиБ")
        self.stdout.write("\nORM жасаған SQL:\n" + sql.captured_queries[0]["sql"])
        self.stdout.write("\nҚолмен жазылған SQL:\n" + RAW_SQL.strip())
