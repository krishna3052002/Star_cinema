
from django.contrib import admin
from .models import Movie, Theater, Show_Table, CarouselSlide, Customer, SeatType, Seat, Booking, BookingSeat
from django.db import connection
admin.site.register(Movie)
admin.site.register(Show_Table)
admin.site.register(CarouselSlide)
admin.site.register(Customer)
admin.site.register(SeatType)
admin.site.register(Seat)
admin.site.register(Booking)
admin.site.register(BookingSeat)


class TheaterAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if not change:  # Only create seats if new
            vip_type = SeatType.objects.filter(name__iexact='VIP').first()
            regular_type = SeatType.objects.filter(name__iexact='Regular').first()

            if not vip_type or not regular_type:
                raise Exception("Please create 'VIP' and 'Regular' seat types first in admin.")

            with connection.cursor() as cursor:
                for row in range(obj.rows):
                    row_letter = chr(ord('A') + row)
                    seat_type_id = vip_type.id if row < 2 else regular_type.id

                    for col in range(1, obj.columns + 1):
                        seat_number = f"{row_letter}{col}"
                        cursor.execute("""
                           INSERT INTO star_cinema_app_seat (seat_number, seat_type_id, theater_id)
                           VALUES (%s, %s, %s)
                        """, [seat_number, seat_type_id, obj.id])
admin.site.register(Theater, TheaterAdmin)

