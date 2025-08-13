from rest_framework.serializers import ModelSerializer
from django.contrib.auth.models import User
from .models import User as mobile, OTPCode, Session, Message


class DefaultUserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class MobileSerializer(ModelSerializer):
    class Meta:
        model = mobile
        fields = '__all__'
        depth = 1

class OTPCodeSerializer(ModelSerializer):
    class Meta:
        model = OTPCode
        fields = '__all__'
        read_only_fields = ('code', )


class SessionSerializer(ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'


class MessageSerializer(ModelSerializer):
    class Meta:
        model = Message
        fields = '__all__'