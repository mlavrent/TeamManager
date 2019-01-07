from django.contrib import admin
from .models import Request


@admin.register(Request)
class RequestModelAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp',
        'item',
        'author',
        'quantity',
        'cost',
        'approved',
        'ordered',
        'delivered',
    ]
