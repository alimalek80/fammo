from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics, permissions, status
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import ChatSession, ChatMessage
from .serializers import (
    ChatSessionSerializer,
    ChatSessionDetailSerializer,
    ChatMessageSerializer,
    SendMessageSerializer,
    ChatResponseSerializer,
)
from .ai_service import pet_answer
from .views import save_image_from_base64
from pet.models import Pet


class ChatSessionListView(generics.ListAPIView):
    """
    GET /api/v1/chat/sessions/
    
    List all chat sessions for the authenticated user.
    Returns sessions ordered by most recently updated.
    """
    serializer_class = ChatSessionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user).order_by('-updated_at')


class ChatSessionDetailView(generics.RetrieveDestroyAPIView):
    """
    GET /api/v1/chat/sessions/<id>/
    DELETE /api/v1/chat/sessions/<id>/
    
    Retrieve a specific chat session with all messages, or delete it.
    """
    serializer_class = ChatSessionDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatSession.objects.filter(user=self.request.user)


class ChatSessionCreateView(APIView):
    """
    POST /api/v1/chat/sessions/new/
    
    Create a new chat session. Optionally deactivates other sessions.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Deactivate other sessions
        ChatSession.objects.filter(user=request.user, is_active=True).update(is_active=False)
        
        # Create new session
        session = ChatSession.objects.create(user=request.user, is_active=True)
        
        serializer = ChatSessionSerializer(session, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SendMessageView(APIView):
    """
    POST /api/v1/chat/send/
    
    Send a message to the AI and get a response.
    
    Request body:
    {
        "message": "What food is best for my dog?",
        "image_data": "image/jpeg;base64,/9j/4AAQ...",  // optional
        "session_id": 123  // optional, creates new session if not provided
    }
    
    Response:
    {
        "session_id": 123,
        "user_message": { ... },
        "bot_message": { ... }
    }
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        message_text = serializer.validated_data.get('message', '').strip()
        image_data = serializer.validated_data.get('image_data', '').strip()
        session_id = serializer.validated_data.get('session_id')
        
        # Get or create session
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            # Try to get active session or create new one
            session = ChatSession.objects.filter(user=request.user, is_active=True).first()
            if not session:
                session = ChatSession.objects.create(user=request.user, is_active=True)
        
        # Check if this is the first message in the session
        is_first_message = not session.messages.exists()
        
        # Get user context for personalization
        user_first = self._get_user_first_name(request.user)
        pet_profiles = self._get_pet_profiles(request.user)
        
        # Save user message
        user_message = ChatMessage(
            session=session,
            role='user',
            text=message_text
        )
        save_image_from_base64(user_message, image_data)
        user_message.save()
        
        # Get AI response
        bot_reply = pet_answer(
            message_text,
            user_name=user_first,
            pet_profiles=pet_profiles,
            is_first_message=is_first_message,
            image_base64=image_data or None
        )
        
        # Save bot message
        bot_message = ChatMessage.objects.create(
            session=session,
            role='bot',
            text=bot_reply
        )
        
        # Update session timestamp
        session.save()
        
        # Prepare response
        response_data = {
            'session_id': session.id,
            'user_message': ChatMessageSerializer(user_message, context={'request': request}).data,
            'bot_message': ChatMessageSerializer(bot_message, context={'request': request}).data,
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    def _get_user_first_name(self, user):
        """Get user's first name for personalization."""
        profile = getattr(user, "profile", None)
        if profile and getattr(profile, "first_name", None):
            return (profile.first_name or "").strip()
        
        username_like = getattr(user, "username", None) or getattr(user, "email", "")
        return (username_like or "").split("@")[0]
    
    def _get_pet_profiles(self, user):
        """Get formatted pet profiles for AI context."""
        pets_qs = Pet.objects.filter(user=user).select_related(
            "pet_type", "breed", "gender", "age_category", "body_type", 
            "activity_level", "food_feeling", "food_importance", "treat_frequency"
        ).prefetch_related("food_types", "food_allergies", "health_issues")
        
        pets = list(pets_qs)
        if not pets:
            return None
        
        parts = []
        for idx, p in enumerate(pets, start=1):
            parts.append(f"Pet {idx}:\n" + p.get_full_profile_for_ai())
        return "\n\n".join(parts)


class ChatHistoryView(generics.ListAPIView):
    """
    GET /api/v1/chat/sessions/<session_id>/messages/
    
    Get all messages for a specific chat session.
    Supports pagination.
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        session_id = self.kwargs.get('session_id')
        session = get_object_or_404(ChatSession, id=session_id, user=self.request.user)
        return session.messages.all().order_by('created_at')


class DeleteMessageView(generics.DestroyAPIView):
    """
    DELETE /api/v1/chat/messages/<id>/
    
    Delete a specific message (and its image if present).
    """
    serializer_class = ChatMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ChatMessage.objects.filter(session__user=self.request.user)
    
    def perform_destroy(self, instance):
        if instance.image:
            instance.delete_image_file()
        instance.delete()


class ClearSessionView(APIView):
    """
    POST /api/v1/chat/sessions/<session_id>/clear/
    
    Clear all messages from a session without deleting the session itself.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, session_id):
        session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        
        # Delete all messages
        for msg in session.messages.all():
            if msg.image:
                msg.delete_image_file()
            msg.delete()
        
        # Reset title
        session.title = ""
        session.save(update_fields=['title'])
        
        return Response({'success': True, 'message': 'Session cleared'}, status=status.HTTP_200_OK)


class ActiveSessionView(APIView):
    """
    GET /api/v1/chat/active/
    
    Get the user's current active session, or create one if none exists.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        session = ChatSession.objects.filter(user=request.user, is_active=True).first()
        
        if not session:
            session = ChatSession.objects.create(user=request.user, is_active=True)
        
        serializer = ChatSessionDetailSerializer(session, context={'request': request})
        return Response(serializer.data)
