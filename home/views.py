from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from home.models import *
import json
from datetime import date
import qrcode
from io import BytesIO
import base64
from django.contrib import messages
from django.contrib import messages
import uuid

# Create your views here.
def home (request):
    return render(request, 'index.html')

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            if user.is_superuser:
                login(request, user)
                return redirect('admin_dashboard')
            else:
                return render(request, 'admin_login.html', {
                    'error': 'You are not authorized to access the admin dashboard.'
                })
        else:
            return render(request, 'admin_login.html', {
                'error': 'Invalid username or password.'
            })

    return render(request, 'admin_login.html')

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

def ticket(request):
    """Main ticket booking page"""
    ferry_types = FerryType.objects.all()
    districts = District.objects.all()
    
    # Build routes data structure for JavaScript
    routes_data = {}
    
    for ferry_type in ferry_types:
        ferry_type_key = ferry_type.name.lower()
        routes_data[ferry_type_key] = {}
        
        for district in districts:
            district_key = district.code.lower()
            
            # Get routes that start from this district and support this ferry type
            routes = Route.objects.filter(
                supported_ferry_types=ferry_type,
                origin_station__district=district,
                is_active=True
            ).select_related('origin_station', 'destination_station')
            
            # Get pricing information
            route_prices = RoutePrice.objects.filter(
                route__in=routes,
                ferry_type=ferry_type,
                is_active=True
            )
            price_map = {rp.route.id: rp.price for rp in route_prices}
            
            # Get schedule information for departure times
            schedules = FerrySchedule.objects.filter(
                route__in=routes,
                ferry__ferry_type=ferry_type,
                is_active=True
            ).select_related('ferry').order_by('departure_time')
            
            schedule_map = {}
            for schedule in schedules:
                if schedule.route.id not in schedule_map:
                    schedule_map[schedule.route.id] = []
                schedule_map[schedule.route.id].append({
                    'time': schedule.departure_time.strftime('%I:%M %p'),
                    'ferry_name': schedule.ferry.name
                })
            
            # Build route list for this ferry type and district
            route_list = []
            for route in routes:
                # Get price (from RoutePrice or fallback to base fare)
                price = price_map.get(route.id, route.base_fare)
                
                # Get next departure time
                next_schedule = schedule_map.get(route.id, [])
                departure_time = next_schedule[0]['time'] if next_schedule else 'Check Schedule'
                
                # Calculate estimated duration (you can enhance this with actual data)
                duration_minutes = int(route.distance_km * 4)  # Rough estimate: 4 min per km
                if duration_minutes < 60:
                    duration = f"{duration_minutes} min"
                else:
                    hours = duration_minutes // 60
                    minutes = duration_minutes % 60
                    duration = f"{hours}h {minutes}m" if minutes else f"{hours}h"
                
                route_data = {
                    'id': route.id,
                    'from': route.origin_station.name,
                    'to': route.destination_station.name,
                    'time': departure_time,
                    'price': f"₹{price:.0f}",
                    'duration': duration,
                    'ferry': ferry_type.display_name,
                    'distance': f"{route.distance_km} km"
                }
                
                # Add ferry type specific info
                if ferry_type.name == 'RORO':
                    # Get vehicle capacity from ferry
                    ferry = schedules.filter(route=route).first()
                    if ferry and ferry.ferry.vehicle_capacity:
                        route_data['capacity'] = f"{ferry.ferry.vehicle_capacity} vehicles"
                elif ferry_type.name == 'VEGA':
                    route_data['features'] = "AC, Premium seats, High-speed"
                
                route_list.append(route_data)
            
            routes_data[ferry_type_key][district_key] = route_list
    
    context = {
        'ferry_types': ferry_types,
        'districts': districts,
        'routes_data_json': json.dumps(routes_data),  # Pass as JSON string
    }
    
    return render(request, 'ticket.html', context)

def book_ticket(request, route_id):
    """Display booking form for a specific route"""
    route = get_object_or_404(Route, id=route_id, is_active=True)
    ferry_type_name = request.GET.get('ferry_type', 'PASSENGER')
    ferry_type = get_object_or_404(FerryType, name=ferry_type_name.upper())
    
    # Get route price
    try:
        route_price = RoutePrice.objects.get(route=route, ferry_type=ferry_type, is_active=True)
        price = route_price.price
    except RoutePrice.DoesNotExist:
        price = route.get_fare_for_ferry_type(ferry_type)
    
    # Get available schedules
    schedules = FerrySchedule.objects.filter(
        route=route,
        ferry__ferry_type=ferry_type,
        is_active=True
    ).select_related('ferry').order_by('departure_time')
    
    context = {
        'route': route,
        'ferry_type': ferry_type,
        'price': price,
        'schedules': schedules,
        'is_roro': ferry_type.name == 'RORO'
    }
    
    return render(request, 'book_ticket.html', context)

def process_booking(request):
    """Process the booking form submission"""
    if request.method == 'POST':
        try:
            # Get form data
            schedule_id = request.POST.get('schedule_id')
            ferry_type_id = request.POST.get('ferry_type_id')
            passenger_name = request.POST.get('passenger_name')
            passenger_phone = request.POST.get('passenger_phone')
            passenger_email = request.POST.get('passenger_email', '')
            passenger_count = int(request.POST.get('passenger_count', 1))
            booking_date = request.POST.get('booking_date')
            special_requirements = request.POST.get('special_requirements', '')
            
            # Vehicle info for RoRo
            vehicle_type = request.POST.get('vehicle_type', '')
            vehicle_registration = request.POST.get('vehicle_registration', '')
            driver_name = request.POST.get('driver_name', '')
            driver_license = request.POST.get('driver_license', '')
            
            # Get related objects
            schedule = get_object_or_404(FerrySchedule, id=schedule_id)
            ferry_type = get_object_or_404(FerryType, id=ferry_type_id)
            
            # Create booking
            booking = Booking.objects.create(
                passenger_name=passenger_name,
                passenger_phone=passenger_phone,
                passenger_email=passenger_email,
                schedule=schedule,
                ferry_type=ferry_type,
                booking_date=booking_date,
                passenger_count=passenger_count,
                special_requirements=special_requirements,
                vehicle_type=vehicle_type,
                vehicle_registration=vehicle_registration,
                booking_status='CONFIRMED'
            )
            
            # Create vehicle booking if RoRo
            if ferry_type.name == 'RORO' and vehicle_type:
                VehicleBooking.objects.create(
                    booking=booking,
                    vehicle_type=vehicle_type,
                    vehicle_registration=vehicle_registration,
                    driver_name=driver_name or passenger_name,
                    driver_license=driver_license
                )
            
            # Redirect to success page
            return redirect('booking_success', booking_id=booking.id)
            
        except Exception as e:
            messages.error(request, f'Booking failed: {str(e)}')
            return redirect('ticket')
    
    return redirect('ticket')

def booking_success(request, booking_id):
    """Display booking success page with QR code"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Generate QR code data
    qr_data = {
        'booking_ref': booking.booking_reference,
        'passenger': booking.passenger_name,
        'route': f"{booking.schedule.route.origin_station.name} → {booking.schedule.route.destination_station.name}",
        'date': booking.booking_date.strftime('%Y-%m-%d'),
        'time': booking.schedule.departure_time.strftime('%H:%M'),
        'ferry': booking.schedule.ferry.name,
        'passengers': booking.passenger_count,
        'fare': f"₹{booking.total_fare}"
    }
    
    # Create QR code string
    qr_string = f"SWTD|{booking.booking_reference}|{booking.passenger_name}|{booking.schedule.route.origin_station.name}-{booking.schedule.route.destination_station.name}|{booking.booking_date}|{booking.schedule.departure_time.strftime('%H:%M')}|₹{booking.total_fare}"
    
    # Generate QR code image
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_string)
    qr.make(fit=True)
    
    # Create QR code image
    qr_img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    qr_img.save(buffer, format='PNG')
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'booking': booking,
        'qr_data': qr_data,
        'qr_code_base64': qr_code_base64,
        'has_vehicle': hasattr(booking, 'vehicle_details')
    }
    
    return render(request, 'booking_success.html', context)

def station_master_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('sm_dashboard')
        else:
            return render(request, 'station_master_login.html', {
                    'error': 'You are not authorized to access the admin dashboard.'
                })

    return render(request, 'station_master_login.html')

def sm_dashboard(request):
    return render(request, 'sm_dashboard.html')