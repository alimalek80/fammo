from rest_framework import serializers
from userapp.models import CustomUser, Profile
from vets.models import Clinic, WorkingHours

class CombinedClinicUserRegistrationSerializer(serializers.Serializer):
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    # Clinic fields
    clinic_name = serializers.CharField()
    address = serializers.CharField(required=False, allow_blank=True)
    city = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    email_clinic = serializers.EmailField(required=False, allow_blank=True)
    website = serializers.CharField(required=False, allow_blank=True)
    instagram = serializers.CharField(required=False, allow_blank=True)
    specializations = serializers.CharField(required=False, allow_blank=True)
    bio = serializers.CharField(required=False, allow_blank=True)
    clinic_eoi = serializers.BooleanField(required=False)
    vet_name = serializers.CharField(required=False, allow_blank=True)
    degrees = serializers.CharField(required=False, allow_blank=True)
    certifications = serializers.CharField(required=False, allow_blank=True)
    latitude = serializers.DecimalField(required=False, allow_null=True, max_digits=9, decimal_places=6)
    longitude = serializers.DecimalField(required=False, allow_null=True, max_digits=9, decimal_places=6)
    working_hours = serializers.ListField(child=serializers.DictField(), required=False)

    def validate_email(self, value):
        """Check if email already exists"""
        if CustomUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError("This email address is already registered. Please use a different email or try logging in.")
        return value

    def validate_clinic_name(self, value):
        """Check if clinic name already exists"""
        if Clinic.objects.filter(name=value.strip()).exists():
            raise serializers.ValidationError("A clinic with this name already exists. Please choose a different name.")
        return value

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise serializers.ValidationError({'password_confirm': "Passwords do not match."})
        return data
