from django.core.management.base import BaseCommand
from main.models import Role

class Command(BaseCommand):
    help = 'Обновляет название роли с "Работник" на "Сотрудник"'

    def handle(self, *args, **options):
        try:
            role = Role.objects.get(name='Работник')
            role.name = 'Сотрудник'
            role.save()
            self.stdout.write(self.style.SUCCESS('Название роли успешно обновлено'))
        except Role.DoesNotExist:
            self.stdout.write(self.style.WARNING('Роль "Работник" не найдена')) 