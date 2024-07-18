from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import School, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ["school"]}),)
    add_fieldsets = UserAdmin.add_fieldsets + ((None, {"fields": ["school"]}),)

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ["name"]