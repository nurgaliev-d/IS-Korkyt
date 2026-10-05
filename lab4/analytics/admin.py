from django.contrib import admin
from .models import Author, Book, Department, Employee

admin.site.register([Author, Book, Department, Employee])
