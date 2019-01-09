from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User


class TMUserAdmin(UserAdmin):
    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'is_active',
        'is_approver',
        'is_purchaser',
    ]

    def is_approver(self, user):
        return user.groups.filter(name="Approvers").exists()

    def is_purchaser(self, user):
        return user.groups.filter(name="Purchasers").exists()

admin.site.unregister(User)
admin.site.register(User, TMUserAdmin)
