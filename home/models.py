from django.db import models
from django.contrib.auth.models import User
import uuid


# Create your models here.
class District(models.Model):
    DISTRICT_CHOICES = [
        ('EKM', 'Ernakulam'),
        ('ALPY', 'Alappuzha'),
        ('KLM', 'Kollam'),
    ]
    
    code = models.CharField(max_length=10, choices=DISTRICT_CHOICES, unique=True)
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        ordering = ['name']


class FerryStation(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)  # e.g., 'KC01', 'AL02'
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='stations')
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    class Meta:
        ordering = ['district', 'name']


class StationMaster(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='station_master_profile')
    employee_id = models.CharField(max_length=20, unique=True)
    assigned_station = models.ForeignKey(FerryStation, on_delete=models.CASCADE, related_name='station_masters')
    phone_number = models.CharField(max_length=15)
    is_on_duty = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.assigned_station.name}"


class FerryType(models.Model):
    FERRY_TYPE_CHOICES = [
        ('PASSENGER', 'Passenger Ferry'),
        ('RORO', 'RoRo Ferry'),
        ('VEGA', 'Vega Boat'),
    ]
    
    name = models.CharField(max_length=20, choices=FERRY_TYPE_CHOICES, unique=True)
    display_name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    base_price_multiplier = models.DecimalField(max_digits=4, decimal_places=2, default=1.0)
    features = models.TextField(blank=True)  # JSON field for features like "AC, Premium seats"
    
    def __str__(self):
        return self.display_name


class Ferry(models.Model):
    FERRY_STATUS = [
        ('ACTIVE', 'Active'),
        ('MAINTENANCE', 'Under Maintenance'),
        ('INACTIVE', 'Inactive'),
    ]
    
    name = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=50, unique=True)
    ferry_type = models.ForeignKey(FerryType, on_delete=models.CASCADE, related_name='ferries')
    capacity = models.PositiveIntegerField()
    vehicle_capacity = models.PositiveIntegerField(null=True, blank=True)  # For RoRo ferries
    status = models.CharField(max_length=20, choices=FERRY_STATUS, default='ACTIVE')
    current_location = models.ForeignKey(FerryStation, on_delete=models.SET_NULL, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.ferry_type.display_name})"
    
    class Meta:
        verbose_name_plural = "Ferries"


class Route(models.Model):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)  # e.g., 'EKM-ALPY-01'
    origin_station = models.ForeignKey(FerryStation, on_delete=models.CASCADE, related_name='origin_routes')
    destination_station = models.ForeignKey(FerryStation, on_delete=models.CASCADE, related_name='destination_routes')
    distance_km = models.DecimalField(max_digits=6, decimal_places=2)
    base_fare = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    supported_ferry_types = models.ManyToManyField(FerryType, related_name='available_routes')
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def get_fare_for_ferry_type(self, ferry_type):
        """Calculate fare based on ferry type multiplier"""
        return self.base_fare * ferry_type.base_price_multiplier


class RoutePrice(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='prices')
    ferry_type = models.ForeignKey(FerryType, on_delete=models.CASCADE, related_name='route_prices')
    price = models.DecimalField(max_digits=8, decimal_places=2)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.route.name} - {self.ferry_type.display_name}: ₹{self.price}"
    
    class Meta:
        unique_together = ['route', 'ferry_type']


class FerrySchedule(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='schedules')
    ferry = models.ForeignKey(Ferry, on_delete=models.CASCADE, related_name='schedules')
    departure_time = models.TimeField()
    arrival_time = models.TimeField()
    operating_days = models.CharField(max_length=100, default='Mon,Tue,Wed,Thu,Fri,Sat,Sun')  # JSON array of days
    is_active = models.BooleanField(default=True)
    
    @property
    def ferry_type(self):
        return self.ferry.ferry_type
    
    def __str__(self):
        return f"{self.ferry.name} ({self.ferry_type.display_name}) - {self.route.name} at {self.departure_time}"
    
    class Meta:
        ordering = ['route', 'departure_time']


class Booking(models.Model):
    BOOKING_STATUS = [
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]
    
    PASSENGER_TYPES = [
        ('ADULT', 'Adult'),
        ('CHILD', 'Child'),
        ('SENIOR', 'Senior Citizen'),
    ]
    
    booking_reference = models.CharField(max_length=20, unique=True, blank=True)
    passenger_name = models.CharField(max_length=100)
    passenger_phone = models.CharField(max_length=10)
    passenger_email = models.EmailField(blank=True)
    
    # Ferry and route information
    schedule = models.ForeignKey(FerrySchedule, on_delete=models.CASCADE, related_name='bookings')
    ferry_type = models.ForeignKey(FerryType, on_delete=models.CASCADE)
    
    # Booking details
    booking_date = models.DateField()  # Date of travel
    passenger_count = models.PositiveIntegerField(default=1)
    passenger_type = models.CharField(max_length=20, choices=PASSENGER_TYPES, default='ADULT')
    
    # Vehicle information (for RoRo bookings)
    vehicle_type = models.CharField(max_length=50, blank=True)  # Car, Bike, Truck, etc.
    vehicle_registration = models.CharField(max_length=20, blank=True)
    
    # Pricing
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    total_fare = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Status and metadata
    booking_status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='CONFIRMED')
    special_requirements = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Generate booking reference if not provided
        if not self.booking_reference:
            self.booking_reference = str(uuid.uuid4())[:8].upper()
        
        # Auto-calculate total fare if not provided
        if not self.total_fare:
            try:
                route_price = RoutePrice.objects.get(
                    route=self.schedule.route,
                    ferry_type=self.ferry_type,
                    is_active=True
                )
                self.base_fare = route_price.price
            except RoutePrice.DoesNotExist:
                # Fallback to route base fare with ferry type multiplier
                self.base_fare = self.schedule.route.get_fare_for_ferry_type(self.ferry_type)
            
            self.total_fare = self.base_fare * self.passenger_count
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.booking_reference} - {self.passenger_name} ({self.ferry_type.display_name})"
    
    class Meta:
        ordering = ['-created_at']


class VehicleBooking(models.Model):
    VEHICLE_TYPES = [
        ('CAR', 'Car'),
        ('BIKE', 'Motorcycle'),
        ('TRUCK', 'Truck'),
        ('BUS', 'Bus'),
        ('AUTO', 'Auto Rickshaw'),
    ]
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='vehicle_details')
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES)
    vehicle_registration = models.CharField(max_length=20)
    driver_name = models.CharField(max_length=100)
    driver_license = models.CharField(max_length=30)
    
    def __str__(self):
        return f"{self.booking.booking_reference} - {self.vehicle_type} ({self.vehicle_registration})"


class Feedback(models.Model):
    RATING_CHOICES = [
        (1, 'Very Poor'), (2, 'Poor'), (3, 'Average'), (4, 'Good'), (5, 'Excellent')
    ]
    
    passenger_name = models.CharField(max_length=100, blank=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='feedback')
    ferry_type = models.ForeignKey(FerryType, on_delete=models.CASCADE, related_name='feedback')
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='feedback', null=True, blank=True)
    
    rating = models.PositiveIntegerField(choices=RATING_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    is_resolved = models.BooleanField(default=False)
    admin_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.ferry_type.display_name} - Rating: {self.rating}/5"
    
    class Meta:
        ordering = ['-created_at']
