from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import LoanApplication
from .serializers import LoanApplicationSerializer


def first_error(errors):
    if isinstance(errors, dict):
        first_value = next(iter(errors.values()), "Проверьте данные заявки.")
        return first_error(first_value)
    if isinstance(errors, list):
        return first_error(errors[0]) if errors else "Проверьте данные заявки."
    return str(errors)


class HealthView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"status": "ok"})


class ApplicationListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        queryset = LoanApplication.objects.all()
        selected_status = request.query_params.get("status")
        valid_statuses = {choice[0] for choice in LoanApplication.Status.choices}

        if selected_status and selected_status not in valid_statuses:
            return Response(
                {"detail": "Неизвестный статус заявки."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if selected_status:
            queryset = queryset.filter(status=selected_status)

        return Response(LoanApplicationSerializer(queryset, many=True).data)

    def post(self, request):
        serializer = LoanApplicationSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": first_error(serializer.errors)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            LoanApplicationSerializer(serializer.save()).data,
            status=status.HTTP_201_CREATED,
        )


class ApplicationStatusView(APIView):
    permission_classes = [AllowAny]

    def patch(self, request, application_id):
        application = get_object_or_404(LoanApplication, pk=application_id)
        new_status = request.data.get("status")
        valid_statuses = {choice[0] for choice in LoanApplication.Status.choices}

        if new_status not in valid_statuses:
            return Response(
                {"detail": "Можно выбрать только новый, одобренный или отклонённый статус."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        application.status = new_status
        application.save(update_fields=["status"])
        return Response(LoanApplicationSerializer(application).data)
