from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from main.models import Room, Booking, Task, TaskStatus, Complaint, ComplaintStatus, Role
from decimal import Decimal
from datetime import datetime, timedelta
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'

    def handle(self, *args, **kwargs):
        # Удаляем существующие данные
        Room.objects.all().delete()
        User = get_user_model()
        User.objects.filter(is_superuser=False).delete()

        # Создаем тестовые номера
        room_types = ['standard', 'deluxe', 'suite', 'presidential']
        amenities = [
            'has_fridge',
            'has_minibar',
            'has_bathroom',
            'has_air_conditioning',
            'has_tv',
            'has_kettle',
            'has_wifi',
            'has_safe',
            'has_balcony',
            'has_jacuzzi',
            'has_kitchen',
            'has_office',
            'has_pool',
            'has_terrace',
            'has_sea_view',
            'has_city_view',
            'has_garden_view'
        ]

        for i in range(1, 16):
            room_type = random.choice(room_types)
            price = {
                'standard': Decimal(random.randint(3000, 5000)),
                'deluxe': Decimal(random.randint(5000, 8000)),
                'suite': Decimal(random.randint(8000, 12000)),
                'presidential': Decimal(random.randint(12000, 20000))
            }[room_type]

            # Создаем случайный набор удобств
            room_amenities = {}
            for amenity in amenities:
                if random.random() < 0.7:  # 70% шанс добавления удобства
                    room_amenities[amenity] = True
                else:
                    room_amenities[amenity] = False

            room = Room.objects.create(
                room_number=str(i),
                room_type=room_type,
                price=price,
                description=f'Описание номера {i}',
                is_available=True,
                **room_amenities
            )
            self.stdout.write(self.style.SUCCESS(f'Создан номер {i}'))

        # Создаем тестовых пользователей
        User = get_user_model()
        
        # Создаем сотрудника
        worker_role = Role.objects.get(name='Сотрудник')
        worker = User.objects.create_user(
            phone='worker',
            password='worker123',
            full_name='Сотрудник',
            role=worker_role
        )
        self.stdout.write(self.style.SUCCESS(f'Создан сотрудник: {worker.full_name}'))

        # Создаем менеджера
        manager_role = Role.objects.get(name='Менеджер')
        manager = User.objects.create_user(
            username='manager',
            phone='+79999999999',
            full_name='Менеджер',
            password='testpass123',
            role=manager_role
        )
        self.stdout.write(self.style.SUCCESS(f'Создан менеджер: {manager.full_name}'))

        # Получаем все номера и пользователей
        rooms = Room.objects.all()
        users = User.objects.filter(is_superuser=False)

        # Создание тестовых бронирований
        for _ in range(10):  # Создаем 10 случайных бронирований
            room = random.choice(rooms)
            user = random.choice(users)
            
            # Генерируем случайные даты
            check_in = datetime.now().date() + timedelta(days=random.randint(1, 30))
            check_out = check_in + timedelta(days=random.randint(1, 14))

            # Проверяем, нет ли уже бронирования на эти даты
            if not Booking.objects.filter(
                room=room,
                check_out__gt=check_in,
                check_in__lt=check_out
            ).exists():
                Booking.objects.create(
                    user=user,
                    room=room,
                    check_in=check_in,
                    check_out=check_out
                )
                room.is_available = False
                room.save()
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Создано бронирование: {user.full_name} - {room.room_number} ({check_in} - {check_out})'
                    )
                )

        # Создание статусов задач
        task_statuses = [
            'Новая',
            'В работе',
            'Выполнена',
            'Отменена'
        ]
        
        for status_name in task_statuses:
            status, created = TaskStatus.objects.get_or_create(name=status_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан статус задачи: {status_name}'))

        # Создание тестовых задач
        for _ in range(5):
            assigned_to = random.choice(users)
            due_date = datetime.now().date() + timedelta(days=random.randint(1, 30))
            status = random.choice(TaskStatus.objects.all())
            
            Task.objects.create(
                assigned_to=assigned_to,
                description=f'Тестовая задача {_+1}',
                due_date=due_date,
                status=status
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Создана задача: {assigned_to.full_name} - {due_date}'
                )
            )

        # Создание статусов жалоб
        complaint_statuses = [
            'Новая',
            'В обработке',
            'Разрешена',
            'Отклонена'
        ]
        
        for status_name in complaint_statuses:
            status, created = ComplaintStatus.objects.get_or_create(name=status_name)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создан статус жалобы: {status_name}'))

        # Создание тестовых жалоб
        bookings = Booking.objects.all()
        for _ in range(3):
            booking = random.choice(bookings)
            status = random.choice(ComplaintStatus.objects.all())
            
            complaint = Complaint.objects.create(
                booking=booking,
                text=f'Тестовая жалоба {_+1}',
                status=status
            )
            
            # Случайно разрешаем некоторые жалобы
            if random.choice([True, False]):
                complaint.resolved_by = random.choice(users)
                complaint.resolution_date = datetime.now().date()
                complaint.save()
                
            self.stdout.write(
                self.style.SUCCESS(
                    f'Создана жалоба: {booking.user.full_name} - {complaint.date}'
                )
            )

        self.stdout.write(self.style.SUCCESS('Тестовые данные успешно созданы')) 