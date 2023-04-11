from django.contrib import admin
from users.models import User


class UserAdmin(admin.ModelAdmin):
    """Класс для работы с пользователями в админ-панели."""
    list_display = ('email', 'username', 'first_name', 'last_name')
    search_fields = ('username', 'email')


admin.site.register(User, UserAdmin)
