from django.db import connection
from django.shortcuts import render

def home(request):
    query = request.GET.get('search', '')

    with connection.cursor() as cursor:
        if query:
            cursor.execute("SELECT * FROM Movie WHERE Title LIKE %s", ['%' + query + '%'])
        else:
            cursor.execute("SELECT * FROM Movie")
        movie_rows = cursor.fetchall()

        cursor.execute("SELECT * FROM Theater")
        theater_rows = cursor.fetchall()

    # Convert raw SQL rows to dictionaries (optional, for easier template use)
    movies = [{'id': row[0], 'title': row[1], 'genre': row[2], 'duration': row[3],
               'description': row[4], 'poster_image': row[5]} for row in movie_rows]

    theaters = [{'id': row[0], 'name': row[1], 'location': row[2], 'capacity': row[3]} for row in theater_rows]

    return render(request, 'star_cinema_app/index.html', {'movies': movies, 'theaters': theaters})
