from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from .calculator import calculate_loan
from .models import LoanApplication


class LoanApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanApplication
        fields = [
            "id",
            "full_name",
            "phone",
            "iin",
            "amount",
            "term_months",
            "monthly_payment",
            "total_payment",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "monthly_payment",
            "total_payment",
            "status",
            "created_at",
        ]

    def validate_full_name(self, value):
        value = value.strip()
        if len(value) < 3:
            raise serializers.ValidationError("Укажите имя и фамилию.")
        return value

    def validate_phone(self, value):
        value = value.strip()
        if len(value) < 10:
            raise serializers.ValidationError("Введите номер телефона.")
        return value

    def validate_iin(self, value):
        if len(value) != 12 or not value.isdigit():
            raise serializers.ValidationError("ИИН должен содержать 12 цифр.")
        return value

    def validate(self, attrs):
        try:
            calculate_loan(attrs.get("amount"), attrs.get("term_months"))
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message) from exc
        return attrs

    def create(self, validated_data):
        calculated = calculate_loan(
            validated_data["amount"], validated_data["term_months"]
        )
        return LoanApplication.objects.create(
            **validated_data,
            **calculated,
        )
