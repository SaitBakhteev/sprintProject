from rest_framework import generics, status, serializers
from rest_framework.response import Response
from .models import PerevalAdded
from .serializers import PerevalAddedSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample

import base64
import os
from django.conf import settings


# Функция-заглушка для преобразования образца картинки в строку base64
def image_to_base64():
    # Путь к файлу в корне проекта
    file_path = os.path.join(settings.BASE_DIR, 'image.jpg')  # загрузка картинки заглушки

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
                    {"data": f"data:image/jpeg;base64,{image_to_base64()}", "title": "Седловина"},
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