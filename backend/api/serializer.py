from pathlib import Path
from rest_framework import serializers
from django.contrib.auth.models import User
from django.conf import settings
from backend.production import ALLOWED_HOSTS
from api.models import *

BASE_DIR = Path(__file__).resolve().parent.parent
PRODUCTION_DOMAIN = ALLOWED_HOSTS[0]

def get_image(data, property_reference:str, default_img:bool=False):
    if default_img:
        default_img = 'students_img.jpg'
    
    img = None
    if settings.DEBUG:
        if data[property_reference] and data[property_reference] != 'null':
            img = f"http://localhost:8000{data[property_reference]}"
        elif default_img:
            img = f"http://localhost:8000/static/images/{default_img}"
    else:
        if data[property_reference] and data[property_reference] != 'null':
            img = f"https://{PRODUCTION_DOMAIN}{data[property_reference]}"
        elif  default_img:  
            img = f"https://{PRODUCTION_DOMAIN}/static/images/{default_img}"
    
    return img


# Student Serializers
class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        exclude = ["user"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['img'] = get_image(data, 'img', True)

        return data


# Workshop Serializers
class WorkShopSerializer(serializers.ModelSerializer):

    class Meta:
        model = Workshop
        exclude = ["students", "created_at"]


class SuperuserWorkshopSerializer(serializers.ModelSerializer):
    students = serializers.SerializerMethodField()

    class Meta:
        model = Workshop
        fields = "__all__"

    def get_students(self, obj):
        return [{
            'name': x.user.get_full_name(),
            'school': x.school,
            'program': x.program,
            'current_year': x.current_year,
            'gender': x.gender,
            'phone_number': x.phone_number,
            'id': x.id,
            'email': x.user.email,
        } for x in obj.students.select_related("user").all()]

