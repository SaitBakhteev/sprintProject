import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import User, Coords, PerevalAdded, PerevalImage
from .serializers import PerevalAddedSerializer


@pytest.mark.django_db
class TestModels:
    def test_user_creation(self):
        user = User.objects.create(
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            phone="+1234567890"
        )
        assert user.email == "test@example.com"
        assert str(user) == "John Doe"

    def test_coords_creation(self):
        coords = Coords.objects.create(
            latitude=45.3842,
            longitude=7.1525,
            height=1200
        )
        assert coords.latitude == 45.3842
        assert str(coords) == "45.3842, 7.1525, 1200m"

    def test_pereval_creation(self, user_factory, coords_factory):
        user = user_factory()
        coords = coords_factory()
        pereval = PerevalAdded.objects.create(
            beautyTitle="Test Pass",
            title="Test Pass Title",
            coords=coords,
            user=user,
            status="new"
        )
        assert pereval.beautyTitle == "Test Pass"
        assert pereval.status == "new"
        assert str(pereval) == "Test Pass Title"


class TestSerializers(APITestCase):
    def setUp(self):
        self.user_data = {
            "email": "test@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "phone": "+1234567890"
        }
        self.coords_data = {
            "latitude": 45.3842,
            "longitude": 7.1525,
            "height": 1200
        }
        self.image_data = {
            "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
            "title": "Test Image"
        }
        self.pereval_data = {
            "beautyTitle": "Test Pass",
            "title": "Test Pass Title",
            "other_titles": "Alternative Name",
            "connect": "",
            "coords": self.coords_data,
            "user": self.user_data,
            "images": [self.image_data],
            "winter_level": "",
            "summer_level": "1A",
            "autumn_level": "",
            "spring_level": ""
        }

    def test_pereval_serializer(self):
        serializer = PerevalAddedSerializer(data=self.pereval_data)
        assert serializer.is_valid(), serializer.errors
        pereval = serializer.save()
        assert pereval.title == "Test Pass Title"
        assert pereval.user.email == "test@example.com"
        assert pereval.coords.latitude == 45.3842
        assert pereval.pereval_images.count() == 1

    def test_pereval_serializer_update(self):
        # Create initial data
        serializer = PerevalAddedSerializer(data=self.pereval_data)
        serializer.is_valid()
        pereval = serializer.save()

        # Update data
        update_data = {
            "title": "Updated Title",
            "coords": {
                "latitude": 46.0,
                "longitude": 8.0,
                "height": 1500
            },
            "images": [
                {
                    "id": pereval.pereval_images.first().id,
                    "title": "Updated Image Title"
                },
                {
                    "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
                    "title": "New Image"
                }
            ]
        }

        updated = PerevalAddedSerializer(instance=pereval, data=update_data, partial=True)
        assert updated.is_valid(), updated.errors
        updated_instance = updated.save()
        assert updated_instance.title == "Updated Title"
        assert updated_instance.coords.latitude == 46.0
        assert updated_instance.pereval_images.count() == 2


class TestAPI(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "test@example.com",
            "fam": "Doe",
            "name": "John",
            "otc": "Smith",
            "phone": "+1234567890"
        }
        self.coords_data = {
            "latitude": "45.3842",
            "longitude": "7.1525",
            "height": "1200"
        }
        self.level_data = {
            "winter": "",
            "summer": "1A",
            "autumn": "",
            "spring": ""
        }
        self.image_data = {
            "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
            "title": "Test Image"
        }
        self.pereval_data = {
            "beautyTitle": "Test Pass",
            "title": "Test Pass Title",
            "other_titles": "Alternative Name",
            "connect": "",
            "coords": self.coords_data,
            "user": self.user_data,
            "level": self.level_data,
            "images": [self.image_data]
        }

    def test_create_pereval(self):
        url = reverse('submitData')
        response = self.client.post(url, self.pereval_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], status.HTTP_200_OK)
        self.assertIsNotNone(response.data['id'])

        # Verify data was created correctly
        pereval = PerevalAdded.objects.get(pk=response.data['id'])
        self.assertEqual(pereval.title, "Test Pass Title")
        self.assertEqual(pereval.user.email, "test@example.com")
        self.assertEqual(pereval.coords.latitude, 45.3842)
        self.assertEqual(pereval.pereval_images.count(), 1)

    def test_get_pereval(self):
        # First create a pereval
        create_response = self.client.post(reverse('submitData'), self.pereval_data, format='json')
        pereval_id = create_response.data['id']

        # Then retrieve it
        url = reverse('pereval-detail', kwargs={'pk': pereval_id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "Test Pass Title")
        self.assertEqual(response.data['user']['email'], "test@example.com")

    def test_update_pereval(self):
        # First create a pereval
        create_response = self.client.post(reverse('submitData'), self.pereval_data, format='json')
        pereval_id = create_response.data['id']

        # Prepare update data
        update_data = {
            "title": "Updated Title",
            "coords": {
                "latitude": "46.0",
                "longitude": "8.0",
                "height": "1500"
            },
            "images": [
                {
                    "id": PerevalAdded.objects.get(pk=pereval_id).pereval_images.first().id,
                    "title": "Updated Image Title"
                },
                {
                    "data": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==",
                    "title": "New Image"
                }
            ]
        }

        # Send PATCH request
        url = reverse('pereval-update', kwargs={'pk': pereval_id})
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['state'], 1)

        # Verify updates
        pereval = PerevalAdded.objects.get(pk=pereval_id)
        self.assertEqual(pereval.title, "Updated Title")
        self.assertEqual(pereval.coords.latitude, 46.0)
        self.assertEqual(pereval.pereval_images.count(), 2)

    def test_update_rejected_pereval(self):
        # First create a pereval
        create_response = self.client.post(reverse('submitData'), self.pereval_data, format='json')
        pereval_id = create_response.data['id']

        # Change status to rejected
        pereval = PerevalAdded.objects.get(pk=pereval_id)
        pereval.status = 'rejected'
        pereval.save()

        # Try to update
        update_data = {"title": "Should Fail"}
        url = reverse('pereval-update', kwargs={'pk': pereval_id})
        response = self.client.patch(url, update_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['state'], 0)

    def test_get_pereval_by_email(self):
        # First create a pereval
        self.client.post(reverse('submitData'), self.pereval_data, format='json')

        # Get by email
        url = reverse('submitData') + f"?user__email={self.user_data['email']}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user']['email'], self.user_data['email'])

    def test_invalid_image_data(self):
        invalid_data = self.pereval_data.copy()
        invalid_data['images'] = [{"data": "invalid", "title": "Bad Image"}]

        url = reverse('submitData')
        response = self.client.post(url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], status.HTTP_400_BAD_REQUEST)


@pytest.mark.django_db
class TestEdgeCases:
    def test_user_email_unique(self):
        User.objects.create(email="test@example.com", first_name="John", last_name="Doe", phone="+1234567890")
        with pytest.raises(Exception):
            User.objects.create(email="test@example.com", first_name="Jane", last_name="Doe", phone="+9876543210")

    def test_pereval_status_choices(self):
        user = User.objects.create(email="test@example.com")
        coords = Coords.objects.create(latitude=45.0, longitude=7.0, height=1000)

        with pytest.raises(Exception):
            PerevalAdded.objects.create(
                beautyTitle="Test",
                title="Test",
                user=user,
                coords=coords,
                status="invalid_status"
            )

    def test_pereval_without_required_fields(self):
        with pytest.raises(Exception):
            PerevalAdded.objects.create(
                beautyTitle="Test",
                title="Test"
                # Missing required fields: user, coords
            )