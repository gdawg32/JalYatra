from django.contrib import admin
from home.models import *

# Register your models here.
admin.site.register(District)
admin.site.register(StationMaster)
admin.site.register(FerryType)
admin.site.register(Ferry)
admin.site.register(FerrySchedule)
admin.site.register(Route)
admin.site.register(FerryStation)
admin.site.register(Booking)
admin.site.register(VehicleBooking)
admin.site.register(Feedback)