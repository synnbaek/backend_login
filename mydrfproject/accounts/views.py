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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import UserSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_profile(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response(serializer.data, status=status.HTTP_200_OK)

        
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

from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Sum
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from .models import FoodIntake
from .serializers import FoodIntakeSerializer

class FoodIntakeView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        serializer = FoodIntakeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            
            # 날짜를 기준으로 누적된 섭취량 계산
            date = request.data.get('date')

            # 식사 종류별로 영양섭취량 누적 계산
            meal_totals = FoodIntake.objects.filter(
                user=request.user,
                date=date
            ).values('meal_time').annotate(
                total_calories=Sum('calories'),
                total_carbs=Sum('carbs'),
                total_protein=Sum('protein'),
                total_fat=Sum('fat')
            )

            # 하루 총 섭취량 계산
            daily_totals = FoodIntake.objects.filter(
                user=request.user,
                date=date
            ).aggregate(
                total_calories=Sum('calories'),
                total_carbs=Sum('carbs'),
                total_protein=Sum('protein'),
                total_fat=Sum('fat')
            )

            # 소수점 두 자리까지 포맷팅
            def format_decimal(value):
                """Decimal 값을 소수점 두 자리까지 포맷팅"""
                if value is None:
                    return '0.00'
                return str(Decimal(value).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))

            # 응답 형식 맞추기
            meal_totals_dict = {
                meal['meal_time']: {
                    'total_calories': format_decimal(meal['total_calories']),
                    'total_carbs': format_decimal(meal['total_carbs']),
                    'total_protein': format_decimal(meal['total_protein']),
                    'total_fat': format_decimal(meal['total_fat'])
                } for meal in meal_totals
            }

            # 하루 총 섭취량 추가
            meal_totals_dict['daily'] = {
                'total_calories': format_decimal(daily_totals['total_calories']),
                'total_carbs': format_decimal(daily_totals['total_carbs']),
                'total_protein': format_decimal(daily_totals['total_protein']),
                'total_fat': format_decimal(daily_totals['total_fat'])
            }

            # 날짜 추가
            meal_totals_dict['date'] = date
            
            return Response(meal_totals_dict, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        # 요청에서 날짜를 가져옵니다
        date = request.query_params.get('date')

        if not date:
            return Response({"detail": "Date parameter is required."}, status=status.HTTP_400_BAD_REQUEST)

        # 저장된 식단을 가져옵니다
        meal_totals = FoodIntake.objects.filter(
            user=request.user,
            date=date
        ).values('meal_time').annotate(
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

        # 소수점 두 자리까지 포맷팅
        def format_decimal(value):
            
            if value is None:
                return '0.00'
            return str(Decimal(value).quantize(Decimal('0.00'), rounding=ROUND_HALF_UP))

        # 응답 형식 맞추기
        meal_totals_dict = {
            meal['meal_time']: {
                'total_calories': format_decimal(meal['total_calories']),
                'total_carbs': format_decimal(meal['total_carbs']),
                'total_protein': format_decimal(meal['total_protein']),
                'total_fat': format_decimal(meal['total_fat'])
            } for meal in meal_totals
        }

        # 하루 총 섭취량 추가
        meal_totals_dict['daily'] = {
            'total_calories': format_decimal(daily_totals['total_calories']),
            'total_carbs': format_decimal(daily_totals['total_carbs']),
            'total_protein': format_decimal(daily_totals['total_protein']),
            'total_fat': format_decimal(daily_totals['total_fat'])
        }

        # 날짜 추가
        meal_totals_dict['date'] = date

        return Response(meal_totals_dict, status=status.HTTP_200_OK)

    
    def delete(self, request):
        # 모든 저장된 식단 데이터를 삭제
        deleted_count, _ = FoodIntake.objects.filter(user=request.user).delete()
        
        if deleted_count > 0:
            return Response({'message': '모든 식단 데이터가 성공적으로 삭제되었습니다.'}, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({'error': '삭제할 데이터가 없습니다.'}, status=status.HTTP_404_NOT_FOUND)
