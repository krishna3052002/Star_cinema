from django.db import models
from django.contrib.auth.hashers import make_password

class Movie(models.Model):
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    duration = models.IntegerField()
    description = models.TextField()
    poster_image = models.ImageField(upload_to='movies/')
    trailer_url = models.URLField(blank=True, null=True, help_text="YouTube trailer link")

    def __str__(self):
        return self.title

from django.db import models

class Theater(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    rows = models.IntegerField()
    columns = models.IntegerField()

    def __str__(self):
        return self.name

    @property
    def total_seats(self):
        return self.rows * self.columns

    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new Theater
        super().save(*args, **kwargs)

        if is_new:
            # Get default seat type (adjust name as needed)
            default_seat_type = SeatType.objects.filter(name="Regular").first()
            if not default_seat_type:
                # If no default seat type found, create one
                default_seat_type = SeatType.objects.create(name="Regular", price=100)

            # Bulk create seats
            seats_to_create = []
            for row_num in range(1, self.rows + 1):
                row_letter = chr(64 + row_num)  # 1 -> A, 2 -> B, etc.
                for col_num in range(1, self.columns + 1):
                    seat_number = f"{row_letter}{col_num}"
                    seat = Seat(
                        seat_number=seat_number,
                        seat_type=default_seat_type,
                        theater=self,
                    )
                    seats_to_create.append(seat)

            Seat.objects.bulk_create(seats_to_create)



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
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    password = models.CharField(max_length=100)

    def save(self, *args, **kwargs):
        # Hash the password before saving
        if self.password:
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
    

class SeatType(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name

# models.py
class Seat(models.Model):
    seat_number = models.CharField(max_length=10)
    seat_type = models.ForeignKey(SeatType, on_delete=models.CASCADE)
    theater = models.ForeignKey('Theater', on_delete=models.CASCADE)

    def __str__(self):
        return self.seat_number


class Booking(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    show = models.ForeignKey('Show_Table', on_delete=models.CASCADE)
    booking_time = models.DateTimeField(auto_now_add=True)

class BookingSeat(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE)
    seat = models.ForeignKey(Seat, on_delete=models.CASCADE)
    show = models.ForeignKey('Show_Table', on_delete=models.CASCADE)
