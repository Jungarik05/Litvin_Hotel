from django.conf import settings
from django.contrib.auth import get_user_model

class AdminSessionMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Проверяем, является ли текущий URL админкой
        if request.path.startswith('/admin/'):
            # Если пользователь авторизован и является суперпользователем
            if request.user.is_authenticated and request.user.is_superuser:
                # Сохраняем сессию админки
                request.session['admin_session'] = True
        else:
            # Если пользователь авторизован и является суперпользователем
            if request.user.is_authenticated and request.user.is_superuser:
                # Проверяем наличие сессии админки
                if request.session.get('admin_session'):
                    # Если сессия админки существует, не выходим из аккаунта
                    request.user.is_authenticated = True

        response = self.get_response(request)
        return response 