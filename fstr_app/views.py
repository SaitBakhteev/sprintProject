from rest_framework import generics, status
from rest_framework.response import Response
from .models import PerevalAdded
from .serializers import PerevalAddedSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample


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
                    {"data": "<картинка1>", "title": "Седловина"},
                    {"data": "<картинка>", "title": "Подъём"}
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
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)