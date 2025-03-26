from django.core.management.base import BaseCommand
from main.models import Role

class Command(BaseCommand):
    help = 'Создает базовые роли пользователей'

    def handle(self, *args, **kwargs):
        roles = [
            {
                'name': 'Пользователь',
                'description': 'Обычный пользователь системы'
            },
            {
                'name': 'Сотрудник',
                'description': 'Сотрудник отеля'
            },
            {
                'name': 'Менеджер',
                'description': 'Менеджер отеля с правами управления задачами'
            }
        ]

        for role_data in roles:
            role, created = Role.objects.get_or_create(
                name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана роль "{role.name}"'))
            else:
                self.stdout.write(self.style.WARNING(f'Роль "{role.name}" уже существует')) 