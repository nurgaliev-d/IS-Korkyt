from django.http import HttpResponse
from .models import Author, Book, Department, Employee


def index(request):
    return HttpResponse(
        "<h1>ORM өнімділігін талдау зертханасы</h1>"
        f"<p>Авторлар: {Author.objects.count()}, кітаптар: {Book.objects.count()}</p>"
        f"<p>Бөлімдер: {Department.objects.count()}, қызметкерлер: {Employee.objects.count()}</p>"
        "<p>Нұсқаулар үшін README.md файлын ашыңыз.</p>"
    )
