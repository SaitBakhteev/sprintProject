from rest_framework import serializers
from .models import User, Coords, PerevalAdded, PerevalImage, PerevalAddedImage

import base64
from django.core.files.base import ContentFile


def decode_base64_image(data):
    if isinstance(data, str) and data.startswith('data:image'):
        # format: data:image/png;base64,XXXX
        header, data = data.split(';base64,')
        try:
            decoded_data = base64.b64decode(data)
            return ContentFile(decoded_data, 'upload.png')
        except TypeError:
            return None
    return None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'middle_name', 'phone']


class CoordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coords
        fields = ['latitude', 'longitude', 'height']


class ImageSerializer(serializers.ModelSerializer):
    data = serializers.CharField(write_only=True)

    class Meta:
        model = PerevalImage
        fields = ['data']

    def validate_data(self, value):
        decoded_data = decode_base64_image(value)
        if not decoded_data:
            raise serializers.ValidationError("Некорректный формат изображения")
        return decoded_data

    def create(self, validated_data):
        # Достаём данные
        image_data = validated_data.pop('data')  # присваиваем с ключа 'data'
        title = validated_data.pop('title')

        # Создаём объект изображения

        ''' Присваиваем полю "img" значения ключа, поскольку согласно ТЗ в эндпоинт из тела
         запроса передается ключ "data" '''
        return PerevalImage.objects.create(
            img=image_data,
            title=title
        )

class PerevalAddedSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    coords = CoordsSerializer()
    images = ImageSerializer(many=True)

    class Meta:
        model = PerevalAdded
        fields = ['beautyTitle', 'title', 'other_titles', 'connect', 'add_time',
                  'user', 'coords', 'winter_level', 'summer_level',
                  'autumn_level', 'spring_level', 'images']

    def create(self, validated_data):
        # Обработка пользователя
        user_data = validated_data.pop('user')
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'middle_name': user_data.get('middle_name', ''),
                'phone': user_data.get('phone', '')
            }
        )

        # Обработка координат
        coords_data = validated_data.pop('coords')
        coords = Coords.objects.create(**coords_data)

        # Обработка изображений
        images_data = validated_data.pop('images', [])

        # Создание перевала
        pereval = PerevalAdded.objects.create(
            user=user,
            coords=coords,
            **validated_data
        )

        # Добавление изображений
        for image_data in images_data:
            img = PerevalImage.objects.create(
                img=image_data['data'],
                title=image_data['title']
            )
            PerevalAddedImage.objects.create(
                pereval=pereval,
                image=img
            )

        return pereval