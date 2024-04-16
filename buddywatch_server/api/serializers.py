from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import Video


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password']
        extra_kwargs = {
            'username': {
                'validators': [
                    UniqueValidator(
                        queryset=User.objects.all()
                    ),
                ],
                'required': True
            },
            'password': {
                'write_only': True,
                'style': {'input_type': 'password'},
                'required': True

            }
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ['title', 'file', 'created_at', 'owner']
        extra_kwargs = {'owner': {'read_only': True}}
