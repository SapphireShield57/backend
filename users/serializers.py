from rest_framework import serializers
from django.contrib.auth import get_user_model
from djoser.serializers import TokenCreateSerializer
from rest_framework.exceptions import ValidationError

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'password', 'is_verified']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        # Securely create user with hashed password
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user
    
class CustomTokenCreateSerializer(TokenCreateSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not user.is_verified:
            raise ValidationError('Please verify your email before logging in.')

        return data
