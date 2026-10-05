from django.db import transaction
from django.db.models import F
from .models import Employee


def pessimistic_raise(employee_id, amount):
    """Пессимистік құлып: жолды транзакция аяқталғанша бұғаттайды."""
    with transaction.atomic():
        employee = Employee.objects.select_for_update().get(pk=employee_id)
        employee.salary = F("salary") + amount
        employee.save(update_fields=["salary"])


def optimistic_raise(employee_id, known_version, amount):
    """Оптимистік құлып: өзгертілген нұсқа ғана жаңартылады."""
    changed = Employee.objects.filter(pk=employee_id, version=known_version).update(
        salary=F("salary") + amount, version=F("version") + 1
    )
    if changed != 1:
        raise RuntimeError("Дерек басқа транзакциямен өзгертілген, қайта оқып көріңіз.")
