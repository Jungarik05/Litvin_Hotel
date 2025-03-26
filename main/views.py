from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse, FileResponse
from django.conf import settings
from django.contrib.auth import logout, login, authenticate
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.db.models import Q
from django.utils import timezone
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.units import cm, inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime, timedelta
from .models import Room, Booking, User, Task, Complaint, ComplaintStatus
from .forms import RegistrationForm, RoomFilterForm, BookingForm, RoomForm, ComplaintForm, TaskForm

def home(request):
    """Представление для главной страницы"""
    rooms = Room.objects.all().order_by('room_number')
    return render(request, 'main/home.html', {'rooms': rooms})

@login_required
def rooms(request):
    """Представление для отображения списка номеров"""
    form = RoomFilterForm(request.GET)
    rooms = Room.objects.filter(is_available=True)  # Показываем только доступные номера
    
    if form.is_valid():
        room_type = form.cleaned_data.get('room_type')
        min_price = form.cleaned_data.get('min_price')
        max_price = form.cleaned_data.get('max_price')
        search_query = form.cleaned_data.get('search')
        
        if room_type:
            rooms = rooms.filter(room_type=room_type)
        if min_price:
            rooms = rooms.filter(price__gte=min_price)
        if max_price:
            rooms = rooms.filter(price__lte=max_price)
        if search_query:
            # Создаем список русских названий типов номеров
            room_types = dict(Room.ROOM_TYPES)
            # Фильтруем номера, где русское название типа номера содержит поисковый запрос
            rooms = rooms.filter(room_type__in=[
                room_type for room_type, display_name in room_types.items()
                if search_query.lower() in display_name.lower()
            ])
    
    return render(request, 'main/rooms.html', {
        'rooms': rooms,
        'form': form
    })

def room_image(request, room_id):
    """Представление для отображения изображения номера"""
    room = get_object_or_404(Room, id=room_id)
    if room.image:
        return HttpResponse(room.image.url)
    return HttpResponse(status=404)

def register(request):
    """Представление для регистрации новых пользователей"""
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация успешно завершена!')
            return redirect('profile')
    else:
        form = RegistrationForm()
    return render(request, 'main/register.html', {'form': form})

@login_required
def book_room(request, room_id):
    """Представление для бронирования номера"""
    room = get_object_or_404(Room, id=room_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data.get('check_in')
            check_out = form.cleaned_data.get('check_out')

            overlapping_bookings = Booking.objects.filter(
                room=room,
                check_out__gt=check_in,  # Существующее бронирование заканчивается после начала нового
                check_in__lt=check_out   # Существующее бронирование начинается до конца нового
            ).exists()

            if overlapping_bookings:
                messages.error(request, "Этот номер уже забронирован на выбранные даты!")
            else:
                Booking.objects.create(
                    user=request.user,
                    room=room,
                    check_in=check_in,
                    check_out=check_out
                )        
                room.is_available = False
                room.save()    
                messages.success(request, f'Номер {room.room_number} успешно забронирован!')
                return redirect('home')
    else:
        form = BookingForm()

    return render(request, 'main/book_room.html', {'room': room, 'form': form})

def room_list(request):
    
    rooms = Room.objects.filter(is_available=True)  # Только доступные номера
    form = RoomFilterForm(request.GET or None)

    query = request.GET.get('q', '').strip()  # Получаем строку поиска
    
    if query:
        # Создаем список русских названий типов номеров
        room_types = dict(Room.ROOM_TYPES)
        # Фильтруем номера, где русское название типа номера содержит поисковый запрос
        rooms = rooms.filter(room_type__in=[
            room_type for room_type, display_name in room_types.items()
            if query.lower() in display_name.lower()
        ])

    if form.is_valid():
        # Фильтрация по типу номера
        check_in = form.cleaned_data.get('check_in')
        check_out = form.cleaned_data.get('check_out')

        if check_in and check_out:
            # Исключаем номера, которые уже заняты в эти даты
            rooms = rooms.exclude(
                bookings__check_in__lt=check_out,
                bookings__check_out__gt=check_in
            )
        

        # Фильтрация по цене
        if form.cleaned_data['min_price']:
            rooms = rooms.filter(price__gte=form.cleaned_data['min_price'])
        if form.cleaned_data['max_price']:
            rooms = rooms.filter(price__lte=form.cleaned_data['max_price'])

        # Фильтрация по удобствам
        if form.cleaned_data['has_wifi']:
            rooms = rooms.filter(has_wifi=True)
        if form.cleaned_data['has_tv']:
            rooms = rooms.filter(has_tv=True)
        if form.cleaned_data['has_balcony']:
            rooms = rooms.filter(has_balcony=True)
        if form.cleaned_data['has_jacuzzi']:
            rooms = rooms.filter(has_jacuzzi=True)
        if form.cleaned_data['has_kitchen']:
            rooms = rooms.filter(has_kitchen=True)
        if form.cleaned_data['has_office']:
            rooms = rooms.filter(has_office=True)       
        if form.cleaned_data['has_pool']:
            rooms = rooms.filter(has_pool=True)
        if form.cleaned_data['has_terrace']:
            rooms = rooms.filter(has_terrace=True)
        if form.cleaned_data['has_sea_view']:
            rooms = rooms.filter(has_sea_view=True)
        if form.cleaned_data['has_city_view']:
            rooms = rooms.filter(has_city_view=True)
        if form.cleaned_data['has_garden_view']:
            rooms = rooms.filter(has_garden_view=True)
        if form.cleaned_data['has_minibar']:
            rooms = rooms.filter(has_minibar=True)
        if form.cleaned_data['has_safe']:
            rooms = rooms.filter(has_safe=True)
        if form.cleaned_data['has_air_conditioning']:
            rooms = rooms.filter(has_air_conditioning=True)
            

    context = {
        'rooms': rooms,
        'form': form,
        'query': query
    }
    return render(request, 'main/rooms.html', context)

def update_room_availability():
    """Освобождает номера, если дата выезда прошла"""
    expired_bookings = Booking.objects.filter(check_out__lt=timezone.now().date())

    for booking in expired_bookings:
        room = booking.room
        room.is_available = True
        room.save()

    expired_bookings.delete()  # Удаляем старые брони

def logout_view(request):
    """Представление для выхода из аккаунта"""
    if request.method == 'POST':
        # Проверяем, не является ли текущий URL админкой
        if not request.path.startswith('/admin/'):
            # Сохраняем текущую сессию админки
            admin_session = request.session.get('admin_session')
            # Выходим из аккаунта
            logout(request)
            # Восстанавливаем сессию админки
            if admin_session:
                request.session['admin_session'] = admin_session
            messages.success(request, 'Вы успешно вышли из аккаунта.')
    return redirect('home')

@login_required
def profile_view(request):
    if request.method == 'POST' and 'photo' in request.FILES:
        user = request.user
        user.photo = request.FILES['photo']
        user.save()
        messages.success(request, 'Фото профиля успешно обновлено')
        return redirect('profile')
    
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/profile.html', {'bookings': bookings})

@login_required
def booking_detail(request, booking_id):
    """Представление для отображения детальной информации о бронировании"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    return render(request, 'main/booking_detail.html', {'booking': booking})

@login_required
def create_complaint(request, booking_id):
    """Представление для создания жалобы"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        complaint_text = request.POST.get('complaint_text')
        if complaint_text:
            Complaint.objects.create(
                booking=booking,
                text=complaint_text,
                status=ComplaintStatus.objects.get(name='Новая')
            )
            messages.success(request, 'Жалоба успешно отправлена')
            return redirect('booking_detail', booking_id=booking.id)
        else:
            messages.error(request, 'Пожалуйста, введите текст жалобы')
    
    return render(request, 'main/create_complaint.html', {'booking': booking})

@login_required
def download_booking_pdf(request, booking_id):
    """Генерация PDF с информацией о бронировании"""
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Создаем буфер для PDF
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    
    # Регистрируем шрифт Times New Roman
    pdfmetrics.registerFont(TTFont('TimesNewRoman', 'TIMES.TTF'))
    pdfmetrics.registerFont(TTFont('TimesNewRoman-Bold', 'TIMESBD.TTF'))
    
    # Добавляем заголовок
    p.setFont("TimesNewRoman-Bold", 16)
    p.drawString(50, 800, "Подтверждение бронирования")
    
    # Информация о бронировании
    p.setFont("TimesNewRoman", 12)
    p.drawString(50, 750, f"Номер бронирования: {booking.id}")
    p.drawString(50, 730, f"Дата создания: {booking.created_at.strftime('%d.%m.%Y %H:%M')}")
    p.drawString(50, 710, f"Дата заезда: {booking.check_in.strftime('%d.%m.%Y')}")
    p.drawString(50, 690, f"Дата выезда: {booking.check_out.strftime('%d.%m.%Y')}")
    
    # Информация о номере
    p.drawString(50, 650, f"Номер комнаты: {booking.room.room_number}")
    p.drawString(50, 630, f"Тип номера: {booking.room.get_room_type_display()}")
    p.drawString(50, 610, f"Цена за ночь: {booking.room.price} ₽")
    
    # Расчет общей стоимости
    nights = (booking.check_out - booking.check_in).days
    total_price = booking.room.price * nights
    p.drawString(50, 570, f"Количество ночей: {nights}")
    p.setFont("TimesNewRoman-Bold", 12)
    p.drawString(50, 550, f"Итоговая стоимость: {total_price} ₽")
    
    # Рекомендации для гостей
    p.setFont("TimesNewRoman", 12)
    p.drawString(50, 500, "Рекомендации для гостей:")
    recommendations = [
        "1. Заезд возможен после 14:00",
        "2. Выезд до 12:00",
        "3. При заезде необходимо предъявить паспорт",
        "4. Бесплатная парковка доступна на территории отеля",
        "5. Wi-Fi доступен во всех номерах",
        "6. Завтрак включен в стоимость проживания (7:00-10:00)",
        "7. В случае опоздания, пожалуйста, сообщите администратору",
        "8. Курение запрещено во всех помещениях отеля",
        "9. Домашние животные не допускаются",
        "10. При необходимости дополнительных услуг обратитесь на ресепшн"
    ]
    
    y = 480
    for rec in recommendations:
        p.drawString(50, y, rec)
        y -= 20
    
    # Добавляем контактную информацию
    p.setFont("TimesNewRoman-Bold", 12)
    p.drawString(50, 200, "Контактная информация:")
    p.setFont("TimesNewRoman", 12)
    p.drawString(50, 180, "Адрес: ул. Примерная, 123")
    p.drawString(50, 160, "Телефон: +7 (900) 123-45-67")
    p.drawString(50, 140, "Email: info@hotel.com")
    
    # Сохраняем PDF
    p.showPage()
    p.save()
    
    # Перемещаем указатель в начало буфера
    buffer.seek(0)
    
    # Создаем ответ с PDF файлом
    response = FileResponse(buffer, as_attachment=True, filename=f'booking_{booking.id}.pdf')
    return response

@login_required
@user_passes_test(lambda u: u.role and u.role.name == 'Менеджер')
def task_list(request):
    tasks = Task.objects.select_related('created_by', 'assigned_to').all().order_by('-created_at')
    workers = User.objects.filter(role__name='Сотрудник')
    return render(request, 'main/task_list.html', {
        'tasks': tasks,
        'workers': workers
    })

@login_required
@user_passes_test(lambda u: u.role and u.role.name == 'Менеджер')
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'Задача успешно создана!')
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'main/task_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.role and u.role.name == 'Менеджер')
def task_edit(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, 'Задача успешно обновлена!')
            return redirect('task_list')
    else:
        form = TaskForm(instance=task)
    return render(request, 'main/task_form.html', {'form': form, 'task': task})

@login_required
@user_passes_test(lambda u: u.role and u.role.name == 'Менеджер')
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        task.delete()
        messages.success(request, 'Задача успешно удалена!')
        return redirect('task_list')
    return render(request, 'main/task_confirm_delete.html', {'task': task})

@login_required
@user_passes_test(lambda u: u.role and u.role.name == 'Менеджер')
def room_create(request):
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Номер успешно создан!')
            return redirect('room_list')
    else:
        form = RoomForm()
    return render(request, 'main/room_form.html', {'form': form})

@login_required
@user_passes_test(lambda u: u.role and u.role.name == 'Менеджер')
def room_edit(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        form = RoomForm(request.POST, request.FILES, instance=room)
        if form.is_valid():
            form.save()
            messages.success(request, 'Номер успешно обновлен!')
            return redirect('room_list')
    else:
        form = RoomForm(instance=room)
    return render(request, 'main/room_form.html', {'form': form, 'room': room})

@login_required
@user_passes_test(lambda u: u.role and u.role.name == 'Менеджер')
def room_delete(request, pk):
    room = get_object_or_404(Room, pk=pk)
    if request.method == 'POST':
        room.delete()
        messages.success(request, 'Номер успешно удален!')
        return redirect('room_list')
    return render(request, 'main/room_confirm_delete.html', {'room': room})

@login_required
def room_detail(request, pk):
    room = get_object_or_404(Room, pk=pk)
    return render(request, 'main/room_detail.html', {'room': room})

@login_required
def complaint_list(request):
    if request.user.role and request.user.role.name == 'Менеджер':
        complaints = Complaint.objects.all().order_by('-date')
    else:
        complaints = Complaint.objects.filter(booking__user=request.user).order_by('-date')
    return render(request, 'main/complaint_list.html', {'complaints': complaints})

@login_required
def complaint_detail(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if not (request.user.role and request.user.role.name == 'Менеджер') and complaint.booking.user != request.user:
        messages.error(request, 'У вас нет доступа к этой жалобе')
        return redirect('complaint_list')
    return render(request, 'main/complaint_detail.html', {'complaint': complaint})

@login_required
@user_passes_test(lambda u: u.role and u.role.name == 'Менеджер')
def complaint_edit(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        form = ComplaintForm(request.POST, instance=complaint)
        if form.is_valid():
            form.save()
            messages.success(request, 'Жалоба успешно обновлена!')
            return redirect('complaint_list')
    else:
        form = ComplaintForm(instance=complaint)
    return render(request, 'main/complaint_form.html', {'form': form, 'complaint': complaint})

@login_required
@user_passes_test(lambda u: u.role and u.role.name == 'Менеджер')
def complaint_delete(request, pk):
    complaint = get_object_or_404(Complaint, pk=pk)
    if request.method == 'POST':
        complaint.delete()
        messages.success(request, 'Жалоба успешно удалена!')
        return redirect('complaint_list')
    return render(request, 'main/complaint_confirm_delete.html', {'complaint': complaint})

@login_required
def booking_list(request):
    """Представление для отображения списка бронирований"""
    if request.user.role and request.user.role.name == 'Менеджер':
        bookings = Booking.objects.all().order_by('-created_at')
    else:
        bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/booking_list.html', {'bookings': bookings})

@login_required
def booking_create(request, pk=None):
    """Представление для создания нового бронирования"""
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data.get('check_in')
            check_out = form.cleaned_data.get('check_out')
            room_id = request.POST.get('room') or pk

            room = get_object_or_404(Room, id=room_id)
            
            # Проверяем, не занят ли номер на эти даты
            overlapping_bookings = Booking.objects.filter(
                room=room,
                check_out__gt=check_in,
                check_in__lt=check_out
            ).exists()

            if overlapping_bookings:
                messages.error(request, "Этот номер уже забронирован на выбранные даты!")
            else:
                booking = Booking.objects.create(
                    user=request.user,
                    room=room,
                    check_in=check_in,
                    check_out=check_out
                )
                room.is_available = False
                room.save()
                messages.success(request, f'Номер {room.room_number} успешно забронирован!')
                
                # Сохраняем сессию пользователя
                request.session.save()
                
                # Проверяем, что пользователь все еще авторизован
                if not request.user.is_authenticated:
                    from django.contrib.auth import login
                    login(request, request.user)
                
                return redirect('booking_detail', pk=booking.pk)
    else:
        initial = {}
        if pk:
            room = get_object_or_404(Room, id=pk)
            initial['room'] = room
        form = BookingForm(initial=initial)
    return render(request, 'main/booking_form.html', {'form': form})

@login_required
def booking_edit(request, pk):
    """Представление для редактирования бронирования"""
    booking = get_object_or_404(Booking, pk=pk)
    if not (request.user.role and request.user.role.name == 'Менеджер') and booking.user != request.user:
        messages.error(request, 'У вас нет доступа к этому бронированию')
        return redirect('booking_list')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            check_in = form.cleaned_data.get('check_in')
            check_out = form.cleaned_data.get('check_out')

            # Проверяем, не занят ли номер на новые даты
            overlapping_bookings = Booking.objects.filter(
                room=booking.room,
                check_out__gt=check_in,
                check_in__lt=check_out
            ).exclude(pk=booking.pk).exists()

            if overlapping_bookings:
                messages.error(request, "Этот номер уже забронирован на выбранные даты!")
            else:
                booking.check_in = check_in
                booking.check_out = check_out
                booking.save()
                messages.success(request, 'Бронирование успешно обновлено!')
                return redirect('booking_detail', pk=booking.pk)
    else:
        form = BookingForm(initial={
            'check_in': booking.check_in,
            'check_out': booking.check_out
        })
    return render(request, 'main/booking_form.html', {'form': form, 'booking': booking})

@login_required
def booking_delete(request, pk):
    """Представление для удаления бронирования"""
    booking = get_object_or_404(Booking, pk=pk)
    if not (request.user.role and request.user.role.name == 'Менеджер') and booking.user != request.user:
        messages.error(request, 'У вас нет доступа к этому бронированию')
        return redirect('booking_list')

    if request.method == 'POST':
        room = booking.room
        booking.delete()
        room.is_available = True
        room.save()
        messages.success(request, 'Бронирование успешно удалено!')
        return redirect('booking_list')
    return render(request, 'main/booking_confirm_delete.html', {'booking': booking})

def user_login(request):
    if request.method == 'POST':
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        user = authenticate(request, phone=phone, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Неверный телефон или пароль')
    return render(request, 'main/user_login.html')

def user_logout(request):
    """Представление для выхода из системы"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'Вы успешно вышли из системы!')
        return redirect('home')
    return redirect('home')

@login_required
def task_update_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            if new_status == 'completed':
                task.completed_at = timezone.now()
            task.save()
            messages.success(request, 'Статус задачи успешно обновлен')
        return redirect('task_list')
    return HttpResponseNotAllowed(['POST'])

@login_required
def worker_tasks(request):
    """Представление для просмотра задач сотрудника"""
    if request.user.role and request.user.role.name == 'Сотрудник':
        tasks = Task.objects.filter(assigned_to=request.user).order_by('-created_at')
        return render(request, 'main/worker_tasks.html', {'tasks': tasks})
    return redirect('home')