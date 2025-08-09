from django.db import models


class User(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)

    class Meta:
        db_table = 'users'


''' Таблица с Названиями больших районов, горных систем (например, Альпы и т.п.) и т.п., выстроенная по иерархии.
Например, 1-я запись с полями: id=1, id_parent=0, title = "Земля". 
2-я запись с полями: id=2, id_parent=1 (условная ссылка на планету Земля ), title = "Анды".
3-я запись с полями: id=3, id_parent=2 (условная ссылка на Анды ), title = "Мачу Пикчу".
.... и т.д. и т.п. '''

class PerevalArea(models.Model):
    id_parent = models.BigIntegerField()
    title = models.TextField()

    class Meta:
        db_table = 'pereval_areas'


class Coords(models.Model):
    latitude = models.FloatField()
    longitude = models.FloatField()
    height = models.IntegerField()

    class Meta:
        db_table = 'coords'


class PerevalAdded(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('pending', 'На модерации'),
        ('accepted', 'Принят'),
        ('rejected', 'Отклонен'),
    ]

    beautyTitle = models.TextField()
    title = models.TextField()
    other_titles = models.TextField(blank=True, null=True)
    connect = models.TextField(blank=True, null=True)
    add_time = models.DateTimeField(auto_now_add=True)
    coords = models.ForeignKey(Coords, on_delete=models.CASCADE)
    summer_level = models.CharField(max_length=10, blank=True, null=True)
    winter_level = models.CharField(max_length=10, blank=True, null=True)
    spring_level = models.CharField(max_length=10, blank=True, null=True)
    autumn_level = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='new')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        db_table = 'pereval_added'


class PerevalImage(models.Model):
    date_added = models.DateTimeField(auto_now_add=True)
    img = models.BinaryField()
    title = models.CharField(max_length=50, default='Без названия')
    pereval = models.ManyToManyField(PerevalAdded, through='PerevalAddedImage', related_name='pereval_images')

    class Meta:
        db_table = 'pereval_images'


class PerevalAddedImage(models.Model):
    pereval = models.ForeignKey(PerevalAdded, on_delete=models.CASCADE, related_name='image')
    image = models.ForeignKey(PerevalImage, on_delete=models.CASCADE)

    class Meta:
        db_table = 'pereval_added_images'
