import os

# Django
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings

# Django Restframework
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.mail import send_mail
from email.utils import formataddr
from django.db import transaction


# Other
from api.models import *
from api.serializer import *
from api.utils import use_pusher, valid_phone_number, valid_email
import random
from datetime import datetime

def root(request):
    return HttpResponse("<h1>Skillhub</h1>")


@api_view(['GET'])
def get_current_server_time(request):
    return Response({'timestamp': timezone.now().timestamp(), 'current_date': timezone.now().date()}, status=200)


@api_view(['POST'])
def refresh_server(request):
    print('Server refreshed')
    return Response(status=204)


# LOGIN
class UserAuthSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        
        return token


class UserAuthView(TokenObtainPairView):
    serializer_class = UserAuthSerializer
    
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        refresh_token = response.data.get('refresh')
        if refresh_token:
            response.set_cookie(
                key="refresh_token",
                value=refresh_token,
                httponly=True,
                expires = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
                secure=settings.DEBUG is False,
                samesite="Lax",
                path="/",
            )
            del response.data['refresh']

        return response


# Refresh Token
class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token is None:
            raise AuthenticationFailed("You have been logged out")

        request.data["refresh"] = refresh_token
        response = super().post(request, *args, **kwargs)
    
        if response.status_code == 200:
            new_refresh_token = response.data['refresh']
            response.set_cookie(
                key="refresh_token",
                value=new_refresh_token,
                httponly=True,
                secure=settings.DEBUG is False,
                samesite="Lax",
                path="/",
                expires = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            )
            del response.data['refresh']

        return response


# Logout
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_user(request):
    refresh_token = request.COOKIES.get('refresh_token')
    if not refresh_token:
        return Response({'message': 'Missing refresh token'}, status=401)
    
    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception as e:
        print(e)
        return Response({'message': 'Invalid refresh token'}, status=400)
    
    response = Response(status=200)
    response.delete_cookie("refresh_token", path="/")
    return response


# Students signup
@api_view(['POST'])
def student_signup(request):
    data = request.data
    first_name = data['firstName'].strip()
    last_name = data['lastName'].strip()
    email = data['email'].strip()
    password = data['password'].strip()
    school = data['school'].strip()
    program = data['program'].strip()
    current_year = int(data['currentYear'].strip())
    gender = data['gender'].strip()
    phone_number = data['phoneNumber'].strip()
    if not valid_email(email):
        return Response({'message': f"{email} is not a valid email. Check your email address"}, status=400)

    existing_user = User.objects.filter(email=email)
    if existing_user.exists():
        return Response({'message': f"The email address '{email}' already exists. Login if you already have an account"}, status=400)
    if not valid_phone_number(phone_number):
        return Response({"message": f"{phone_number} is not a valid phone number. Ensure you omit any leading zero (0) and include the country code instead. For example, use +233596021383 instead of 0596021383."}, status=400)
    user_no = random.randint(100, 999)
    username = f"{first_name.replace(' ', '')[0].upper()}{last_name.replace(' ', '').lower()}{user_no}"     
    
    with transaction.atomic():
        try:
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password,
            )
            Student.objects.create(
                user=user,
                school=school,
                program=program,
                current_year=current_year,
                gender=gender,
                phone_number=phone_number,
            )
            mail_sender = formataddr((os.environ.get("EMAIL_SENDER_NAME"), os.environ.get("EMAIL_SENDER_ADDRESS")))
            send_mail("Credential", f"Username: {username}", mail_sender, [email], fail_silently=False)
            return Response(status=204)
        except Exception:
            transaction.set_rollback(True)
            return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)


# User Data
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_data(request):
    user = request.user
    user_data = {
        'first_name': user.first_name,
        'last_name': user.last_name,
        'username': user.username,
        'last_login': user.last_login,
        'email': user.email,
    }
    current_year = timezone.now().year
    user_data['current_year_start_date'] = datetime(current_year, 1, 1).strftime("%Y-%m-%d")
    user_data['current_year_end_date'] = datetime(current_year, 12, 31).strftime("%Y-%m-%d")
    
    try:
        student = Student.objects.get(user=user)
        student_data = StudentSerializer(student).data
        user_data.update(student_data)
        user_data['role'] = 'student'

    except Student.DoesNotExist:
        user_data['role'] = 'superuser'

    except Exception as e:
        return Response("You don't have permission to access the system. Contact the IT administrator", status=401)
        
    user_data['ms'] = 'LOGIN SUCCESSFUL'
    return Response(user_data, status=200)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def superuser_data(request):
    if request.method == 'GET':
        workshops = SuperuserWorkshopSerializer(Workshop.objects.prefetch_related('students').all().order_by('-id'), many=True).data
        
        return Response({
            'workshops': workshops,
        }, status=200)

    elif request.method == 'POST':
        data = request.data
        if data['type'] == 'fetchMissedWorkShopRegistrations':
            workshops = SuperuserWorkshopSerializer(Workshop.objects.prefetch_related('students').filter(date__gt=timezone.now().date()), many=True).data
            return Response(workshops, status=200)

        if data['type'] == 'create':
            title = data['title']
            description = data['description']
            start_time = data['startTime']
            end_time = data['endTime']
            location = data['location']
            max_participants = int(data['maxParticipant'])
            date = data['date']
            deadline = data['deadline']

            with transaction.atomic():
                try:
                    workshop = Workshop.objects.create(
                        title=title,
                        description=description,
                        start_time=start_time,
                        end_time=end_time,
                        location=location,
                        max_participants=max_participants,
                        deadline=deadline,
                        date=date,
                    )
                    pusher = use_pusher()
                    pusher.trigger('workshop_creation_channel', 'new_workshop', WorkShopSerializer(workshop).data)
                    return Response(SuperuserWorkshopSerializer(workshop).data, status=200)

                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)

        workshop_id = int(data['workshopId'])
        workshop = Workshop.objects.get(id=workshop_id)
        if data['type'] == 'update_title':
            new_value = data['newValue']
            with transaction.atomic():
                try:
                    workshop.title = new_value
                    workshop.save()
                    pusher = use_pusher()
                    pusher.trigger('workshop_update_channel', 'update', {'id': workshop_id, 'update_type': 'title', 'new_value': new_value})
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)
                
        elif data['type'] == 'update_description':
            new_value = data['newValue']
            with transaction.atomic():
                try:
                    workshop.description = new_value
                    workshop.save()
                    pusher = use_pusher()
                    pusher.trigger('workshop_update_channel', 'update', {'id': workshop_id, 'update_type': 'description', 'new_value': new_value})
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)
                
        elif data['type'] == 'update_date':
            new_value = data['newValue']
            with transaction.atomic():
                try:
                    workshop.date = new_value
                    workshop.save()
                    pusher = use_pusher()
                    pusher.trigger('workshop_update_channel', 'update', {'id': workshop_id, 'update_type': 'date', 'new_value': new_value})
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)
                
        elif data['type'] == 'update_start_time':
            new_value = data['newValue']
            with transaction.atomic():
                try:
                    workshop.start_time = new_value
                    workshop.save()
                    pusher = use_pusher()
                    pusher.trigger('workshop_update_channel', 'update', {'id': workshop_id, 'update_type': 'start_time', 'new_value': new_value})
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)

        elif data['type'] == 'update_end_time':
            new_value = data['newValue']
            with transaction.atomic():
                try:
                    workshop.end_time = new_value
                    workshop.save()
                    pusher = use_pusher()
                    pusher.trigger('workshop_update_channel', 'update', {'id': workshop_id, 'update_type': 'end_time', 'new_value': new_value})
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)
                
        elif data['type'] == 'update_location':
            new_value = data['newValue']
            with transaction.atomic():
                try:
                    workshop.location = new_value
                    workshop.save()
                    pusher = use_pusher()
                    pusher.trigger('workshop_update_channel', 'update', {'id': workshop_id, 'update_type': 'location', 'new_value': new_value})
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)
                
        elif data['type'] == 'update_deadline':
            new_value = data['newValue']
            with transaction.atomic():
                try:
                    workshop.deadline = new_value
                    workshop.save()
                    pusher = use_pusher()
                    pusher.trigger('workshop_update_channel', 'update', {'id': workshop_id, 'update_type': 'deadline', 'new_value': new_value})
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)

        elif data['type'] == 'update_max_participants':
            new_value = int(data['newValue'])
            with transaction.atomic():
                try:
                    workshop.max_participants = new_value
                    workshop.save()
                    pusher = use_pusher()
                    pusher.trigger('workshop_update_channel', 'update', {'id': workshop_id, 'update_type': 'max_participants', 'new_value': new_value})
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)
        
        elif data['type'] == 'delete':
            with transaction.atomic():
                try:
                    workshop.delete()
                    pusher = use_pusher()
                    pusher.trigger('workshop_update_channel', 'update', {'id': workshop_id, 'update_type': 'delete', 'new_value': ''})
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)


@api_view(['POST', 'GET'])
@permission_classes([IsAuthenticated])
def student_data(request):
    if request.method == 'GET':
        student = Student.objects.get(user=request.user)
        workshops_data = []
        workshops = Workshop.objects.prefetch_related('students').all()
        for _workshop_ in workshops:
            workshop_students = _workshop_.students.all()
            data = WorkShopSerializer(_workshop_).data
            if student in workshop_students:
                data = data | {'registered': True}
                workshops_data.append(data)
            else:
                data = data | {'registered': False}
                workshops_data.append(data)
        
        return Response({
            'workshops': workshops_data,
        }, status=200)

    elif request.method == 'POST':
        data = request.data
        student = Student.objects.select_related('user').get(user=request.user)
        if data['type'] == 'fetchMissedWorkShopUpdates':
            workshops_data = []
            workshops = Workshop.objects.prefetch_related('students').all()
            for _workshop_ in workshops:
                workshop_students = _workshop_.students.all()
                data = WorkShopSerializer(_workshop_).data
                if student in workshop_students:
                    data = data | {'registered': True}
                    workshops_data.append(data)
                else:
                    data = data | {'registered': False}
                    workshops_data.append(data)

            return Response(workshops_data, status=200)
        
        workshop_id = int(data['workshopId'])
        workshop = Workshop.objects.prefetch_related('students').get(id=workshop_id)
  
        if data['type'] == 'register':
            if workshop.deadline < timezone.now().date():
                return Response({'message': "The deadline for registration for this workshop has passed"}, status=400)
            if workshop.max_participants <= workshop.students.count():
                return Response({'message': "This workshop is already full."}, status=400)
            with transaction.atomic():
                try:
                    workshop.students.add(student)
                    student_data = {
                        'name': student.user.get_full_name(),
                        'school': student.school,
                        'program': student.program,
                        'current_year': student.current_year,
                        'gender': student.gender,
                        'phone_number': student.phone_number,
                        'id': student.id,
                        'email': student.user.email,
                    }
                    pusher = use_pusher()
                    pusher.trigger(f'workshop_{workshop_id}_registration_channel', 'new_registration', student_data)
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)
        
        elif data['type'] == 'cancel':
            if workshop.date < timezone.now().date():
                return Response({'message': "The date for this workshop has passed"}, status=400)
            with transaction.atomic():
                try:
                    workshop.students.remove(student)
                    pusher = use_pusher()
                    pusher.trigger(f'workshop_{workshop_id}_registration_channel', 'cancel_registration', student.id)
                    return Response(status=204)
                except Exception:
                    transaction.set_rollback(True)
                    return Response({'message': 'A network error occured, check your internet connection and try again'}, status=400)
