from rest_framework import serializers
from .models import Clinic, VetProfile, WorkingHours, ReferralCode
from django.contrib.auth import get_user_model

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
