from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Booking, Room

@receiver(post_save, sender=Booking)
def update_room_availability_on_booking(sender, instance, created, **kwargs):
    """Обновляет доступность номера при создании бронирования"""
    if created:
        room = instance.room
        room.is_available = False
        room.save()

@receiver(post_delete, sender=Booking)
def update_room_availability_on_booking_delete(sender, instance, **kwargs):
    """Обновляет доступность номера при удалении бронирования"""
    room = instance.room
    # Проверяем, есть ли еще активные бронирования для этого номера
    has_active_bookings = Booking.objects.filter(room=room).exists()
    room.is_available = not has_active_bookings
    room.save() 