# accounts/serializers.py

from rest_framework import serializers
from .models import CustomUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'activity_level', 'height', 'weight', 'username', 'password', 'required_intake']
        extra_kwargs = {
            'password': {'write_only': True},
            'required_intake': {'read_only': True}  # 회원가입 시에는 입력받지 않음
        }

    def create(self, validated_data):
        user = CustomUser(
            username=validated_data['username'],
            email=validated_data['email'],
            name=validated_data['name'],
            activity_level=validated_data['activity_level'],
            height=validated_data['height'],
            weight=validated_data['weight']
        )
        user.set_password(validated_data['password'])
        user.required_intake = user.calculate_required_intake()
        user.save()
        return user
