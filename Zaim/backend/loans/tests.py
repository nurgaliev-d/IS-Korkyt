from django.core.exceptions import ValidationError
from django.test import SimpleTestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .calculator import calculate_loan
from .models import LoanApplication


class LoanCalculatorTests(SimpleTestCase):
    def test_calculates_six_month_plan(self):
        result = calculate_loan(150000, 6)
        self.assertEqual(result["monthly_payment"], 26779)
        self.assertEqual(result["total_payment"], 160674)

    def test_rejects_amount_outside_limits(self):
        with self.assertRaises(ValidationError):
            calculate_loan(10000, 6)


class LoanApplicationApiTests(APITestCase):
    def payload(self, **overrides):
        values = {
            "full_name": "Алия Сейтова",
            "phone": "+7 700 123 45 67",
            "iin": "000000000000",
            "amount": 150000,
            "term_months": 6,
        }
        values.update(overrides)
        return values

    def test_health_endpoint(self):
        response = self.client.get("/api/health/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), {"status": "ok"})

    def test_create_recalculates_payment_on_server(self):
        response = self.client.post(
            "/api/applications/",
            {**self.payload(), "monthly_payment": 1},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.json()["monthly_payment"], 26779)
        self.assertEqual(LoanApplication.objects.count(), 1)

    def test_rejects_invalid_iin(self):
        response = self.client.post(
            "/api/applications/",
            self.payload(iin="123"),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("ИИН", response.json()["detail"])

    def test_rejects_amount_outside_limits(self):
        response = self.client.post(
            "/api/applications/",
            self.payload(amount=10000),
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Сумма", response.json()["detail"])

    def test_filters_applications_by_status(self):
        first = LoanApplication.objects.create(**self.payload())
        second = LoanApplication.objects.create(
            **self.payload(full_name="Нурлан Ермеков", iin="111111111111")
        )
        second.status = LoanApplication.Status.APPROVED
        second.save(update_fields=["status"])

        response = self.client.get("/api/applications/?status=approved")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual([item["id"] for item in response.json()], [second.id])
        self.assertNotEqual(first.id, second.id)

    def test_updates_application_status(self):
        application = LoanApplication.objects.create(**self.payload())

        response = self.client.patch(
            f"/api/applications/{application.id}/status/",
            {"status": "rejected"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["status"], "rejected")

    def test_rejects_unknown_status(self):
        application = LoanApplication.objects.create(**self.payload())

        response = self.client.patch(
            f"/api/applications/{application.id}/status/",
            {"status": "paid"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
