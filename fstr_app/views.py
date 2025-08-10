from rest_framework import generics, status, serializers
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import PerevalAdded
from .serializers import PerevalAddedSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample

import base64
import os
from django.conf import settings


# Функция-заглушка для преобразования образца картинки в строку base64
def image_to_base64(filename: str):
    # Путь к файлу в корне проекта
    file_path = os.path.join(settings.BASE_DIR, filename)  # загрузка картинки заглушки

    try:
        with open(file_path, 'rb') as image_file:
            # Читаем файл и кодируем в base64
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
    except FileNotFoundError:
        return "Ошибка: файл example.jpg не найден в корне проекта"
    except Exception as e:
        return f"Ошибка при обработке файла: {str(e)}"


@extend_schema(
    summary="Добавить новый перевал",
    description="Создает новую запись о перевале в базе данных",
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                "beauty_title": "пер. ",
                "title": "Пхия",
                "other_titles": "Триев",
                "connect": "",
                "add_time": "2021-09-22 13:18:13",
                "user": {
                    "email": "qwerty@mail.ru",
                    "fam": "Пупкин",
                    "name": "Василий",
                    "otc": "Иванович",
                    "phone": "+7 555 55 55"
                },
                "coords": {
                    "latitude": "45.3842",
                    "longitude": "7.1525",
                    "height": "1200"
                },
                "level": {
                    "winter": "",
                    "summer": "1А",
                    "autumn": "1А",
                    "spring": ""
                },
                "images": [
                    {"data": f"data:image/jpeg;base64,{image_to_base64('image.jpg')}", "title": "Седловина"},
                    # {"data": f"data:image/jpeg;base64,{image_to_base64()}", "title": "Подъём"}
                ]
            },
            request_only=True
        )
    ]
)
class PerevalCreateView(generics.CreateAPIView):
    queryset = PerevalAdded.objects.all()
    serializer_class = PerevalAddedSerializer

    def create(self, request, *args, **kwargs):
        try:
            # Преобразуем входные данные в формат, ожидаемый сериализатором
            data = request.data.copy()
            data['beautyTitle'] = data.pop('beauty_title', '')

            # Обрабатываем уровень сложности
            level_data = data.pop('level', {})
            data['winter_level'] = level_data.get('winter', '')
            data['summer_level'] = level_data.get('summer', '')
            data['autumn_level'] = level_data.get('autumn', '')
            data['spring_level'] = level_data.get('spring', '')

            # Обрабатываем пользователя
            user_data = data.pop('user', {})
            data['user'] = {
                'email': user_data.get('email', ''),
                'first_name': user_data.get('name', ''),
                'last_name': user_data.get('fam', ''),
                'middle_name': user_data.get('otc', ''),
                'phone': user_data.get('phone', '')
            }

            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(
                data={
                    'status': status.HTTP_200_OK,
                    'message': 'Отправлено успешно',
                    'id': serializer.instance.id  # id созданной записи перевала
                },
                status=status.HTTP_200_OK,
                headers={'Content-Type': 'application/json'})
        except serializers.ValidationError as e:
            return Response(
                data={'status': status.HTTP_400_BAD_REQUEST,
                      'message': str(e.detail),
                      'id': None},
                status=status.HTTP_400_BAD_REQUEST,
                content_type='application/json'
            )
        except Exception as e:
            return Response(
                data={'status': status.HTTP_500_INTERNAL_SERVER_ERROR,
                      'message': f'Ошибка при выполнении операции: {str(e)}',
                      'id': None},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content_type='application/json'
            )


@extend_schema(description='Получение данных перевала по ID (включая статус модерации).')
class PerevalDetailView(generics.RetrieveAPIView):
    queryset = PerevalAdded.objects.all()
    serializer_class = PerevalAddedSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


@extend_schema(
    methods=['PATCH'],
    summary="Редактировать перевал",
    description="Редактирует данные о перевале, но без изменения данных пользователя",
    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                "beauty_title": "тракт ",
                "title": "Чуйский",
                "other_titles": "Алтайские перевалы",
                "connect": "",
                "add_time": "2021-09-22 13:18:13",
                "coords": {
                    "latitude": "52.2142",
                    "longitude": "82.48525",
                    "height": "850"
                },
                "level": {
                    "winter": "3B",
                    "summer": "2C",
                    "autumn": "1D",
                    "spring": ""
                },
                "images": [
                    # Меняем картинку на вторую заглушку
                    {"data": f"data:image/jpeg;base64,{image_to_base64('image2.jpg')}", "title": "Дорога у перевала"},
                    # {"data": f"data:image/jpeg;base64,{image_to_base64()}", "title": "Подъём"}
                ]
            },
            request_only=True
        )
    ]
)
class PerevalUpdateView(generics.UpdateAPIView):
    queryset = PerevalAdded.objects.all()
    serializer_class = PerevalAddedSerializer
    http_method_names = ['patch']  # Разрешаем только PATCH

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()

        try:
            # Преобразуем входные данные как в create
            data = request.data.copy()
            data['beautyTitle'] = data.pop('beauty_title', instance.beautyTitle)

            level_data = data.pop('level', {})
            data['winter_level'] = level_data.get('winter', instance.winter_level)
            data['summer_level'] = level_data.get('summer', instance.summer_level)
            data['autumn_level'] = level_data.get('autumn', instance.autumn_level)
            data['spring_level'] = level_data.get('spring', instance.spring_level)

            # Исключаем возможность изменения пользователя
            if 'user' in data:
                del data['user']

            serializer = self.get_serializer(
                instance,
                data=data,
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            return Response({
                'state': 1,
                'message': 'Запись успешно обновлена'
            })
        except serializers.ValidationError as e:
            return Response({
                'state': 0,
                'message': str(e.detail)
            }, status=400)
        except Exception as e:
            return Response({
                'state': 0,
                'message': f'Ошибка при обновлении: {str(e)}'
            }, status=500)


class PerevalUserListView(generics.ListAPIView):
    serializer_class = PerevalAddedSerializer

    def get_queryset(self):
        email = self.request.GET.get('user__email', None)
        if email:
            return PerevalAdded.objects.filter(user__email=email)
        return PerevalAdded.objects.none()