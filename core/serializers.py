from rest_framework import serializers
from .models import OnboardingSlide, LegalDocument, UserConsent, ClinicConsent, ConsentLog, DocumentType


class OnboardingSlideSerializer(serializers.ModelSerializer):
    """Serializer for onboarding slides with localized fields."""
    
    icon_url = serializers.SerializerMethodField()
    
    class Meta:
        model = OnboardingSlide
        fields = ['id', 'title', 'description', 'icon_url', 'order', 'button_text']
    
    def get_icon_url(self, obj):
        """Return absolute URL for the icon."""
        request = self.context.get('request')
        if obj.icon and hasattr(obj.icon, 'url'):
            if request is not None:
                return request.build_absolute_uri(obj.icon.url)
            return obj.icon.url
        return None


# ============================================
# Legal Document Serializers
# ============================================

class LegalDocumentSerializer(serializers.ModelSerializer):
    """Serializer for legal documents (read-only for public)."""
    doc_type_display = serializers.CharField(source='get_doc_type_display', read_only=True)
    
    class Meta:
        model = LegalDocument
        fields = [
            'id',
            'doc_type',
            'doc_type_display',
            'language',
            'title',
            'version',
            'content',
            'summary',
            'effective_date',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class LegalDocumentAdminSerializer(serializers.ModelSerializer):
    """Serializer for legal documents (admin: full access)."""
    doc_type_display = serializers.CharField(source='get_doc_type_display', read_only=True)
    
    class Meta:
        model = LegalDocument
        fields = [
            'id',
            'doc_type',
            'doc_type_display',
            'language',
            'title',
            'version',
            'content',
            'summary',
            'is_active',
            'effective_date',
            'admin_notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserConsentSerializer(serializers.ModelSerializer):
    """Serializer for user consent tracking."""
    document_title = serializers.CharField(source='document.title', read_only=True)
    document_type = serializers.CharField(source='document.doc_type', read_only=True)
    
    class Meta:
        model = UserConsent
        fields = [
            'id',
            'document',
            'document_title',
            'document_type',
            'accepted',
            'accepted_at',
        ]
        read_only_fields = ['id', 'accepted_at']


class ClinicConsentSerializer(serializers.ModelSerializer):
    """Serializer for clinic consent tracking."""
    document_title = serializers.CharField(source='document.title', read_only=True)
    document_type = serializers.CharField(source='document.doc_type', read_only=True)
    
    class Meta:
        model = ClinicConsent
        fields = [
            'id',
            'document',
            'document_title',
            'document_type',
            'clinic_email',
            'accepted',
            'accepted_at',
        ]
        read_only_fields = ['id', 'accepted_at']


class ConsentLogSerializer(serializers.ModelSerializer):
    """Serializer for consent audit logs."""
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    document_title = serializers.CharField(source='document.title', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    admin_email = serializers.CharField(source='admin_user.email', read_only=True)
    
    class Meta:
        model = ConsentLog
        fields = [
            'id',
            'action',
            'action_display',
            'document',
            'document_title',
            'user',
            'user_email',
            'admin_user',
            'admin_email',
            'details',
            'timestamp',
        ]
        read_only_fields = ['id', 'timestamp']

