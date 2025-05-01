from django.db import connection
from django.shortcuts import render

def home(request):
    theater_id = request.GET.get('theater_id')

    with connection.cursor() as cursor:
        cursor.execute("SELECT id, name FROM star_cinema_app_theater")
        theaters = cursor.fetchall()

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

    context = {
        'theaters': theaters,
        'movies': movies,
    }
    return render(request, 'star_cinema_app/home.html', context)