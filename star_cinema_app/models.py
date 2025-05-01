from django.db import models

class Movie(models.Model):
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    duration = models.IntegerField()
    description = models.TextField()
    poster_image = models.ImageField(upload_to='movies/')

    def __str__(self):
        return self.title

class Theater(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    seat_capacity = models.IntegerField()

    def __str__(self):
        return self.name

class Show_Table(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    theater = models.ForeignKey(Theater, on_delete=models.CASCADE)
    show_date = models.DateField()
    show_time = models.TimeField()
    available_seats = models.IntegerField()

    def __str__(self):
        return f"{self.movie.title} at {self.theater.name} on {self.show_date}"

class CarouselSlide(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='carousel/')
    description = models.TextField(blank=True)

    def __str__(self):
        return self.title

# models.py
class Customer(models.Model):
    username = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    password = models.CharField(max_length=100)
