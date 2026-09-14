from django.core.exceptions import ValidationError
from django.db import models

from .calculator import calculate_loan


class LoanApplication(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "Новая"
        APPROVED = "approved", "Одобрена"
        REJECTED = "rejected", "Отклонена"

    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=32)
    iin = models.CharField(max_length=12)
    amount = models.PositiveIntegerField()
    term_months = models.PositiveSmallIntegerField()
    monthly_payment = models.PositiveIntegerField(default=0)
    total_payment = models.PositiveIntegerField(default=0)
    status = models.CharField(
        max_length=16,
        choices=Status.choices,
        default=Status.NEW,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        super().clean()
        if self.amount is None or self.term_months is None:
            raise ValidationError("Укажите сумму и срок займа.")
        calculated = calculate_loan(self.amount, self.term_months)
        self.monthly_payment = calculated["monthly_payment"]
        self.total_payment = calculated["total_payment"]
        if len(self.iin or "") != 12 or not (self.iin or "").isdigit():
            raise ValidationError({"iin": "ИИН должен содержать 12 цифр."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Заявка #{self.pk} — {self.full_name}"
