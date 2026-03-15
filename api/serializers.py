from rest_framework import serializers
from userapp.models import CustomUser, Profile
from vets.models import Clinic, WorkingHours
from blog.models import BlogPost, BlogCategory
from django.utils import timezone

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


# Blog Serializers

class BlogCategorySerializer(serializers.ModelSerializer):
    """Serializer for blog categories"""
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug']


class BlogPostMinimalSerializer(serializers.ModelSerializer):
    """Minimal serializer with just title and URL"""
    url = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = ['id', 'title', 'slug', 'url']
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/blog/{obj.slug}/')
        return f'/blog/{obj.slug}/'


class BlogPostListSerializer(serializers.ModelSerializer):
    """List serializer with moderate details (no full content)"""
    url = serializers.SerializerMethodField()
    categories = BlogCategorySerializer(source='category', many=True, read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    excerpt = serializers.CharField(read_only=True)
    image_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'url', 'categories', 'excerpt', 
            'image_url', 'author_name', 'published_at', 'views', 
            'language', 'average_rating'
        ]
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/blog/{obj.slug}/')
        return f'/blog/{obj.slug}/'
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_average_rating(self, obj):
        return obj.average_rating()


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer with full content"""
    url = serializers.SerializerMethodField()
    categories = BlogCategorySerializer(source='category', many=True, read_only=True)
    author_name = serializers.CharField(source='author.get_full_name', read_only=True)
    author_email = serializers.EmailField(source='author.email', read_only=True)
    image_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'url', 'categories', 'content', 
            'meta_description', 'meta_keywords', 'image_url', 
            'author_name', 'author_email', 'created_at', 'updated_at',
            'published_at', 'views', 'language', 'average_rating',
            'total_comments'
        ]
    
    def get_url(self, obj):
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/blog/{obj.slug}/')
        return f'/blog/{obj.slug}/'
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None
    
    def get_average_rating(self, obj):
        return obj.average_rating()
    
    def get_total_comments(self, obj):
        return obj.comments.count()
