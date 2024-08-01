# accounts/urls.py

from django.urls import path
from .views import register_user, user_login, user_logout, FoodIntakeView

urlpatterns = [
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('food-intake/', FoodIntakeView.as_view(), name='food-intake'),
   
]