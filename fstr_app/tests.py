import logging

import pytest
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import  APIClient, APITestCase

from .models import PerevalAdded
from .views import image_to_base64
from .serializers import PerevalAddedSerializer
from .factories import UserFactory, CoordsFactory, PerevalAddedFactory, PerevalImageFactory, PerevalAddedImageFactory


# Класс для создания симуляционных объектов User

@pytest.mark.django_db
def test_pereval_creation():
    pereval = PerevalAddedFactory()
    assert str(pereval) == "пер., Чуйский тракт, Вьючная тропа"
    assert str(pereval.user) == 'Иван, Сидоров, test@example.com'
    assert str(pereval.coords) == "45.3842, 7.1515, 1200"

    # Проверяем связь многие-ко-многим
    pereval_image = PerevalAddedImageFactory(pereval=pereval)
    assert pereval_image.pereval == pereval
    assert bytes(pereval_image.image.img)[10:20] == b'\x00\x01\x01\x01\x00H\x00H\x00\x00'

#
class TestSerializers(TestCase):
    def setUp(self):
        # Создаем объекты через фабрики
        self.user = UserFactory()
        self.coords = CoordsFactory()
        self.pereval = PerevalAddedFactory(user=self.user, coords=self.coords)
        self.image = PerevalImageFactory()
        self.pereval.pereval_images.add(self.image)

        # Подготовка данных для сериализатора
        self.pereval_data = {
            "beautyTitle": self.pereval.beautyTitle,
            "title": self.pereval.title,
            "other_titles": self.pereval.other_titles,
            "connect": self.pereval.connect,
            "coords": {
                "latitude": self.coords.latitude,
                "longitude": self.coords.longitude,
                "height": self.coords.height
            },
            "user": {
                "email": self.user.email,
                "first_name": self.user.first_name,
                "last_name": self.user.last_name,
                "middle_name": self.user.middle_name,
                "phone": self.user.phone
            },
            "images": [{
                # Новая картинка в виде строки base64
                "data": f"data:image/png;base64,...",  # передаем картинку как строку base64
                "title": self.image.title
            }],
            "winter_level": self.pereval.winter_level,
            "summer_level": self.pereval.summer_level,
            "autumn_level": self.pereval.autumn_level,
            "spring_level": self.pereval.spring_level
        }

    def test_pereval_serializer(self):
        serializer = PerevalAddedSerializer(data=self.pereval_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        pereval = serializer.save()
        self.assertEqual(pereval.title, self.pereval.title)
        self.assertEqual(pereval.user.email, self.user.email)
        self.assertEqual(pereval.coords.latitude, self.coords.latitude)
        self.assertEqual(pereval.pereval_images.count(), 1)

    def test_pereval_serializer_update(self):
        # Создаем новые данные через фабрики для обновления
        new_coords = CoordsFactory()
        new_image = PerevalImageFactory()

        update_data = {
            "title": "Updated Title",
            "coords": {
                "latitude": new_coords.latitude,
                "longitude": new_coords.longitude,
                "height": new_coords.height
            },
            "images": [
                {
                    "id": self.image.id,
                    "title": "Updated Image Title"
                },
                {
                    "data": f"data:image/png;base64,...",
                    "title": new_image.title
                }
            ]
        }

        serializer = PerevalAddedSerializer(instance=self.pereval, data=update_data, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        updated_instance = serializer.save()

        self.assertEqual(updated_instance.title, "Updated Title")
        self.assertEqual(updated_instance.coords.latitude, new_coords.latitude)
        self.assertEqual(updated_instance.pereval_images.count(), 2)
#
#
class TestAPI(APITestCase):
    def setUp(self):
        self.client = APIClient()

        ''' Мы не используем PerevalAddedFactory, поскольку будет дублирование объекта при
        тестировании post-запроса на создание перевала '''

        self.user = UserFactory()
        self.coords = CoordsFactory()

        self.user_data = {
            "email": "test@api.com",  # здесь специально сделал замену для проверки
            "fam": self.user.last_name,
            "name": self.user.first_name,
            "otc": self.user.middle_name,
            "phone": self.user.phone
        }
        self.coords_data = {
            "latitude": self.coords.latitude,
            "longitude": self.coords.longitude,
            "height": self.coords.height,
        }
        self.level_data = {
            "winter": "",
            "summer": "1A",
            "autumn": "",
            "spring": ""
        }
        self.image_data = {
            "data": f"data:image/png;base64,{image_to_base64('image.jpg')}",
            "title": "Test Image"
        }
        self.pereval_data = {
            "beautyTitle": "пер.",
            "title": "Апишный тракт",
            "other_titles": "Вьючная API",
            "connect": "",
            "coords": self.coords_data,
            "user": self.user_data,
            "level": self.level_data,
            "images": [self.image_data]
        }

        # Делаем запрос на создание тестового объекта перевала
        self.create_response = self.client.post(reverse('submitData'), self.pereval_data, format='json')
        self.pk = self.create_response.data['id']

    def test_create_pereval(self):
        self.assertEqual(self.create_response.status_code, status.HTTP_200_OK)
        self.assertEqual(self.create_response.data['status'], status.HTTP_200_OK)
        self.assertIsNotNone(self.pk)

        # Проверяем только-что созданный тестовый объект перевала
        pereval = PerevalAdded.objects.get(pk=self.pk)
        self.assertEqual(pereval.title, "Апишный тракт")
        self.assertEqual(pereval.other_titles, "Вьючная API")
        self.assertEqual(pereval.user.email, "test@api.com")
        self.assertEqual(pereval.coords.latitude, 45.3842)
        self.assertEqual(pereval.pereval_images.count(), 1)

    def test_get_pereval(self):
        url = reverse('pereval-detail', kwargs={'pk': self.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Апишный тракт")
        self.assertEqual(response.data['user']['email'], "test@api.com")

    def test_update_pereval(self):
        # Готовим данные для обновления
        update_data = {
            "title": "Updated Title",
            "coords": {
                "latitude": "46.0",
                "longitude": "8.0",
                "height": "1500"
            },
            "images": [
                {
                    "id": PerevalAdded.objects.get(pk=self.pk).pereval_images.first().id,
                    "title": "Updated Image Title"
                },
                {
                    # Добавляем вторую картинку в ранее созданный тестовый объект перевала в виде условной base64-строки
                    "data": f"data:image/png;base64,/9j/4AAQSkZJRgABAQAA...",
                    "title": "New Image"
                }
            ]
        }

        # Посылаем PATCH запрос
        url = reverse('pereval-update', kwargs={'pk': self.pk})
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 1)
#
#         # Проверяем данные после обновления
        pereval = PerevalAdded.objects.get(pk=self.pk)
        images = pereval.pereval_images.all()  # получаем изображения нашего тестового перевала
        self.assertEqual(pereval.title, "Updated Title")
        self.assertEqual(pereval.coords.latitude, 46.0)
        self.assertEqual(pereval.pereval_images.count(), 2)
        self.assertEqual(images[0].title, "Updated Image Title")
        self.assertEqual(images[1].title, "New Image")

        # Проверка байтов второго изображения
        self.assertEqual(bytes(images[1].img),  b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00')

    def test_update_rejected_pereval(self):
#         # Меняем статуc модерации на rejected
        pereval = PerevalAdded.objects.get(pk=self.pk)
        pereval.status = 'rejected'
        pereval.save()

        update_data = {"title": "Should Fail"}
        url = reverse('pereval-update', kwargs={'pk': self.pk})
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['state'], 0)
#
    def test_get_pereval_by_email(self):
        url = reverse('submitData') + f"?user__email={self.user_data['email']}"
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user']['email'], self.user_data['email'])
        self.assertEqual(response.data[0]['other_titles'], "Вьючная API")
#
    def test_invalid_image_data(self):
        invalid_data = self.pereval_data.copy()
        invalid_data['images'] = [{"data": "invalid", "title": "Bad Image"}]

        url = reverse('submitData')
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], status.HTTP_400_BAD_REQUEST)
