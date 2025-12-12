"""
API endpoints for legal documents and consent management.

Available endpoints:
- GET /api/v1/legal/documents/ - List legal documents (public)
- GET /api/v1/legal/documents/{doc_type}/{language}/ - Get specific document
- POST /api/v1/legal/consent/user/ - Record user consent
- POST /api/v1/legal/consent/clinic/ - Record clinic consent
- GET /api/v1/legal/consent/user/ - Get user's consent history (authenticated)
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.db.models import Q
from django.shortcuts import get_object_or_404

from core.models import LegalDocument, UserConsent, ClinicConsent, ConsentLog, DocumentType
from core.serializers import (
    LegalDocumentSerializer,
    LegalDocumentAdminSerializer,
    UserConsentSerializer,
    ClinicConsentSerializer,
    ConsentLogSerializer,
)


class LegalDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for retrieving legal documents.
    
    Endpoints:
    - GET /legal/documents/ - List all active documents (public)
    - GET /legal/documents/?doc_type=user_terms - Filter by document type
    - GET /legal/documents/?language=en - Filter by language
    - GET /legal/documents/{id}/ - Get specific document
    - GET /legal/documents/by_type/ - Get latest version by type and language
    """
    queryset = LegalDocument.objects.filter(is_active=True)
    serializer_class = LegalDocumentSerializer
    pagination_class = PageNumberPagination
    filterset_fields = ['doc_type', 'language']
    ordering_fields = ['effective_date', 'created_at']
    ordering = ['-effective_date']
    
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=['get'])
    def by_type(self, request):
        """
        Get the latest active document by type and language.
        
        Query params:
        - doc_type: Document type (user_terms, user_privacy, clinic_terms, clinic_partnership, clinic_eoi)
        - language: Language code (default: en)
        
        Example: GET /legal/documents/by_type/?doc_type=user_terms&language=en
        """
        doc_type = request.query_params.get('doc_type')
        language = request.query_params.get('language', 'en')
        
        if not doc_type:
            return Response(
                {'error': 'doc_type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate doc_type
        if doc_type not in [choice[0] for choice in DocumentType.choices]:
            return Response(
                {'error': f'Invalid doc_type. Must be one of: {[c[0] for c in DocumentType.choices]}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        document = get_object_or_404(
            LegalDocument,
            doc_type=doc_type,
            language=language,
            is_active=True
        )
        
        serializer = self.get_serializer(document)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def available_types(self, request):
        """List all available document types."""
        types = [
            {'value': choice[0], 'label': choice[1]}
            for choice in DocumentType.choices
        ]
        return Response(types)


class UserConsentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user consent to legal documents.
    
    Endpoints:
    - POST /legal/consent/user/ - Record user consent
    - GET /legal/consent/user/ - Get user's consent history (authenticated)
    - GET /legal/consent/user/{id}/ - Get specific consent record
    """
    queryset = UserConsent.objects.all()
    serializer_class = UserConsentSerializer
    pagination_class = PageNumberPagination
    ordering = ['-accepted_at']
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Users can only see their own consent records."""
        if self.request.user.is_staff:
            return UserConsent.objects.all()
        return UserConsent.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Associate consent with the current user."""
        user = self.request.user
        document = serializer.validated_data['document']
        
        # Extract IP and user agent for audit trail
        ip_address = self.get_client_ip()
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        
        # Create or update consent record
        consent, created = UserConsent.objects.update_or_create(
            user=user,
            document=document,
            defaults={
                'accepted': serializer.validated_data.get('accepted', True),
                'ip_address': ip_address,
                'user_agent': user_agent,
            }
        )
        
        # Log the action
        ConsentLog.objects.create(
            action='accepted' if consent.accepted else 'revoked',
            document=document,
            user=user,
            details=f"User {'accepted' if consent.accepted else 'revoked'} {document.get_doc_type_display()}"
        )
    
    @staticmethod
    def get_client_ip(request=None):
        """Extract client IP from request."""
        if request is None:
            return None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_client_ip(self):
        """Extract client IP from request."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=False, methods=['get'])
    def check_compliance(self, request):
        """
        Check if user has accepted required documents.
        
        Returns:
        {
            "compliant": bool,
            "missing_documents": [],
            "accepted_documents": []
        }
        """
        user = request.user
        
        # Required documents for users
        required_docs = [
            DocumentType.USER_TERMS_CONDITIONS,
            DocumentType.USER_PRIVACY_POLICY,
        ]
        
        # Get user's accepted documents
        accepted = UserConsent.objects.filter(
            user=user,
            accepted=True
        ).values_list('document__doc_type', flat=True)
        
        missing = [doc for doc in required_docs if doc not in accepted]
        
        return Response({
            'compliant': len(missing) == 0,
            'missing_documents': missing,
            'accepted_documents': list(accepted),
        })


class ClinicConsentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing clinic consent to legal documents.
    
    Endpoints:
    - POST /legal/consent/clinic/ - Record clinic consent
    - GET /legal/consent/clinic/ - Get clinic's consent history (authenticated clinic owner)
    """
    queryset = ClinicConsent.objects.all()
    serializer_class = ClinicConsentSerializer
    pagination_class = PageNumberPagination
    ordering = ['-accepted_at']
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Users can only see consent records for clinics they own."""
        if self.request.user.is_staff:
            return ClinicConsent.objects.all()
        return ClinicConsent.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Associate consent with the current user (clinic owner)."""
        user = self.request.user
        document = serializer.validated_data['document']
        clinic_email = serializer.validated_data['clinic_email']
        
        # Extract IP and user agent for audit trail
        ip_address = self.get_client_ip()
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        
        # Create or update consent record
        consent, created = ClinicConsent.objects.update_or_create(
            user=user,
            document=document,
            clinic_email=clinic_email,
            defaults={
                'accepted': serializer.validated_data.get('accepted', True),
                'ip_address': ip_address,
                'user_agent': user_agent,
            }
        )
        
        # Log the action
        ConsentLog.objects.create(
            action='accepted' if consent.accepted else 'revoked',
            document=document,
            user=user,
            details=f"Clinic {clinic_email} {'accepted' if consent.accepted else 'revoked'} {document.get_doc_type_display()}"
        )
    
    def get_client_ip(self):
        """Extract client IP from request."""
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        return ip
    
    @action(detail=False, methods=['get'])
    def check_compliance(self, request):
        """
        Check if clinic (by email) has accepted required documents.
        
        Query params:
        - clinic_email: Email of clinic to check
        
        Returns:
        {
            "compliant": bool,
            "missing_documents": [],
            "accepted_documents": []
        }
        """
        clinic_email = request.query_params.get('clinic_email')
        
        if not clinic_email:
            return Response(
                {'error': 'clinic_email parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Required documents for clinics
        required_docs = [
            DocumentType.CLINIC_TERMS_CONDITIONS,
            DocumentType.CLINIC_PARTNERSHIP,
        ]
        
        # Get clinic's accepted documents
        accepted = ClinicConsent.objects.filter(
            clinic_email=clinic_email,
            accepted=True
        ).values_list('document__doc_type', flat=True)
        
        missing = [doc for doc in required_docs if doc not in accepted]
        
        return Response({
            'compliant': len(missing) == 0,
            'missing_documents': missing,
            'accepted_documents': list(accepted),
        })


class ConsentLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing consent audit logs (admin only).
    """
    queryset = ConsentLog.objects.all()
    serializer_class = ConsentLogSerializer
    pagination_class = PageNumberPagination
    filterset_fields = ['action', 'document__doc_type']
    ordering = ['-timestamp']
    
    permission_classes = [permissions.IsAdminUser]
