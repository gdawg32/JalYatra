from django.urls import path
from . import views
from . import api_views

urlpatterns = [
    path('', views.home, name='home'),
    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('ticket/', views.ticket, name='ticket'),
    path('book-ticket/<int:route_id>/', views.book_ticket, name='book_ticket'),
    path('process-booking/', views.process_booking, name='process_booking'),
    path('booking-success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('station-master-login/', views.station_master_login, name='station_master_login'),


   
]

