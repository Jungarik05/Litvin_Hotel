from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Room, Booking, Task, Role, TaskStatus, ComplaintStatus, Complaint

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'full_name', 'role', 'is_staff', 'is_active')
    list_filter = ('role', 'is_staff', 'is_active')
    search_fields = ('phone', 'full_name')
    ordering = ('phone',)
    
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Персональная информация', {'fields': ('full_name', 'photo', 'role')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'full_name', 'password1', 'password2', 'role'),
        }),
    )

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_type', 'price', 'is_available')
    list_filter = ('room_type', 'is_available')
    search_fields = ('room_number', 'description')
    ordering = ('room_number',)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'room', 'check_in', 'check_out', 'created_at')
    list_filter = ('check_in', 'check_out', 'created_at')
    search_fields = ('user__full_name', 'user__phone', 'room__room_number')
    ordering = ('-created_at',)

@admin.register(TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'assigned_to', 'created_by', 'status', 'due_date')
    list_filter = ('status', 'assigned_to', 'created_by')
    search_fields = ('title', 'description')
    readonly_fields = ('created_at', 'completed_at')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        if request.user.role and request.user.role.name == 'Менеджер':
            return qs.filter(created_by=request.user)
        return qs.filter(assigned_to=request.user)

@admin.register(ComplaintStatus)
class ComplaintStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('booking', 'date', 'status', 'resolved_by', 'resolution_date')
    list_filter = ('status', 'date', 'resolution_date')
    search_fields = ('booking__user__full_name', 'booking__user__phone', 'text')
    ordering = ('-date',)
