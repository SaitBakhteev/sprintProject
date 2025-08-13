from factory.django import DjangoModelFactory
from factory import SubFactory

from .models import User, Coords, PerevalAdded, PerevalImage, PerevalAddedImage
from .views import image_to_base64

from base64 import b64decode


''' Это "фабрики" для создания тестовых объектов с помощью наследования от DjangoModelFactory.
Для связывания объектов (внешние ключи) используем SubFactory '''

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User
    email = "test@example.com"
    first_name = "Иван"
    last_name = "Сидоров"
    middle_name = "Петрович"
    phone = "+79112345678"


class CoordsFactory(DjangoModelFactory):
    class Meta:
        model = Coords
    latitude = 45.3842
    longitude = 7.1515
    height = 1200


class PerevalAddedFactory(DjangoModelFactory):
    class Meta:
        model = PerevalAdded

    beautyTitle = "пер."
    title = "Чуйский тракт"
    other_titles = "Вьючная тропа"
    status = "new"
    user = SubFactory(UserFactory)  # Автоматически создаст User
    coords = SubFactory(CoordsFactory)  # Автоматически создаст Coords


class PerevalImageFactory(DjangoModelFactory):
    class Meta:
        model = PerevalImage
    title = "Дорога у перевала"

    # Открываем заглушку image.jpg как base64-строку и преобразуем в байты
    img = b64decode(image_to_base64('image.jpg'))


class PerevalAddedImageFactory(DjangoModelFactory):
    class Meta:
        model = PerevalAddedImage

    pereval = SubFactory(PerevalAddedFactory)
    image = SubFactory(PerevalImageFactory)