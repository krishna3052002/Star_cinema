from django.db import connection
from django.shortcuts import render

def home(request):
    theater_id = request.GET.get('theater_id')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM star_cinema_app_theater")
        theaters = cursor.fetchall()

        # Load movies (filtered by theater)
        if theater_id:
            cursor.execute("""
                SELECT m.id, m.title, m.genre, m.poster_image, t.name AS theater_name, s.show_time 
                FROM star_cinema_app_movie m
                JOIN star_cinema_app_show_table s ON m.id = s.movie_id
                JOIN star_cinema_app_theater t ON t.id = s.theater_id
                WHERE t.id = %s
            """, [theater_id])
        else:
            cursor.execute("""
                SELECT m.id, m.title, m.genre, m.poster_image, t.name AS theater_name, s.show_time 
                FROM star_cinema_app_movie m
                JOIN star_cinema_app_show_table s ON m.id = s.movie_id
                JOIN star_cinema_app_theater t ON t.id = s.theater_id
            """)
        movies = cursor.fetchall()

    # Load Carousel Slides
    from .models import CarouselSlide
    slides = CarouselSlide.objects.all()

    context = {
        'theaters': theaters,
        'movies': movies,
        'slides': slides,
    }
    return render(request, 'star_cinema_app/home.html', context)


# movie details
def movie_detail(request, movie_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT m.id, m.title, m.genre, m.description, m.poster_image, t.name AS theater_name, s.show_time
            FROM star_cinema_app_movie m
            JOIN star_cinema_app_show_table s ON m.id = s.movie_id
            JOIN star_cinema_app_theater t ON t.id = s.theater_id
            WHERE m.id = %s
        """, [movie_id])
        movie_data = cursor.fetchall()

    if not movie_data:
        return render(request, 'star_cinema_app/movie_not_found.html')

    context = {
        'movie': movie_data[0],
        'shows': movie_data
    }
    return render(request, 'star_cinema_app/movie_detail.html', context)
