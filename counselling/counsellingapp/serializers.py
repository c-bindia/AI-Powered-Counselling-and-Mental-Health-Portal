# mental_health_app/serializers.py
from rest_framework import serializers
from .models import Conversation, Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['sender', 'text', 'timestamp']

class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True) # Nested serializer for messages
    
    class Meta:
        model = Conversation
        fields = ['id', 'start_time', 'messages']