# api_views.py
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.utils import timezone
from rest_framework import serializers
import datetime

from home.models import *

# Serializers
class StationMasterSerializer(serializers.ModelSerializer):
    station_name = serializers.CharField(source='assigned_station.name', read_only=True)
    station_code = serializers.CharField(source='assigned_station.code', read_only=True)
    district_name = serializers.CharField(source='assigned_station.district.name', read_only=True)
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = StationMaster
        fields = ['employee_id', 'full_name', 'station_name', 'station_code', 
                 'district_name', 'phone_number', 'is_on_duty']

class LoginRequestSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=128, write_only=True)
    station_code = serializers.CharField(max_length=10, required=False, allow_blank=True)
    remember_me = serializers.BooleanField(default=False)
    device_info = serializers.JSONField(required=False)

class LoginResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    station_master = StationMasterSerializer()
    message = serializers.CharField()
    expires_in = serializers.IntegerField()

# API Views
@api_view(['POST'])
@permission_classes([AllowAny])
def station_master_login_api(request):
    """
    RESTful Station Master Login API
    
    POST /api/station-master/login/
    {
        "username": "sm_kochi",
        "password": "password123",
        "station_code": "KC01",  // optional
        "remember_me": false,
        "device_info": {         // optional, for mobile apps
            "device_type": "mobile",
            "os": "android",
            "app_version": "1.0.0"
        }
    }
    """
    serializer = LoginRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response({
            'success': False,
            'errors': serializer.errors,
            'message': 'Invalid input data'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    username = serializer.validated_data['username']
    password = serializer.validated_data['password']
    station_code = serializer.validated_data.get('station_code', '').upper()
    remember_me = serializer.validated_data.get('remember_me', False)
    device_info = serializer.validated_data.get('device_info', {})
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if not user:
        return Response({
            'success': False,
            'message': 'Invalid username or password',
            'error_code': 'INVALID_CREDENTIALS'
        }, status=status.HTTP_401_UNAUTHORIZED)
    
    # Check if user is active
    if not user.is_active:
        return Response({
            'success': False,
            'message': 'Account has been deactivated. Contact administrator.',
            'error_code': 'ACCOUNT_DEACTIVATED'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Check station master profile
    try:
        station_master = StationMaster.objects.select_related(
            'assigned_station', 'assigned_station__district'
        ).get(user=user)
    except StationMaster.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Station Master profile not found',
            'error_code': 'NOT_STATION_MASTER'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Verify station code if provided
    if station_code and station_master.assigned_station.code != station_code:
        return Response({
            'success': False,
            'message': 'Invalid station code for your account',
            'error_code': 'INVALID_STATION_CODE'
        }, status=status.HTTP_403_FORBIDDEN)
    
    # Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access_token = refresh.access_token
    
    # Set token expiry based on remember_me
    if remember_me:
        refresh.set_exp(lifetime=timezone.timedelta(days=7))
        access_token.set_exp(lifetime=timezone.timedelta(hours=24))
    else:
        refresh.set_exp(lifetime=timezone.timedelta(hours=8))
        access_token.set_exp(lifetime=timezone.timedelta(hours=8))
    
    # Update station master status
    station_master.is_on_duty = True
    station_master.save()
    
    # Log device info if provided (for mobile apps)
    if device_info:
        # You can log this for analytics/security
        pass
    
    # Prepare response
    station_master_data = StationMasterSerializer(station_master).data
    
    return Response({
        'success': True,
        'message': f'Welcome back, {user.get_full_name()}!',
        'data': {
            'access_token': str(access_token),
            'refresh_token': str(refresh),
            'token_type': 'Bearer',
            'expires_in': int(access_token['exp'] - timezone.now().timestamp()),
            'station_master': station_master_data
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def station_master_logout_api(request):
    """
    RESTful Station Master Logout API
    
    POST /api/station-master/logout/
    Authorization: Bearer <access_token>
    {
        "refresh_token": "refresh_token_here"
    }
    """
    try:
        # Get station master
        station_master = StationMaster.objects.get(user=request.user)
        station_master.is_on_duty = False
        station_master.save()
        
        # Blacklist refresh token if provided
        refresh_token = request.data.get('refresh_token')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass  # Token already invalid/blacklisted
        
        return Response({
            'success': True,
            'message': 'Successfully logged out'
        }, status=status.HTTP_200_OK)
        
    except StationMaster.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Station Master profile not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def station_master_profile_api(request):
    """
    Get Station Master Profile
    
    GET /api/station-master/profile/
    Authorization: Bearer <access_token>
    """
    try:
        station_master = StationMaster.objects.select_related(
            'assigned_station', 'assigned_station__district'
        ).get(user=request.user)
        
        data = StationMasterSerializer(station_master).data
        
        # Add additional profile data
        data.update({
            'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
            'date_joined': request.user.date_joined.isoformat(),
            'current_time': timezone.now().isoformat(),
        })
        
        return Response({
            'success': True,
            'data': data
        }, status=status.HTTP_200_OK)
        
    except StationMaster.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Station Master profile not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_duty_status_api(request):
    """
    Update Station Master Duty Status
    
    PATCH /api/station-master/duty-status/
    Authorization: Bearer <access_token>
    {
        "is_on_duty": true
    }
    """
    try:
        station_master = StationMaster.objects.get(user=request.user)
        
        is_on_duty = request.data.get('is_on_duty')
        if is_on_duty is not None:
            station_master.is_on_duty = bool(is_on_duty)
            station_master.save()
        
        return Response({
            'success': True,
            'message': 'Duty status updated successfully',
            'data': {
                'is_on_duty': station_master.is_on_duty,
                'updated_at': timezone.now().isoformat()
            }
        }, status=status.HTTP_200_OK)
        
    except StationMaster.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Station Master profile not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([AllowAny])
def stations_list_api(request):
    """
    Get list of all ferry stations
    
    GET /api/stations/
    """
    stations = FerryStation.objects.select_related('district').filter(is_active=True)
    
    stations_data = []
    for station in stations:
        stations_data.append({
            'id': station.id,
            'name': station.name,
            'code': station.code,
            'district': {
                'code': station.district.code,
                'name': station.district.name
            }
        })
    
    return Response({
        'success': True,
        'data': stations_data
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_api(request):
    """
    Refresh JWT Token
    
    POST /api/auth/refresh/
    {
        "refresh": "refresh_token_here"
    }
    """
    refresh_token = request.data.get('refresh')
    
    if not refresh_token:
        return Response({
            'success': False,
            'message': 'Refresh token is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        refresh = RefreshToken(refresh_token)
        access_token = refresh.access_token
        
        return Response({
            'success': True,
            'data': {
                'access_token': str(access_token),
                'token_type': 'Bearer',
                'expires_in': int(access_token['exp'] - timezone.now().timestamp())
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': 'Invalid refresh token'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def validate_qr_simple(request):
    """
    Simple QR Code Validation - Just check if it's real
    
    POST /api/validate-qr/
    Authorization: Bearer <access_token>
    {
        "qr_data": "SWTD|5533987E|Leon Shatto|Ernakulam Main Jetty-Vypin Island Terminal|2025-07-22|08:00|₹60.00"
    }
    """
    
    # Verify user is a station master
    try:
        station_master = StationMaster.objects.get(user=request.user)
    except StationMaster.DoesNotExist:
        return Response({
            'valid': False,
            'message': 'Access denied. Station Master credentials required.'
        }, status=status.HTTP_403_FORBIDDEN)
    
    qr_data = request.data.get('qr_data', '').strip()
    
    if not qr_data:
        return Response({
            'valid': False,
            'message': 'QR code data is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Parse QR code: SWTD|REF|NAME|ROUTE|DATE|TIME|FARE
    try:
        parts = qr_data.split('|')
        
        if len(parts) != 7 or parts[0] != 'SWTD':
            return Response({
                'valid': False,
                'message': 'Invalid QR code format'
            })
        
        booking_ref = parts[1]
        passenger_name = parts[2]
        travel_date = parts[4]
        
        # Find booking in database
        try:
            booking = Booking.objects.select_related(
                'schedule__route__origin_station',
                'schedule__route__destination_station'
            ).get(booking_reference=booking_ref)
        except Booking.DoesNotExist:
            return Response({
                'valid': False,
                'message': f'Booking {booking_ref} not found'
            })
        
        # Simple validations
        if booking.booking_status == 'CANCELLED':
            return Response({
                'valid': False,
                'message': 'Booking has been cancelled'
            })
        
        if booking.passenger_name.lower() != passenger_name.lower():
            return Response({
                'valid': False,
                'message': 'Passenger name does not match'
            })
        
        # Check travel date
        qr_date = datetime.strptime(travel_date, '%Y-%m-%d').date()
        if booking.booking_date != qr_date:
            return Response({
                'valid': False,
                'message': 'Travel date does not match'
            })
        
        # Valid ticket
        return Response({
            'valid': True,
            'message': f'Valid ticket for {passenger_name}',
            'booking_details': {
                'reference': booking.booking_reference,
                'passenger': booking.passenger_name,
                'phone': booking.passenger_phone,
                'passengers': booking.passenger_count,
                'date': booking.booking_date.strftime('%Y-%m-%d'),
                'route': f"{booking.schedule.route.origin_station.name} → {booking.schedule.route.destination_station.name}",
                'fare': f"₹{booking.total_fare}",
                'ferry_type': booking.ferry_type.display_name
            }
        })
        
    except ValueError as e:
        return Response({
            'valid': False,
            'message': 'Invalid date format in QR code'
        })
    except Exception as e:
        return Response({
            'valid': False,
            'message': f'Error validating QR code: {str(e)}'
        })
