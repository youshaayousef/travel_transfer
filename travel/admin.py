from django.contrib import admin
# Register your models here.

from .models import *

class StationAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'city__name', 'address']

admin.site.register(Station, StationAdmin)

class SeatAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'number', 'bus__name']
    list_filter = ['bus']

admin.site.register(Seat, SeatAdmin)

class BusAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'number', 'capacity']

admin.site.register(Bus, BusAdmin)

class JourneyAdmin(admin.ModelAdmin):
    date_hierarchy = 'departure_datetime'
    list_display = ["id", 'departure_station', 'arrival_station']

admin.site.register(Journey, JourneyAdmin)

class ScheduleAdmin(admin.ModelAdmin):
    date_hierarchy = 'departure_datetime'
    list_display = ['departure_station', 'arrival_station']
    list_filter = ["category"]
admin.site.register(Schedule, ScheduleAdmin)


class ReservationAdmin(admin.ModelAdmin):
    # date_hierarchy = "created_at"
    list_display = ['id', 'created_at', 'user', 'price']

admin.site.register(Reservation, ReservationAdmin)

class ReservationDetailsAdmin(admin.ModelAdmin):
    # date_hierarchy = "created_at"
    list_display = ['id', 'journey', 'seat', 'reservation']

admin.site.register(ReservationDetails, ReservationDetailsAdmin)