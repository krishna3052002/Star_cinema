from django.contrib import admin
from .models import Movie, Theater, Show_Table
from .models import CarouselSlide
admin.site.register(Movie)
admin.site.register(Theater)
admin.site.register(Show_Table)
admin.site.register(CarouselSlide)