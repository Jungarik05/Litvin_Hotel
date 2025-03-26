from django.core.management.base import BaseCommand
from main.models import User, Room
from decimal import Decimal

class Command(BaseCommand):
    help = 'Создает тестовые данные'

    def handle(self, *args, **kwargs):
        # Создание суперпользователя
        if not User.objects.filter(phone='+79215250705').exists():
            User.objects.create_superuser(
                phone='+79215250705',
                full_name='Водвуд Владислав Викторович',
                password='1Vladislav'
            )
            self.stdout.write(self.style.SUCCESS('Суперпользователь создан'))

        # Создание тестовых номеров
        rooms_data = [
            {
                'room_number': '101',
                'room_type': 'standard',
                'price': Decimal('3000.00'),
                'description': 'Стандартный номер с современным дизайном',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True
            },
            {
                'room_number': '102',
                'room_type': 'deluxe',
                'price': Decimal('3500.00'),
                'description': 'Делюкс номер с видом на город',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_balcony': True,
                'has_city_view': True
            },
            {
                'room_number': '201',
                'room_type': 'suite',
                'price': Decimal('5000.00'),
                'description': 'Люкс с гостиной и спальней',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_jacuzzi': True,
                'has_kitchen': True
            },
            {
                'room_number': '202',
                'room_type': 'suite',
                'price': Decimal('7000.00'),
                'description': 'Люкс с панорамным видом',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_balcony': True,
                'has_sea_view': True
            },
            {
                'room_number': '301',
                'room_type': 'presidential',
                'price': Decimal('15000.00'),
                'description': 'Президентский люкс с отдельным бассейном',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_jacuzzi': True,
                'has_kitchen': True,
                'has_office': True,
                'has_pool': True,
                'has_terrace': True,
                'has_sea_view': True
            },
            {
                'room_number': '103',
                'room_type': 'standard',
                'price': Decimal('3200.00'),
                'description': 'Стандартный номер с видом на сад',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_garden_view': True
            },
            {
                'room_number': '104',
                'room_type': 'deluxe',
                'price': Decimal('3800.00'),
                'description': 'Делюкс номер с балконом',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_balcony': True
            },
            {
                'room_number': '203',
                'room_type': 'suite',
                'price': Decimal('6000.00'),
                'description': 'Люкс с джакузи',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_jacuzzi': True
            },
            {
                'room_number': '204',
                'room_type': 'suite',
                'price': Decimal('6500.00'),
                'description': 'Люкс с кухней',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_kitchen': True
            },
            {
                'room_number': '302',
                'room_type': 'presidential',
                'price': Decimal('12000.00'),
                'description': 'Президентский люкс с офисом',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_office': True
            },
            {
                'room_number': '303',
                'room_type': 'presidential',
                'price': Decimal('13000.00'),
                'description': 'Президентский люкс с бассейном',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_pool': True
            },
            {
                'room_number': '304',
                'room_type': 'presidential',
                'price': Decimal('14000.00'),
                'description': 'Президентский люкс с террасой',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_terrace': True
            },
            {
                'room_number': '105',
                'room_type': 'standard',
                'price': Decimal('3100.00'),
                'description': 'Стандартный номер с холодильником',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': False,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True
            },
            {
                'room_number': '205',
                'room_type': 'suite',
                'price': Decimal('5500.00'),
                'description': 'Люкс с видом на море',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_sea_view': True
            },
            {
                'room_number': '305',
                'room_type': 'presidential',
                'price': Decimal('16000.00'),
                'description': 'Президентский люкс с максимальным комфортом',
                'is_available': True,
                'has_fridge': True,
                'has_minibar': True,
                'has_bathroom': True,
                'has_air_conditioning': True,
                'has_tv': True,
                'has_kettle': True,
                'has_wifi': True,
                'has_safe': True,
                'has_jacuzzi': True,
                'has_kitchen': True,
                'has_office': True,
                'has_pool': True,
                'has_terrace': True,
                'has_sea_view': True,
                'has_city_view': True,
                'has_garden_view': True
            }
        ]

        for room_data in rooms_data:
            Room.objects.get_or_create(
                room_number=room_data['room_number'],
                defaults=room_data
            )
        
        self.stdout.write(self.style.SUCCESS('Тестовые номера созданы')) 