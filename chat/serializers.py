from rest_framework import serializers
from .models import ChatSession, ChatMessage


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for individual chat messages."""
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'text', 'image_url', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']
    
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions (list view)."""
    message_count = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_active', 'message_count', 'last_message']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()
    
    def get_last_message(self, obj):
        last_msg = obj.messages.order_by('-created_at').first()
        if last_msg:
            return {
                'role': last_msg.role,
                'text': last_msg.text[:100] + '...' if len(last_msg.text) > 100 else last_msg.text,
                'created_at': last_msg.created_at
            }
        return None


class ChatSessionDetailSerializer(serializers.ModelSerializer):
    """Serializer for chat session detail with all messages."""
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_active', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at']


class SendMessageSerializer(serializers.Serializer):
    """Serializer for sending a new chat message."""
    message = serializers.CharField(required=False, allow_blank=True, max_length=10000)
    image_data = serializers.CharField(required=False, allow_blank=True, help_text="Base64 encoded image data (e.g., 'image/jpeg;base64,/9j/4AAQ...')")
    session_id = serializers.IntegerField(required=False, allow_null=True, help_text="Optional session ID to continue an existing chat")
    
    def validate(self, data):
        message = data.get('message', '').strip()
        image_data = data.get('image_data', '').strip()
        
        if not message and not image_data:
            raise serializers.ValidationError("Either 'message' or 'image_data' must be provided.")
        
        return data


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for the chat response."""
    session_id = serializers.IntegerField()
    user_message = ChatMessageSerializer()
    bot_message = ChatMessageSerializer()
