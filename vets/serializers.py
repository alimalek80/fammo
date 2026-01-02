from rest_framework import serializers
from .models import Clinic, VetProfile, WorkingHours, ReferralCode, Appointment, AppointmentReason, AppointmentStatus, ClinicNotification
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()


class WorkingHoursSerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = WorkingHours
        fields = ['id', 'day_of_week', 'day_name', 'is_closed', 'open_time', 'close_time']


class VetProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = VetProfile
        fields = ['id', 'vet_name', 'degrees', 'certifications']


class ReferralCodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReferralCode
        fields = ['id', 'code', 'is_active', 'created_at']
        read_only_fields = ['code', 'created_at']


class ClinicListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing clinics"""
    referral_code = serializers.SerializerMethodField()
    
    def get_referral_code(self, obj):
        return obj.active_referral_code
    
    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'slug', 'city', 'address', 'latitude', 'longitude',
            'phone', 'email', 'website', 'instagram', 'specializations',
            'logo', 'is_verified', 'email_confirmed', 'admin_approved',
            'is_active_clinic', 'referral_code'
        ]
        read_only_fields = ['slug', 'is_verified', 'email_confirmed', 'admin_approved', 'is_active_clinic']


class ClinicDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with nested relationships"""
    working_hours_schedule = WorkingHoursSerializer(many=True, read_only=True)
    vet_profile = VetProfileSerializer(read_only=True)
    referral_codes = ReferralCodeSerializer(many=True, read_only=True)
    active_referral_code = serializers.CharField(read_only=True)
    formatted_working_hours = serializers.SerializerMethodField()
    owner_email = serializers.EmailField(source='owner.email', read_only=True)
    
    def get_formatted_working_hours(self, obj):
        return obj.get_formatted_working_hours()
    
    class Meta:
        model = Clinic
        fields = [
            'id', 'name', 'slug', 'city', 'address', 'latitude', 'longitude',
            'phone', 'email', 'website', 'instagram', 'specializations',
            'working_hours', 'bio', 'logo', 'is_verified', 'clinic_eoi',
            'email_confirmed', 'admin_approved', 'is_active_clinic',
            'owner_email', 'working_hours_schedule', 'formatted_working_hours',
            'vet_profile', 'referral_codes', 'active_referral_code',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'slug', 'is_verified', 'email_confirmed', 'admin_approved',
            'is_active_clinic', 'created_at', 'updated_at'
        ]


class ClinicRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for clinic registration"""
    vet_name = serializers.CharField(write_only=True, required=False, allow_blank=True)
    degrees = serializers.CharField(write_only=True, required=False, allow_blank=True)
    certifications = serializers.CharField(write_only=True, required=False, allow_blank=True)
    
    class Meta:
        model = Clinic
        fields = [
            'name', 'city', 'address', 'latitude', 'longitude',
            'phone', 'email', 'website', 'instagram', 'specializations',
            'working_hours', 'bio', 'logo', 'clinic_eoi',
            'vet_name', 'degrees', 'certifications'
        ]
    
    def create(self, validated_data):
        # Extract vet profile data
        vet_name = validated_data.pop('vet_name', None)
        degrees = validated_data.pop('degrees', '')
        certifications = validated_data.pop('certifications', '')
        
        # Create clinic
        clinic = Clinic.objects.create(**validated_data)
        
        # Create vet profile if vet_name provided
        if vet_name:
            VetProfile.objects.create(
                clinic=clinic,
                vet_name=vet_name,
                degrees=degrees,
                certifications=certifications
            )
        
        # Create default referral code
        ReferralCode.create_default_for_clinic(clinic)
        
        return clinic


class ClinicUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating clinic information"""
    
    class Meta:
        model = Clinic
        fields = [
            'name', 'city', 'address', 'latitude', 'longitude',
            'phone', 'email', 'website', 'instagram', 'specializations',
            'working_hours', 'bio', 'logo', 'clinic_eoi'
        ]


class VetProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating vet profile"""
    
    class Meta:
        model = VetProfile
        fields = ['vet_name', 'degrees', 'certifications']


class WorkingHoursUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating working hours"""
    
    class Meta:
        model = WorkingHours
        fields = ['day_of_week', 'is_closed', 'open_time', 'close_time']
    
    def validate(self, data):
        """Validate that open_time is before close_time"""
        if not data.get('is_closed'):
            if data.get('open_time') and data.get('close_time'):
                if data['open_time'] >= data['close_time']:
                    raise serializers.ValidationError("Opening time must be before closing time")
        return data


# ==================== APPOINTMENT SERIALIZERS ====================

class AppointmentReasonSerializer(serializers.ModelSerializer):
    """Serializer for appointment reasons"""
    class Meta:
        model = AppointmentReason
        fields = ['id', 'name', 'description']


class PetBasicSerializer(serializers.Serializer):
    """Basic pet info for appointments"""
    id = serializers.IntegerField()
    name = serializers.CharField()
    pet_type = serializers.SerializerMethodField()
    breed = serializers.SerializerMethodField()
    image = serializers.ImageField()
    
    def get_pet_type(self, obj):
        return obj.pet_type.name if obj.pet_type else None
    
    def get_breed(self, obj):
        return obj.breed.name if obj.breed else None


class UserBasicSerializer(serializers.Serializer):
    """Basic user info for appointments"""
    id = serializers.IntegerField()
    email = serializers.EmailField()
    first_name = serializers.SerializerMethodField()
    last_name = serializers.SerializerMethodField()
    phone = serializers.SerializerMethodField()
    
    def get_first_name(self, obj):
        return getattr(obj.profile, 'first_name', '') if hasattr(obj, 'profile') else ''
    
    def get_last_name(self, obj):
        return getattr(obj.profile, 'last_name', '') if hasattr(obj, 'profile') else ''
    
    def get_phone(self, obj):
        return getattr(obj.profile, 'phone', '') if hasattr(obj, 'profile') else ''


class AppointmentListSerializer(serializers.ModelSerializer):
    """Serializer for listing appointments"""
    pet_name = serializers.CharField(source='pet.name', read_only=True)
    pet_type = serializers.SerializerMethodField()
    clinic_name = serializers.CharField(source='clinic.name', read_only=True)
    clinic_address = serializers.CharField(source='clinic.address', read_only=True)
    reason_name = serializers.CharField(source='reason.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    
    def get_pet_type(self, obj):
        return obj.pet.pet_type.name if obj.pet.pet_type else None
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'reference_code', 'pet_name', 'pet_type', 'clinic_name', 
            'clinic_address', 'appointment_date', 'appointment_time',
            'duration_minutes', 'reason_name', 'reason_text', 'status',
            'status_display', 'is_upcoming', 'can_cancel', 'created_at'
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single appointment view"""
    pet = PetBasicSerializer(read_only=True)
    user = UserBasicSerializer(read_only=True)
    clinic = ClinicListSerializer(read_only=True)
    reason = AppointmentReasonSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_upcoming = serializers.BooleanField(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'reference_code', 'pet', 'user', 'clinic',
            'appointment_date', 'appointment_time', 'duration_minutes',
            'reason', 'reason_text', 'notes', 'status', 'status_display',
            'is_upcoming', 'can_cancel', 'confirmed_at', 'cancelled_at',
            'cancellation_reason', 'created_at', 'updated_at'
        ]


class AppointmentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating appointments"""
    
    class Meta:
        model = Appointment
        fields = [
            'clinic', 'pet', 'appointment_date', 'appointment_time',
            'reason', 'reason_text', 'notes'
        ]
    
    def validate_pet(self, value):
        """Ensure the pet belongs to the requesting user"""
        request = self.context.get('request')
        if request and value.user != request.user:
            raise serializers.ValidationError("You can only book appointments for your own pets.")
        return value
    
    def validate_clinic(self, value):
        """Ensure the clinic has verified their email (only requirement for accepting appointments)"""
        if not value.email_confirmed:
            raise serializers.ValidationError("This clinic is not currently accepting appointments.")
        return value
    
    def validate(self, data):
        """Validate the appointment date and time"""
        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')
        clinic = data.get('clinic')
        
        # Check date is in the future
        today = timezone.now().date()
        if appointment_date < today:
            raise serializers.ValidationError({
                'appointment_date': "Appointment date must be in the future."
            })
        
        # Check if same day, time must be in the future
        if appointment_date == today:
            current_time = timezone.now().time()
            if appointment_time <= current_time:
                raise serializers.ValidationError({
                    'appointment_time': "Appointment time must be in the future."
                })
        
        # Check clinic is open on this day
        day_of_week = appointment_date.weekday()
        try:
            working_hours = clinic.working_hours_schedule.get(day_of_week=day_of_week)
            if working_hours.is_closed:
                raise serializers.ValidationError({
                    'appointment_date': f"The clinic is closed on {working_hours.get_day_of_week_display()}."
                })
            
            # Check time is within working hours
            if working_hours.open_time and working_hours.close_time:
                if appointment_time < working_hours.open_time:
                    raise serializers.ValidationError({
                        'appointment_time': f"Clinic opens at {working_hours.open_time.strftime('%H:%M')}."
                    })
                if appointment_time >= working_hours.close_time:
                    raise serializers.ValidationError({
                        'appointment_time': f"Clinic closes at {working_hours.close_time.strftime('%H:%M')}."
                    })
        except WorkingHours.DoesNotExist:
            # No working hours defined for this day - allow booking
            pass
        
        # Check for conflicting appointments (same clinic, same time)
        existing = Appointment.objects.filter(
            clinic=clinic,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            status__in=[AppointmentStatus.PENDING, AppointmentStatus.CONFIRMED]
        ).exists()
        
        if existing:
            raise serializers.ValidationError({
                'appointment_time': "This time slot is already booked. Please choose another time."
            })
        
        return data
    
    def create(self, validated_data):
        """Create appointment and send notifications"""
        request = self.context.get('request')
        validated_data['user'] = request.user
        appointment = super().create(validated_data)
        
        # Send notifications (done in view or signal)
        return appointment


class AppointmentCancelSerializer(serializers.Serializer):
    """Serializer for cancelling appointments"""
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)


class AvailableSlotsSerializer(serializers.Serializer):
    """Serializer for available time slots"""
    date = serializers.DateField()
    slots = serializers.ListField(child=serializers.TimeField())
    is_open = serializers.BooleanField()
    working_hours = serializers.DictField(required=False)


# ==================== CLINIC NOTIFICATION SERIALIZERS ====================

class ClinicNotificationSerializer(serializers.ModelSerializer):
    """Serializer for clinic notifications"""
    appointment_reference = serializers.CharField(
        source='appointment.reference_code', 
        read_only=True
    )
    
    class Meta:
        model = ClinicNotification
        fields = [
            'id', 'notification_type', 'title', 'message',
            'appointment', 'appointment_reference', 'is_read',
            'read_at', 'created_at'
        ]
        read_only_fields = ['notification_type', 'title', 'message', 'appointment', 'created_at']


class ClinicAppointmentListSerializer(serializers.ModelSerializer):
    """Serializer for clinic to view their appointments"""
    pet = PetBasicSerializer(read_only=True)
    user = UserBasicSerializer(read_only=True)
    reason = AppointmentReasonSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'reference_code', 'pet', 'user',
            'appointment_date', 'appointment_time', 'duration_minutes',
            'reason', 'reason_text', 'notes', 'status', 'status_display',
            'confirmed_at', 'created_at'
        ]


class ClinicAppointmentUpdateSerializer(serializers.Serializer):
    """Serializer for clinic to update appointment status"""
    status = serializers.ChoiceField(choices=[
        (AppointmentStatus.CONFIRMED, 'Confirm'),
        (AppointmentStatus.CANCELLED_BY_CLINIC, 'Cancel'),
        (AppointmentStatus.COMPLETED, 'Complete'),
        (AppointmentStatus.NO_SHOW, 'No Show'),
    ])
    cancellation_reason = serializers.CharField(required=False, allow_blank=True)

