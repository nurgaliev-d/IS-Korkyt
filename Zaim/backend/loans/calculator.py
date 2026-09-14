from django.core.exceptions import ValidationError


MIN_AMOUNT = 50_000
MAX_AMOUNT = 500_000
MIN_TERM_MONTHS = 1
MAX_TERM_MONTHS = 12
ANNUAL_RATE = 0.24


def calculate_loan(amount: int, term_months: int) -> dict[str, int]:
    """Return a simple fixed-rate annuity estimate in tenge."""
    try:
        amount = int(amount)
        term_months = int(term_months)
    except (TypeError, ValueError) as exc:
        raise ValidationError("Сумма и срок должны быть числами.") from exc

    if not MIN_AMOUNT <= amount <= MAX_AMOUNT:
        raise ValidationError(
            f"Сумма должна быть от {MIN_AMOUNT} до {MAX_AMOUNT} ₸."
        )
    if not MIN_TERM_MONTHS <= term_months <= MAX_TERM_MONTHS:
        raise ValidationError(
            f"Срок должен быть от {MIN_TERM_MONTHS} до {MAX_TERM_MONTHS} месяцев."
        )

    monthly_rate = ANNUAL_RATE / 12
    factor = (1 + monthly_rate) ** term_months
    payment = amount * monthly_rate * factor / (factor - 1)
    monthly_payment = round(payment)

    return {
        "monthly_payment": monthly_payment,
        "total_payment": monthly_payment * term_months,
    }
