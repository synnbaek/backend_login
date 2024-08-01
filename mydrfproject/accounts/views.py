# accounts/views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .serializers import UserSerializer

@api_view(['POST'])
def register_user(request):
    if request.method == 'POST':
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# accounts/views.py

from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ObjectDoesNotExist

from .models import CustomUser

@api_view(['POST'])
def user_login(request):
    if request.method == 'POST':
        username = request.data.get('username')
        password = request.data.get('password')

        user = None
        if '@' in username:
            try:
                user = CustomUser.objects.get(email=username)
            except ObjectDoesNotExist:
                pass

        if not user:
            user = authenticate(username=username, password=password)

        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    
# accounts/views.py

from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        try:
            # Delete the user's token to logout
            request.user.auth_token.delete()
            return Response({'message': 'Successfully logged out.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)   
        
# accounts/views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_required_intake(request):
    user = request.user
    required_intake = request.data.get('required_intake')

    if required_intake is not None:
        user.required_intake = required_intake
        user.save()
        return Response({'message': 'Required intake updated successfully.'}, status=status.HTTP_200_OK)
    
    return Response({'error': 'Required intake not provided.'}, status=status.HTTP_400_BAD_REQUEST)

# views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import FoodIntake
from .serializers import FoodIntakeSerializer
from django.db.models import Sum
from rest_framework.permissions import IsAuthenticated

class FoodIntakeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = FoodIntakeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            
            # 날짜를 기준으로 누적된 섭취량 계산
            date = request.data.get('date')
            meal_time = request.data.get('meal_time')

            total_intake = FoodIntake.objects.filter(
                user=request.user,
                date=date
            ).values(
                'meal_time'
            ).annotate(
                total_calories=Sum('calories'),
                total_carbs=Sum('carbs'),
                total_protein=Sum('protein'),
                total_fat=Sum('fat')
            )

            daily_totals = FoodIntake.objects.filter(
                user=request.user,
                date=date
            ).aggregate(
                total_calories=Sum('calories'),
                total_carbs=Sum('carbs'),
                total_protein=Sum('protein'),
                total_fat=Sum('fat')
            )
            
            return Response({
                'meal_totals': total_intake,
                'daily_totals': daily_totals
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
