from django.urls import path
from .views import *

urlpatterns = [
    path('api/reports/monthly_pie/', MonthlyPieReportView.as_view()),
    path('api/reports/yearly_bar/', YearlyBarReportView.as_view()),
    path('api/reports/journey_reservation_count/', JourneyReservationCount.as_view()),
    path('api/reports/journeys/<int:id>/', JourneyRetrieve.as_view()),
]
