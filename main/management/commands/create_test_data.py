from django.core.management.base import BaseCommand
from main.models import User, Room
from decimal import Decimal

class Command(BaseCommand):
    help = 'Создает тестовые данные: номера и пользователей'

    def handle(self, *args, **kwargs):
        # Создаем менеджера
        manager = User.objects.create_user(
            username="manager",
            phone="+79001234569",
            full_name="Косов Вадим Алексеевич",
            password="Manager12345!",
            is_staff=True,
            is_superuser=False
        )
        self.stdout.write(self.style.SUCCESS(f'Создан менеджер: {manager.full_name}'))

        # Создаем работника
        worker = User.objects.create_user(
            username="worker",
            phone="+79001234570",
            full_name="Леонов Илья Викторович",
            password="Worker12345!",
            is_staff=False,
            is_superuser=False
        )
        self.stdout.write(self.style.SUCCESS(f'Создан работник: {worker.full_name}'))

        # Создаем обычного пользователя
        user = User.objects.create_user(
            username="user",
            phone="+79001234571",
            full_name="Иванов Иван Иванович",
            password="User12345!",
            is_staff=False,
            is_superuser=False
        )
        self.stdout.write(self.style.SUCCESS(f'Создан пользователь: {user.full_name}'))

        # Создаем номера
        room_types = ['standard', 'deluxe', 'suite', 'family']
        amenities = [
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': True, 'has_minibar': False, 'has_safe': False},
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': True, 'has_minibar': True, 'has_safe': True},
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': True, 'has_minibar': True, 'has_safe': True},
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': True, 'has_minibar': False, 'has_safe': True},
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': True, 'has_minibar': True, 'has_safe': False},
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': False, 'has_minibar': True, 'has_safe': True},
            {'has_wifi': True, 'has_tv': False, 'has_air_conditioning': True, 'has_minibar': True, 'has_safe': True},
            {'has_wifi': False, 'has_tv': True, 'has_air_conditioning': True, 'has_minibar': True, 'has_safe': True},
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': True, 'has_minibar': False, 'has_safe': False},
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': True, 'has_minibar': True, 'has_safe': True},
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': True, 'has_minibar': True, 'has_safe': True},
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': True, 'has_minibar': False, 'has_safe': True},
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': True, 'has_minibar': True, 'has_safe': False},
            {'has_wifi': True, 'has_tv': True, 'has_air_conditioning': False, 'has_minibar': True, 'has_safe': True},
            {'has_wifi': True, 'has_tv': False, 'has_air_conditioning': True, 'has_minibar': True, 'has_safe': True}
        ]

        prices = {
            'standard': Decimal('2500.00'),
            'deluxe': Decimal('3500.00'),
            'suite': Decimal('5000.00'),
            'family': Decimal('4000.00')
        }

        descriptions = {
            'standard': 'Стандартный номер с базовыми удобствами',
            'deluxe': 'Улучшенный номер с дополнительными удобствами',
            'suite': 'Люкс с максимальным комфортом',
            'family': 'Семейный номер с расширенным пространством'
        }

        for i in range(15):
            room_type = room_types[i % len(room_types)]
            room = Room.objects.create(
                room_number=f"{100 + i}",
                room_type=room_type,
                price=prices[room_type],
                description=descriptions[room_type],
                is_available=True,
                **amenities[i]
            )
            self.stdout.write(self.style.SUCCESS(f'Создан номер: {room.room_number} ({room_type})')) 