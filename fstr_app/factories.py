from factory.django import DjangoModelFactory
from factory import SubFactory

from .models import User, Coords, PerevalAdded


''' Это "фабрики" для создания тестовых объектов с помощью наследования от DjangoModelFactory.
Для связывания объектов (внешние ключи) используем SubFactory '''

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    email = "test@example.com"
    first_name = "Иван"
    last_name = "Сидоров"
    middle_name = "Петрович"
    phone_number = "+79112345678"


class CoordsFactory(DjangoModelFactory):
    class Meta:
        model = Coords
    latitude = 45.3842
    longitude = 7.1525
    height = 1200


class PerevalAddedFactory(DjangoModelFactory):
    class Meta:
        model = PerevalAdded

    beautyTitle = "Test Pass"
    title = "Test Pass Title"
    status = "new"
    user = SubFactory(UserFactory)  # Автоматически создаст User
    coords = SubFactory(CoordsFactory)  # Автоматически создаст Coords
