# accounts/models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, default='example@example.com')  # 기본값 설정
    name = models.CharField(max_length=30, default='Unknown')  # 기본값 설정
    ACTIVITY_LEVEL_CHOICES = [
        (25, '25'),
        (30, '30'),
        (35, '35'),
        (40, '40'),
    ]
    activity_level = models.IntegerField(choices=ACTIVITY_LEVEL_CHOICES, default=25)  # 활동량
    height = models.FloatField(default=170.0)  # 기본값 설정
    weight = models.FloatField(default=70.0)   # 기본값 설정
    required_intake = models.FloatField(null=True, blank=True)  # 권장 섭취량


    def calculate_required_intake(self):
        # 권장 섭취량 계산 로직 (여기서는 단순 예시)
        # 예: (체중 * 활동 수준) * 10 + 기본 대사율 (일반적으로는 더 복잡한 계산 사용)
        return (self.weight * self.activity_level) * 10


    def __str__(self):
        return self.username
