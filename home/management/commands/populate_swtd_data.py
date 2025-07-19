# management/commands/populate_swtd_data.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from datetime import date, time, datetime
import json
from home.models import (
    District, FerryStation, StationMaster, FerryType, Ferry, 
    Route, RoutePrice, FerrySchedule, Booking, VehicleBooking, Feedback
)

class Command(BaseCommand):
    help = 'Populate SWTD Kerala database with sample data'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting SWTD Kerala data population...'))
        
        # Clear existing data (optional - uncomment if needed)
        # self.clear_existing_data()
        
        # Create data in order
        self.create_districts()
        self.create_ferry_types()
        self.create_ferry_stations()
        self.create_station_masters()
        self.create_ferries()
        self.create_routes()
        self.create_route_prices()
        self.create_ferry_schedules()
        self.create_sample_bookings()
        self.create_sample_feedback()
        
        self.stdout.write(self.style.SUCCESS('Successfully populated SWTD Kerala database!'))

    def clear_existing_data(self):
        """Clear existing data (use with caution)"""
        self.stdout.write('Clearing existing data...')
        Feedback.objects.all().delete()
        VehicleBooking.objects.all().delete()
        Booking.objects.all().delete()
        FerrySchedule.objects.all().delete()
        RoutePrice.objects.all().delete()
        Route.objects.all().delete()
        Ferry.objects.all().delete()
        StationMaster.objects.all().delete()
        FerryStation.objects.all().delete()
        FerryType.objects.all().delete()
        District.objects.all().delete()

    def create_districts(self):
        """Create the 3 districts"""
        self.stdout.write('Creating districts...')
        districts_data = [
            {'code': 'EKM', 'name': 'Ernakulam'},
            {'code': 'ALPY', 'name': 'Alappuzha'},
            {'code': 'KLM', 'name': 'Kollam'}
        ]
        
        for district_data in districts_data:
            district, created = District.objects.get_or_create(
                code=district_data['code'],
                defaults={'name': district_data['name']}
            )
            if created:
                self.stdout.write(f'  Created district: {district}')

    def create_ferry_types(self):
        """Create ferry types"""
        self.stdout.write('Creating ferry types...')
        ferry_types_data = [
            {
                'name': 'PASSENGER',
                'display_name': 'Passenger Ferry',
                'description': 'Standard passenger transport service with basic seating',
                'base_price_multiplier': 1.0,
                'features': json.dumps({"amenities": ["Basic seating", "Life jackets", "Basic restroom"], "capacity_range": "50-150"})
            },
            {
                'name': 'RORO',
                'display_name': 'RoRo Ferry',
                'description': 'Roll-on/Roll-off vehicle transport ferry',
                'base_price_multiplier': 3.5,
                'features': json.dumps({"amenities": ["Vehicle deck", "Passenger seating", "Loading ramp"], "vehicle_types": ["Cars", "Bikes", "Small trucks"]})
            },
            {
                'name': 'VEGA',
                'display_name': 'Vega Boat',
                'description': 'High-speed premium ferry service',
                'base_price_multiplier': 2.2,
                'features': json.dumps({"amenities": ["AC cabin", "Premium seating", "Fast service", "Refreshments"], "speed": "High-speed"})
            }
        ]
        
        for ferry_type_data in ferry_types_data:
            ferry_type, created = FerryType.objects.get_or_create(
                name=ferry_type_data['name'],
                defaults=ferry_type_data
            )
            if created:
                self.stdout.write(f'  Created ferry type: {ferry_type}')

    def create_ferry_stations(self):
        """Create ferry stations for all districts"""
        self.stdout.write('Creating ferry stations...')
        
        stations_data = [
            # Ernakulam District
            {'name': 'Kochi Main Jetty', 'code': 'KC01', 'district_code': 'EKM'},
            {'name': 'Fort Kochi Ferry Terminal', 'code': 'FK01', 'district_code': 'EKM'},
            {'name': 'Mattancherry Jetty', 'code': 'MT01', 'district_code': 'EKM'},
            {'name': 'Vypin Island Terminal', 'code': 'VP01', 'district_code': 'EKM'},
            {'name': 'Bolgatty Island', 'code': 'BG01', 'district_code': 'EKM'},
            {'name': 'Willingdon Island', 'code': 'WI01', 'district_code': 'EKM'},
            {'name': 'Cherai Beach Jetty', 'code': 'CB01', 'district_code': 'EKM'},
            {'name': 'Kumbakonam Terminal', 'code': 'KM01', 'district_code': 'EKM'},
            
            # Alappuzha District
            {'name': 'Alappuzha Main Terminal', 'code': 'AL01', 'district_code': 'ALPY'},
            {'name': 'Kumarakom Jetty', 'code': 'KR01', 'district_code': 'ALPY'},
            {'name': 'Kuttanad Ferry Point', 'code': 'KT01', 'district_code': 'ALPY'},
            {'name': 'Marari Beach Terminal', 'code': 'MB01', 'district_code': 'ALPY'},
            {'name': 'Pathiramanal Island', 'code': 'PI01', 'district_code': 'ALPY'},
            {'name': 'Champakulam Jetty', 'code': 'CP01', 'district_code': 'ALPY'},
            {'name': 'Edathua Ferry Terminal', 'code': 'ED01', 'district_code': 'ALPY'},
            {'name': 'Mankombu Ghat', 'code': 'MG01', 'district_code': 'ALPY'},
            
            # Kollam District
            {'name': 'Kollam Boat Jetty', 'code': 'KL01', 'district_code': 'KLM'},
            {'name': 'Ashtamudi Lake Terminal', 'code': 'AS01', 'district_code': 'KLM'},
            {'name': 'Munroe Island Jetty', 'code': 'MI01', 'district_code': 'KLM'},
            {'name': 'Thenmala Ferry Point', 'code': 'TM01', 'district_code': 'KLM'},
            {'name': 'Karunagappally Jetty', 'code': 'KG01', 'district_code': 'KLM'},
            {'name': 'Neendakara Harbor', 'code': 'NK01', 'district_code': 'KLM'},
            {'name': 'Chavara Boat Terminal', 'code': 'CV01', 'district_code': 'KLM'},
            {'name': 'Paravur Lake Jetty', 'code': 'PV01', 'district_code': 'KLM'}
        ]
        
        for station_data in stations_data:
            district = District.objects.get(code=station_data['district_code'])
            station, created = FerryStation.objects.get_or_create(
                code=station_data['code'],
                defaults={
                    'name': station_data['name'],
                    'district': district,
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(f'  Created station: {station}')

    def create_station_masters(self):
        """Create station master users and profiles"""
        self.stdout.write('Creating station masters...')
        
        station_masters_data = [
            {'username': 'sm_kochi', 'first_name': 'Ravi', 'last_name': 'Kumar', 'employee_id': 'SM-EKM-001', 'station_code': 'KC01', 'phone': '+91-9876543210'},
            {'username': 'sm_fortkochi', 'first_name': 'Priya', 'last_name': 'Nair', 'employee_id': 'SM-EKM-002', 'station_code': 'FK01', 'phone': '+91-9876543211'},
            {'username': 'sm_alappuzha', 'first_name': 'Suresh', 'last_name': 'Menon', 'employee_id': 'SM-ALPY-001', 'station_code': 'AL01', 'phone': '+91-9876543212'},
            {'username': 'sm_kumarakom', 'first_name': 'Maya', 'last_name': 'Thomas', 'employee_id': 'SM-ALPY-002', 'station_code': 'KR01', 'phone': '+91-9876543213'},
            {'username': 'sm_kollam', 'first_name': 'Anil', 'last_name': 'Varma', 'employee_id': 'SM-KLM-001', 'station_code': 'KL01', 'phone': '+91-9876543214'},
            {'username': 'sm_ashtamudi', 'first_name': 'Lakshmi', 'last_name': 'Pillai', 'employee_id': 'SM-KLM-002', 'station_code': 'AS01', 'phone': '+91-9876543215'}
        ]
        
        for sm_data in station_masters_data:
            # Create user
            user, created = User.objects.get_or_create(
                username=sm_data['username'],
                defaults={
                    'first_name': sm_data['first_name'],
                    'last_name': sm_data['last_name'],
                    'email': f"{sm_data['username']}@swtdkerala.gov.in",
                    'is_staff': True
                }
            )
            if created:
                user.set_password('swtd2025')
                user.save()
            
            # Create station master profile
            station = FerryStation.objects.get(code=sm_data['station_code'])
            sm, created = StationMaster.objects.get_or_create(
                user=user,
                defaults={
                    'employee_id': sm_data['employee_id'],
                    'assigned_station': station,
                    'phone_number': sm_data['phone'],
                    'is_on_duty': True
                }
            )
            if created:
                self.stdout.write(f'  Created station master: {sm}')

    def create_ferries(self):
        """Create ferry fleet"""
        self.stdout.write('Creating ferries...')
        
        ferries_data = [
            # Passenger Ferries
            {'name': 'Kerala Pride', 'registration_number': 'KL-07-2023', 'ferry_type': 'PASSENGER', 'capacity': 120, 'current_location': 'KC01'},
            {'name': 'Backwater Queen', 'registration_number': 'KL-09-2023', 'ferry_type': 'PASSENGER', 'capacity': 90, 'current_location': 'AL01'},
            {'name': 'Coconut Express', 'registration_number': 'KL-11-2023', 'ferry_type': 'PASSENGER', 'capacity': 110, 'current_location': 'KL01'},
            {'name': 'Marine Star', 'registration_number': 'KL-14-2023', 'ferry_type': 'PASSENGER', 'capacity': 85, 'current_location': 'FK01'},
            {'name': 'River Cruise', 'registration_number': 'KL-18-2023', 'ferry_type': 'PASSENGER', 'capacity': 75, 'current_location': 'KR01'},
            
            # RoRo Ferries
            {'name': 'Vehicle Transporter 1', 'registration_number': 'KL-RR-01', 'ferry_type': 'RORO', 'capacity': 60, 'vehicle_capacity': 15, 'current_location': 'VP01'},
            {'name': 'Auto Carrier', 'registration_number': 'KL-RR-02', 'ferry_type': 'RORO', 'capacity': 80, 'vehicle_capacity': 20, 'current_location': 'AS01'},
            {'name': 'Island Connect', 'registration_number': 'KL-RR-03', 'ferry_type': 'RORO', 'capacity': 45, 'vehicle_capacity': 12, 'current_location': 'MI01'},
            
            # Vega Boats
            {'name': 'Speed Wave', 'registration_number': 'KL-VG-01', 'ferry_type': 'VEGA', 'capacity': 50, 'current_location': 'KC01'},
            {'name': 'Swift Current', 'registration_number': 'KL-VG-02', 'ferry_type': 'VEGA', 'capacity': 45, 'current_location': 'AL01'},
            {'name': 'Rapid Stream', 'registration_number': 'KL-VG-03', 'ferry_type': 'VEGA', 'capacity': 55, 'current_location': 'KL01'}
        ]
        
        for ferry_data in ferries_data:
            ferry_type = FerryType.objects.get(name=ferry_data['ferry_type'])
            current_location = FerryStation.objects.get(code=ferry_data['current_location'])
            
            ferry, created = Ferry.objects.get_or_create(
                registration_number=ferry_data['registration_number'],
                defaults={
                    'name': ferry_data['name'],
                    'ferry_type': ferry_type,
                    'capacity': ferry_data['capacity'],
                    'vehicle_capacity': ferry_data.get('vehicle_capacity'),
                    'current_location': current_location,
                    'status': 'ACTIVE'
                }
            )
            if created:
                self.stdout.write(f'  Created ferry: {ferry}')

    def create_routes(self):
        """Create ferry routes"""
        self.stdout.write('Creating routes...')
        
        routes_data = [
            # Ernakulam Routes
            {'name': 'Kochi - Fort Kochi', 'code': 'EKM-FK-01', 'origin': 'KC01', 'destination': 'FK01', 'distance_km': 2.5, 'base_fare': 25.00},
            {'name': 'Kochi - Vypin Island', 'code': 'EKM-VP-01', 'origin': 'KC01', 'destination': 'VP01', 'distance_km': 3.2, 'base_fare': 30.00},
            {'name': 'Fort Kochi - Mattancherry', 'code': 'EKM-MT-01', 'origin': 'FK01', 'destination': 'MT01', 'distance_km': 1.8, 'base_fare': 20.00},
            {'name': 'Kochi - Bolgatty Island', 'code': 'EKM-BG-01', 'origin': 'KC01', 'destination': 'BG01', 'distance_km': 1.5, 'base_fare': 35.00},
            {'name': 'Vypin - Cherai Beach', 'code': 'EKM-CB-01', 'origin': 'VP01', 'destination': 'CB01', 'distance_km': 8.5, 'base_fare': 45.00},
            
            # Alappuzha Routes
            {'name': 'Alappuzha - Kumarakom', 'code': 'ALPY-KR-01', 'origin': 'AL01', 'destination': 'KR01', 'distance_km': 16.0, 'base_fare': 65.00},
            {'name': 'Alappuzha - Kuttanad', 'code': 'ALPY-KT-01', 'origin': 'AL01', 'destination': 'KT01', 'distance_km': 12.5, 'base_fare': 55.00},
            {'name': 'Kumarakom - Pathiramanal', 'code': 'ALPY-PI-01', 'origin': 'KR01', 'destination': 'PI01', 'distance_km': 8.0, 'base_fare': 40.00},
            {'name': 'Alappuzha - Champakulam', 'code': 'ALPY-CP-01', 'origin': 'AL01', 'destination': 'CP01', 'distance_km': 18.5, 'base_fare': 70.00},
            {'name': 'Marari - Mankombu', 'code': 'ALPY-MG-01', 'origin': 'MB01', 'destination': 'MG01', 'distance_km': 14.2, 'base_fare': 60.00},
            
            # Kollam Routes
            {'name': 'Kollam - Ashtamudi Lake', 'code': 'KLM-AS-01', 'origin': 'KL01', 'destination': 'AS01', 'distance_km': 8.5, 'base_fare': 40.00},
            {'name': 'Kollam - Munroe Island', 'code': 'KLM-MI-01', 'origin': 'KL01', 'destination': 'MI01', 'distance_km': 12.0, 'base_fare': 50.00},
            {'name': 'Ashtamudi - Thenmala', 'code': 'KLM-TM-01', 'origin': 'AS01', 'destination': 'TM01', 'distance_km': 22.0, 'base_fare': 85.00},
            {'name': 'Kollam - Karunagappally', 'code': 'KLM-KG-01', 'origin': 'KL01', 'destination': 'KG01', 'distance_km': 25.5, 'base_fare': 95.00},
            {'name': 'Neendakara - Chavara', 'code': 'KLM-CV-01', 'origin': 'NK01', 'destination': 'CV01', 'distance_km': 6.5, 'base_fare': 35.00}
        ]
        
        for route_data in routes_data:
            origin_station = FerryStation.objects.get(code=route_data['origin'])
            destination_station = FerryStation.objects.get(code=route_data['destination'])
            
            route, created = Route.objects.get_or_create(
                code=route_data['code'],
                defaults={
                    'name': route_data['name'],
                    'origin_station': origin_station,
                    'destination_station': destination_station,
                    'distance_km': route_data['distance_km'],
                    'base_fare': route_data['base_fare'],
                    'is_active': True
                }
            )
            if created:
                # Add supported ferry types
                ferry_types = FerryType.objects.all()
                route.supported_ferry_types.set(ferry_types)
                self.stdout.write(f'  Created route: {route}')

    def create_route_prices(self):
        """Create specific pricing for routes and ferry types"""
        self.stdout.write('Creating route prices...')
        
        route_prices_data = [
            # Ernakulam Route Prices
            {'route_code': 'EKM-FK-01', 'ferry_type': 'PASSENGER', 'price': 25.00},
            {'route_code': 'EKM-FK-01', 'ferry_type': 'RORO', 'price': 180.00},
            {'route_code': 'EKM-FK-01', 'ferry_type': 'VEGA', 'price': 120.00},
            
            {'route_code': 'EKM-VP-01', 'ferry_type': 'PASSENGER', 'price': 30.00},
            {'route_code': 'EKM-VP-01', 'ferry_type': 'RORO', 'price': 200.00},
            {'route_code': 'EKM-VP-01', 'ferry_type': 'VEGA', 'price': 150.00},
            
            {'route_code': 'EKM-BG-01', 'ferry_type': 'PASSENGER', 'price': 35.00},
            {'route_code': 'EKM-BG-01', 'ferry_type': 'VEGA', 'price': 180.00},
            
            # Alappuzha Route Prices
            {'route_code': 'ALPY-KR-01', 'ferry_type': 'PASSENGER', 'price': 65.00},
            {'route_code': 'ALPY-KR-01', 'ferry_type': 'RORO', 'price': 250.00},
            {'route_code': 'ALPY-KR-01', 'ferry_type': 'VEGA', 'price': 200.00},
            
            {'route_code': 'ALPY-KT-01', 'ferry_type': 'PASSENGER', 'price': 55.00},
            {'route_code': 'ALPY-KT-01', 'ferry_type': 'VEGA', 'price': 180.00},
            
            # Kollam Route Prices
            {'route_code': 'KLM-AS-01', 'ferry_type': 'PASSENGER', 'price': 40.00},
            {'route_code': 'KLM-AS-01', 'ferry_type': 'VEGA', 'price': 180.00},
            
            {'route_code': 'KLM-MI-01', 'ferry_type': 'PASSENGER', 'price': 50.00},
            {'route_code': 'KLM-MI-01', 'ferry_type': 'RORO', 'price': 220.00},
            {'route_code': 'KLM-MI-01', 'ferry_type': 'VEGA', 'price': 200.00}
        ]
        
        for price_data in route_prices_data:
            try:
                route = Route.objects.get(code=price_data['route_code'])
                ferry_type = FerryType.objects.get(name=price_data['ferry_type'])
                
                route_price, created = RoutePrice.objects.get_or_create(
                    route=route,
                    ferry_type=ferry_type,
                    defaults={
                        'price': price_data['price'],
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'  Created price: {route_price}')
            except (Route.DoesNotExist, FerryType.DoesNotExist):
                continue

    def create_ferry_schedules(self):
        """Create ferry schedules"""
        self.stdout.write('Creating ferry schedules...')
        
        schedules_data = [
            # Morning schedules
            {'route_code': 'EKM-FK-01', 'ferry_name': 'Kerala Pride', 'departure_time': '06:30:00', 'arrival_time': '06:50:00'},
            {'route_code': 'EKM-FK-01', 'ferry_name': 'Speed Wave', 'departure_time': '07:15:00', 'arrival_time': '07:30:00'},
            {'route_code': 'EKM-VP-01', 'ferry_name': 'Marine Star', 'departure_time': '08:00:00', 'arrival_time': '08:25:00'},
            {'route_code': 'EKM-VP-01', 'ferry_name': 'Vehicle Transporter 1', 'departure_time': '09:30:00', 'arrival_time': '10:00:00'},
            
            {'route_code': 'ALPY-KR-01', 'ferry_name': 'Backwater Queen', 'departure_time': '07:00:00', 'arrival_time': '08:15:00'},
            {'route_code': 'ALPY-KR-01', 'ferry_name': 'Swift Current', 'departure_time': '09:00:00', 'arrival_time': '09:45:00'},
            {'route_code': 'ALPY-KT-01', 'ferry_name': 'River Cruise', 'departure_time': '08:30:00', 'arrival_time': '09:25:00'},
            
            {'route_code': 'KLM-AS-01', 'ferry_name': 'Coconut Express', 'departure_time': '07:30:00', 'arrival_time': '08:10:00'},
            {'route_code': 'KLM-MI-01', 'ferry_name': 'Auto Carrier', 'departure_time': '08:45:00', 'arrival_time': '09:45:00'},
            {'route_code': 'KLM-MI-01', 'ferry_name': 'Rapid Stream', 'departure_time': '10:00:00', 'arrival_time': '10:40:00'},
            
            # Evening schedules
            {'route_code': 'EKM-FK-01', 'ferry_name': 'Kerala Pride', 'departure_time': '16:30:00', 'arrival_time': '16:50:00'},
            {'route_code': 'EKM-VP-01', 'ferry_name': 'Speed Wave', 'departure_time': '17:15:00', 'arrival_time': '17:30:00'},
            {'route_code': 'ALPY-KR-01', 'ferry_name': 'Swift Current', 'departure_time': '15:30:00', 'arrival_time': '16:15:00'},
            {'route_code': 'KLM-AS-01', 'ferry_name': 'Rapid Stream', 'departure_time': '18:00:00', 'arrival_time': '18:40:00'}
        ]
        
        for schedule_data in schedules_data:
            try:
                route = Route.objects.get(code=schedule_data['route_code'])
                ferry = Ferry.objects.get(name=schedule_data['ferry_name'])
                
                schedule, created = FerrySchedule.objects.get_or_create(
                    route=route,
                    ferry=ferry,
                    departure_time=schedule_data['departure_time'],
                    defaults={
                        'arrival_time': schedule_data['arrival_time'],
                        'operating_days': 'Mon,Tue,Wed,Thu,Fri,Sat,Sun',
                        'is_active': True
                    }
                )
                if created:
                    self.stdout.write(f'  Created schedule: {schedule}')
            except (Route.DoesNotExist, Ferry.DoesNotExist):
                continue

    def create_sample_bookings(self):
        """Create sample bookings"""
        self.stdout.write('Creating sample bookings...')
        
        bookings_data = [
            {
                'passenger_name': 'Arjun Nair',
                'passenger_phone': '+91-8765432109',
                'passenger_email': 'arjun.nair@email.com',
                'route_code': 'EKM-FK-01',
                'ferry_type': 'PASSENGER',
                'booking_date': '2025-07-20',
                'passenger_count': 2,
                'total_fare': 50.00
            },
            {
                'passenger_name': 'Deepa Krishnan',
                'passenger_phone': '+91-8765432108',
                'passenger_email': 'deepa.k@email.com',
                'route_code': 'ALPY-KR-01',
                'ferry_type': 'VEGA',
                'booking_date': '2025-07-21',
                'passenger_count': 1,
                'total_fare': 200.00
            },
            {
                'passenger_name': 'Rajesh Kumar',
                'passenger_phone': '+91-8765432107',
                'passenger_email': 'rajesh.kumar@email.com',
                'route_code': 'EKM-VP-01',
                'ferry_type': 'RORO',
                'booking_date': '2025-07-22',
                'passenger_count': 3,
                'vehicle_type': 'CAR',
                'vehicle_registration': 'KL-07-AB-1234',
                'total_fare': 200.00
            }
        ]
        
        for booking_data in bookings_data:
            try:
                route = Route.objects.get(code=booking_data['route_code'])
                ferry_type = FerryType.objects.get(name=booking_data['ferry_type'])
                schedule = FerrySchedule.objects.filter(route=route, ferry__ferry_type=ferry_type).first()
                
                if schedule:
                    booking, created = Booking.objects.get_or_create(
                        passenger_phone=booking_data['passenger_phone'],
                        booking_date=booking_data['booking_date'],
                        defaults={
                            'passenger_name': booking_data['passenger_name'],
                            'passenger_email': booking_data.get('passenger_email', ''),
                            'schedule': schedule,
                            'ferry_type': ferry_type,
                            'passenger_count': booking_data['passenger_count'],
                            'base_fare': booking_data['total_fare'] / booking_data['passenger_count'],
                            'total_fare': booking_data['total_fare'],
                            'vehicle_type': booking_data.get('vehicle_type', ''),
                            'vehicle_registration': booking_data.get('vehicle_registration', ''),
                            'booking_status': 'CONFIRMED'
                        }
                    )
                    
                    if created:
                        self.stdout.write(f'  Created booking: {booking}')
                        
                        # Create vehicle booking if RoRo
                        if booking_data['ferry_type'] == 'RORO' and booking_data.get('vehicle_type'):
                            vehicle_booking, v_created = VehicleBooking.objects.get_or_create(
                                booking=booking,
                                defaults={
                                    'vehicle_type': 'CAR',
                                    'vehicle_registration': booking_data['vehicle_registration'],
                                    'driver_name': booking_data['passenger_name'],
                                    'driver_license': 'KL-123456789'
                                }
                            )
                            if v_created:
                                self.stdout.write(f'    Created vehicle booking: {vehicle_booking}')
            except (Route.DoesNotExist, FerryType.DoesNotExist):
                continue

    def create_sample_feedback(self):
        """Create sample feedback"""
        self.stdout.write('Creating sample feedback...')
        
        feedback_data = [
            {
                'passenger_name': 'Anitha Menon',
                'route_code': 'EKM-FK-01',
                'ferry_type': 'PASSENGER',
                'rating': 4,
                'title': 'Good service, clean ferry',
                'description': 'The ferry was clean and the staff was helpful. Journey was comfortable and on time.'
            },
            {
                'passenger_name': 'Vishnu Prasad',
                'route_code': 'ALPY-KR-01',
                'ferry_type': 'VEGA',
                'rating': 5,
                'title': 'Excellent high-speed service',
                'description': 'Amazing experience with the Vega boat. Very fast and comfortable with great amenities.'
            },
            {
                'passenger_name': 'Sarah Jacob',
                'route_code': 'KLM-MI-01',
                'ferry_type': 'PASSENGER',
                'rating': 3,
                'title': 'Average service',
                'description': 'Ferry was okay but could improve cleanliness. Staff was friendly though.'
            }
        ]
        
        for feedback_item in feedback_data:
            try:
                route = Route.objects.get(code=feedback_item['route_code'])
                ferry_type = FerryType.objects.get(name=feedback_item['ferry_type'])
                
                feedback, created = Feedback.objects.get_or_create(
                    passenger_name=feedback_item['passenger_name'],
                    route=route,
                    defaults={
                        'ferry_type': ferry_type,
                        'rating': feedback_item['rating'],
                        'title': feedback_item['title'],
                        'description': feedback_item['description'],
                        'is_resolved': False
                    }
                )
                if created:
                    self.stdout.write(f'  Created feedback: {feedback}')
            except (Route.DoesNotExist, FerryType.DoesNotExist):
                continue
