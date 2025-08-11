from rest_framework import generics, status, serializers
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import PerevalAdded, User
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
                "beautyTitle": "пер. ",
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
            data['beautyTitle'] = data.pop('beautyTitle', '')

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
    description="""Если не хотите менять поле, то не передавайте его в JSON.   
                **Данные пользователя в JSON не передавать!**   
                ***Один из словарей списка `images` содержит пример заглушки (`data:image/jpeg;base64...`). 
                В реальном запросе используйте ваши base64-данные изображений.***""",

    examples=[
        OpenApiExample(
            'Пример запроса',
            value={
                "beautyTitle": "",
                "title": "",
                "other_titles": "",
                "winter_level": "",
                "summer_level": "",
                "autumn_level": "",
                "spring_level": "",

                # "user": {'email': ""},  # если вдруг потребуется передача данных пользователя

                # Поля через взаимосвязанные модели
                "coords": {
                    "latitude": "",
                    "longitude": "",
                    "height": ""
                },
                "images": [
                    # если старое фото остается, то передаем его id
                    {"id": "<Здесь указываете id старого фото, которое не должно удаляться>"},

                    # Пример второй картинки-заглушки для добавления нового фото
                    {"data": f"data:image/jpeg;base64,{image_to_base64('image2.jpg')}", "title": "Дорога у перевала"},
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
            # if instance.user != self.request.user:

            # Преобразуем входные данные как в create
            data = request.data.copy()
            # data['beautyTitle'] = data.pop('beautyTitle', instance.beautyTitle)

            # level_data = data.pop('level', {})
            # data['winter_level'] = level_data.get('winter', instance.winter_level)
            # data['summer_level'] = level_data.get('summer', instance.summer_level)
            # data['autumn_level'] = level_data.get('autumn', instance.autumn_level)
            # data['spring_level'] = level_data.get('spring', instance.spring_level)

            ''' Здесь заготовка, если потребуется на уровне API контролировать, чтобы пользователи могли
              редактировать только свои перевалы. В этом случае в теле запроса ожидаем email пользователя '''
            # if not 'user' in data or not 'email' in data['user']:
            #     raise serializers.ValidationError('В тело запроса не передан email пользователя')
            # email = data['user'].get('email', '')
            #
            # if len(email) > 0:
            #     user = User.objects.get(email=email)
            #
            # else:
            #     raise serializers.ValidationError('В ключ email передано пустое значение')
            # print(f"email: {email}\n"
            #       f"user_email: {user.email}")
            # if instance.user_id != user.id:  # если пользователь пытается редактировать чужой перевал
            #     raise serializers.ValidationError('Нельзя редактировать данные перевалов, '
            #                                       'добавленные другими пользователями')

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