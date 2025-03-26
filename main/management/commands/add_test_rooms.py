from django.core.management.base import BaseCommand
from main.models import Room
from django.core.files import File
import os

class Command(BaseCommand):
    help = 'Добавляет тестовые номера в базу данных'

    def handle(self, *args, **kwargs):
        # Список тестовых номеров
        rooms_data = [
            # Стандартные номера
            {
                'room_number': '101',
                'room_type': 'standard',
                'description': 'Стандартный номер с современным дизайном и всеми необходимыми удобствами',
                'price': 3000,
                'image_path': os.path.join('media', 'room_images', 'standard_room1.jpg')
            },
            {
                'room_number': '102',
                'room_type': 'standard',
                'description': 'Уютный стандартный номер с видом на город',
                'price': 3200,
                'image_path': os.path.join('media', 'room_images', 'standard_room2.jpg')
            },
            {
                'room_number': '103',
                'room_type': 'standard',
                'description': 'Стандартный номер с рабочей зоной',
                'price': 3400,
                'image_path': os.path.join('media', 'room_images', 'standard_room3.jpg')
            },
            # Делюкс номера
            {
                'room_number': '201',
                'room_type': 'deluxe',
                'description': 'Делюкс номер с панорамным видом и отдельной гостиной зоной',
                'price': 5000,
                'image_path': os.path.join('media', 'room_images', 'deluxe_room1.jpg')
            },
            {
                'room_number': '202',
                'room_type': 'deluxe',
                'description': 'Делюкс номер с балконом и видом на море',
                'price': 5500,
                'image_path': os.path.join('media', 'room_images', 'deluxe_room2.jpg')
            },
            {
                'room_number': '203',
                'room_type': 'deluxe',
                'description': 'Делюкс номер с отдельной спальней',
                'price': 6000,
                'image_path': os.path.join('media', 'room_images', 'deluxe_room3.jpg')
            },
            # Люксы
            {
                'room_number': '301',
                'room_type': 'suite',
                'description': 'Люкс с отдельной спальней и гостиной, идеально подходит для семейного отдыха',
                'price': 8000,
                'image_path': os.path.join('media', 'room_images', 'suite_room1.jpg')
            },
            {
                'room_number': '302',
                'room_type': 'suite',
                'description': 'Семейный люкс с двумя спальнями',
                'price': 9000,
                'image_path': os.path.join('media', 'room_images', 'suite_room2.jpg')
            },
            {
                'room_number': '303',
                'room_type': 'suite',
                'description': 'Люкс с панорамным видом и террасой',
                'price': 9500,
                'image_path': os.path.join('media', 'room_images', 'suite_room3.jpg')
            },
            # Президентские люксы
            {
                'room_number': '401',
                'room_type': 'presidential',
                'description': 'Президентский люкс с панорамным видом и всеми возможными удобствами',
                'price': 15000,
                'image_path': os.path.join('media', 'room_images', 'presidential_suite1.jpg')
            },
            {
                'room_number': '402',
                'room_type': 'presidential',
                'description': 'Президентский люкс с частным бассейном',
                'price': 18000,
                'image_path': os.path.join('media', 'room_images', 'presidential_suite2.jpg')
            },
            {
                'room_number': '403',
                'room_type': 'presidential',
                'description': 'Президентский люкс с панорамной террасой и джакузи',
                'price': 20000,
                'image_path': os.path.join('media', 'room_images', 'presidential_suite3.jpg')
            },
            # Дополнительные номера
            {
                'room_number': '501',
                'room_type': 'suite',
                'description': 'Люкс с фантаном',
                'price': 8500,
                'image_path': os.path.join('media', 'room_images', 'suite_room1.jpg')
            },
            {
                'room_number': '502',
                'room_type': 'deluxe',
                'description': 'Делюкс номер с видом на сад',
                'price': 4800,
                'image_path': os.path.join('media', 'room_images', 'deluxe_room2.jpg')
            },
            {
                'room_number': '503',
                'room_type': 'standard',
                'description': 'Стандартный номер с видом на город',
                'price': 3100,
                'image_path': os.path.join('media', 'room_images', 'standard_room3.jpg')
            }
        ]

        # Создаем номера
        for room_data in rooms_data:
            room = Room.objects.create(
                room_number=room_data['room_number'],
                room_type=room_data['room_type'],
                description=room_data['description'],
                price=room_data['price']
            )
            
            # Добавляем изображение, если оно существует
            image_path = room_data['image_path']
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    room.image.save(os.path.basename(image_path), File(f), save=True)
            
            self.stdout.write(self.style.SUCCESS(f'Успешно создан номер {room.room_number}')) 