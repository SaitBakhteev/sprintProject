import binascii

from django.db import transaction

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

        # Здесь отключаем валидатор уникальности email
        extra_kwargs = {'email': {'validators': []}}


class CoordsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coords
        fields = ['latitude', 'longitude', 'height']


class ImageSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)  # необязательное поле, нужно только при редактировании картинок
    data = serializers.CharField(write_only=True)

    class Meta:
        model = PerevalImage
        fields = ['id', 'data', 'title']

    def validate_data(self, value):
        # Удаляем префикс data:image/...;base64, если есть
        if isinstance(value, str) and value.startswith('data:image'):
            _, value = value.split(';base64,')

        try:
            return base64.b64decode(value)  # Декодируем в байты
        except (TypeError, binascii.Error):
            raise serializers.ValidationError("Некорректный формат Base64")

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
    images = ImageSerializer(many=True, source='pereval_images')

    class Meta:
        model = PerevalAdded
        fields = ['beautyTitle', 'title', 'other_titles', 'connect',
                  'add_time', 'user', 'coords', 'winter_level', 'summer_level',
                  'autumn_level', 'spring_level', 'images', 'status']

    def create(self, validated_data):
        # Обработка пользователя
        user_data = validated_data.pop('user')
        if User.objects.filter(email=user_data.get('email')).exists():
            user = User.objects.get(email=user_data.get('email'))

            # Если у пользователя поменялись какие-либо поля, то обновляем его
            has_changes = any(
                getattr(user, field) != value
                for field, value in user_data.items()
            )
            if has_changes:
                print('есть замена')
                for field, value in user_data.items():
                    setattr(user, field, value)
                user.save()
        else:  # если пользователя с таким email нет, то создаем его
            user = User.objects.create(
                email=user_data['email'],
                first_name=user_data.get('first_name', ''),
                last_name=user_data.get('last_name', ''),
                middle_name=user_data.get('middle_name', ''),
                phone=user_data.get('phone', ''),
            )

        # Обработка координат
        coords_data = validated_data.pop('coords')
        coords = Coords.objects.create(**coords_data)

        # Обработка изображений
        images_data = validated_data.pop('pereval_images', [])

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

    def update(self, instance, validated_data):
        with transaction.atomic():

            if instance.status != 'new':
                raise serializers.ValidationError("Редактирование запрещено. Поменялся статус записи")

            # Обработка координат
            if 'coords' in validated_data:
                self.fields['coords'].update(instance.coords, validated_data.pop('coords'))

            # Обработка изображений
            if 'pereval_images' in validated_data:
                images_data = validated_data.pop('pereval_images')
                images_to_keep = []

                for img_data in images_data:
                    print(img_data)
                    if 'id' in img_data:  # Существующее изображение
                        img = PerevalImage.objects.get(id=img_data['id'])
                        if 'title' in img_data:
                            img.title = img_data['title']
                        img.save()
                        images_to_keep.append(img)
                    else:  # Новое изображение
                        if 'data' not in img_data:
                            raise serializers.ValidationError("Для нового изображения обязательно поле 'data'")
                        img = PerevalImage.objects.create(
                            img=img_data['data'],
                            title=img_data['title']
                        )
                        images_to_keep.append(img)

                # Обновляем связи перевала с изображениями
                instance.pereval_images.set(images_to_keep)

                # Удаляем отвязанные изображения
                PerevalImage.objects.filter(perevaladdedimage__isnull=True).delete()

            # Обновляем остальные поля
            for attr, value in validated_data.items():
                setattr(instance, attr, value)

            instance.save()
            return instance
