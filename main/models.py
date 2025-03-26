from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, PermissionsMixin
from django.core.validators import MinValueValidator, RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError

class CustomUserManager(BaseUserManager):
    def create_user(self, phone, full_name, password=None, **extra_fields):
        if not phone:
            raise ValueError('Номер телефона обязателен')
        if not full_name:
            raise ValueError('ФИО обязательно')

        user = self.model(phone=phone, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(phone, full_name, password, **extra_fields)

class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Роль'
        verbose_name_plural = 'Роли'

class User(AbstractUser):
    phone = models.CharField(max_length=12, unique=True)
    email = models.EmailField(max_length=100, null=True, blank=True, verbose_name="Электронная почта")
    full_name = models.CharField(max_length=100)
    photo = models.ImageField(upload_to='user_photos/', null=True, blank=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    registration_date = models.DateField(auto_now_add=True, verbose_name="Дата регистрации")

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)

    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.phone
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        db_table = 'Users'

class Room(models.Model):
    ROOM_TYPES = [
        ('standard', 'Стандартный'),
        ('deluxe', 'Делюкс'),
        ('suite', 'Люкс'),
        ('presidential', 'Президентский люкс'),
    ]

    room_number = models.CharField(max_length=10, unique=True, verbose_name="Номер")
    room_type = models.CharField(max_length=20, choices=ROOM_TYPES, verbose_name="Тип номера")
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)], verbose_name="Цена")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='room_images/', null=True, blank=True, verbose_name="Изображение")
    
    # Удобства в номере
    has_fridge = models.BooleanField(default=False, verbose_name='Холодильник')
    has_minibar = models.BooleanField(default=True, verbose_name='Мини-бар')
    has_bathroom = models.BooleanField(default=True, verbose_name='Ванная комната')
    has_air_conditioning = models.BooleanField(default=True, verbose_name='Кондиционер')
    has_tv = models.BooleanField(default=True, verbose_name='Телевизор')
    has_kettle = models.BooleanField(default=True, verbose_name='Чайник')
    has_wifi = models.BooleanField(default=True, verbose_name='Wi-Fi')
    has_safe = models.BooleanField(default=True, verbose_name='Сейф')
    has_balcony = models.BooleanField(default=False, verbose_name='Балкон')
    has_jacuzzi = models.BooleanField(default=False, verbose_name='Джакузи')
    has_kitchen = models.BooleanField(default=False, verbose_name='Кухня')
    has_office = models.BooleanField(default=False, verbose_name='Офис')
    has_pool = models.BooleanField(default=False, verbose_name='Бассейн')
    has_terrace = models.BooleanField(default=False, verbose_name='Тераса')
    has_sea_view = models.BooleanField(default=False, verbose_name='Вид на море')
    has_city_view = models.BooleanField(default=False, verbose_name='Вид на город')
    has_garden_view = models.BooleanField(default=False, verbose_name='Вид на сад')
    
    is_available = models.BooleanField(default=True, verbose_name="Доступен")

    def __str__(self):
        return f"Номер {self.room_number} - {self.get_room_type_display()}"

    class Meta:
        verbose_name = 'Номер'
        verbose_name_plural = 'Номера'
        db_table = 'Rooms'

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey('Room', on_delete=models.CASCADE, related_name='bookings')
    check_in = models.DateField()
    check_out = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        # Проверяем, нет ли конфликтующих бронирований
        conflicting_bookings = Booking.objects.filter(
            room=self.room,
            check_in__lte=self.check_out,
            check_out__gte=self.check_in
        ).exclude(id=self.id)
        
        if conflicting_bookings.exists():
            raise ValidationError('Номер уже забронирован на эти даты')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Обновляем статус доступности номера
        self.room.is_available = False
        self.room.save()

    class Meta:
        db_table = 'Bookings'

class TaskStatus(models.Model):
    """Модель для статусов задач"""
    name = models.CharField(max_length=50, verbose_name="Название статуса")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статус задачи'
        verbose_name_plural = 'Статусы задач'
        db_table = 'TaskStatus'

class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('completed', 'Выполнена'),
        ('cancelled', 'Отменена'),
    ]

    title = models.CharField(max_length=200, verbose_name='Название')
    description = models.TextField(verbose_name='Описание')
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks', verbose_name='Назначен')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks', verbose_name='Создал')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')
    due_date = models.DateTimeField(verbose_name='Срок выполнения')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name='Статус')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='Выполнено')
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.assigned_to.full_name}"

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['-created_at']

class ComplaintStatus(models.Model):
    """Модель для статусов жалоб"""
    name = models.CharField(max_length=50, verbose_name="Название статуса")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Статус жалобы'
        verbose_name_plural = 'Статусы жалоб'
        db_table = 'ComplaintStatus'

class Complaint(models.Model):
    """Модель для жалоб"""
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, verbose_name="Бронирование")
    text = models.TextField(verbose_name="Текст жалобы")
    date = models.DateField(auto_now_add=True, verbose_name="Дата жалобы")
    status = models.ForeignKey(ComplaintStatus, on_delete=models.CASCADE, verbose_name="Статус")
    resolved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Разрешил")
    resolution_date = models.DateField(null=True, blank=True, verbose_name="Дата разрешения")

    def __str__(self):
        return f"Жалоба от {self.booking.user.full_name} - {self.text[:50]}"

    class Meta:
        verbose_name = 'Жалоба'
        verbose_name_plural = 'Жалобы'
        db_table = 'Complaint'