from django.contrib.admin import AdminSite
from django.conf import settings

class CustomAdminSite(AdminSite):
    site_header = settings.ADMIN_SITE_HEADER
    site_title = settings.ADMIN_SITE_TITLE
    index_title = settings.ADMIN_INDEX_TITLE
    
    def get_app_list(self, request):
        """
        Возвращает список приложений для админки
        """
        app_list = super().get_app_list(request)
        return app_list

# Создаем экземпляр админки
admin_site = CustomAdminSite(name='admin')

# Регистрируем модели
from .models import Room, Booking, User
admin_site.register(Room)
admin_site.register(Booking)
admin_site.register(User) 