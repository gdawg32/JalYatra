from django.urls import path
from . import api_views

urlpatterns = [
    path('station-master/login/', api_views.station_master_login_api, name='station_master_login_api'),
    path('station-master/logout/', api_views.station_master_logout_api, name='station_master_logout_api'),
    path('station-master/profile/', api_views.station_master_profile_api, name='station_master_profile_api'),
    path('station-master/duty-status/', api_views.update_duty_status_api, name='update_duty_status_api'),
    path('validate-qr/', api_views.validate_qr_simple, name='validate_qr_simple'),
]

