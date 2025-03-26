from django import forms
from .models import Room, User, Booking, Task, Complaint, ComplaintStatus
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.utils import timezone
import re

class RegistrationForm(UserCreationForm):
    phone = forms.CharField(
        max_length=12,
        help_text='Введите номер телефона в формате +79001234567'
    )
    full_name = forms.CharField(max_length=100)

    class Meta:
        model = get_user_model()
        fields = ('phone', 'full_name', 'password1', 'password2')

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if not re.match(r'^\+7\d{10}$', phone):
            raise forms.ValidationError('Номер телефона должен быть в формате +79001234567')
        if get_user_model().objects.filter(phone=phone).exists():
            raise forms.ValidationError('Этот номер телефона уже зарегистрирован')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.phone = self.cleaned_data['phone']
        user.full_name = self.cleaned_data['full_name']
        if commit:
            user.save()
        return user

class RoomFilterForm(forms.Form):
    room_type = forms.ChoiceField(
        choices=[('', 'Все типы')] + Room.ROOM_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    min_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Мин. цена'})
    )
    max_price = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Макс. цена'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Поиск по номеру или описанию'})
    )

class BookingForm(forms.Form):
    room = forms.ModelChoiceField(
        queryset=Room.objects.filter(is_available=True),
        label="Номер",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    check_in = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat()
        }),
        label="Дата заезда"
    )
    check_out = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'min': timezone.now().date().isoformat()
        }),
        label="Дата выезда"
    )

    def clean(self):
        cleaned_data = super().clean()
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        room = cleaned_data.get('room')

        if check_in and check_out and room:
            # Проверяем, что даты не в прошлом
            today = timezone.now().date()
            if check_in < today:
                raise forms.ValidationError('Дата заезда не может быть в прошлом')
            if check_out < today:
                raise forms.ValidationError('Дата выезда не может быть в прошлом')

            if check_out <= check_in:
                raise forms.ValidationError('Дата выезда должна быть позже даты заезда')

            # Проверяем, не занят ли номер на эти даты
            overlapping_bookings = Booking.objects.filter(
                room=room,
                check_out__gt=check_in,
                check_in__lt=check_out
            ).exists()

            if overlapping_bookings:
                raise forms.ValidationError('Этот номер уже забронирован на выбранные даты')

        return cleaned_data

class TaskForm(forms.ModelForm):
    assigned_to = forms.ModelChoiceField(
        queryset=User.objects.filter(role__name='Сотрудник'),
        label='Назначить сотруднику',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Task
        fields = ['title', 'description', 'assigned_to', 'due_date', 'status']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'title': 'Название задачи',
            'description': 'Описание',
            'due_date': 'Срок выполнения',
            'status': 'Статус',
        }

class RoomForm(forms.ModelForm):
    class Meta:
        model = Room
        fields = [
            'room_number', 'room_type', 'price', 'description', 'image',
            'has_fridge', 'has_minibar', 'has_bathroom', 'has_air_conditioning',
            'has_tv', 'has_kettle', 'has_wifi', 'has_safe', 'has_balcony',
            'has_jacuzzi', 'has_kitchen', 'has_office', 'has_pool', 'has_terrace',
            'has_sea_view', 'has_city_view', 'has_garden_view'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
        }
        labels = {
            'room_number': 'Номер комнаты',
            'room_type': 'Тип номера',
            'price': 'Цена за ночь',
            'description': 'Описание',
            'image': 'Изображение',
            'has_fridge': 'Холодильник',
            'has_minibar': 'Мини-бар',
            'has_bathroom': 'Ванная комната',
            'has_air_conditioning': 'Кондиционер',
            'has_tv': 'Телевизор',
            'has_kettle': 'Чайник',
            'has_wifi': 'Wi-Fi',
            'has_safe': 'Сейф',
            'has_balcony': 'Балкон',
            'has_jacuzzi': 'Джакузи',
            'has_kitchen': 'Кухня',
            'has_office': 'Офис',
            'has_pool': 'Бассейн',
            'has_terrace': 'Тераса',
            'has_sea_view': 'Вид на море',
            'has_city_view': 'Вид на город',
            'has_garden_view': 'Вид на сад'
        }

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['text', 'status']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 4}),
        }
        labels = {
            'text': 'Текст жалобы',
            'status': 'Статус'
        }