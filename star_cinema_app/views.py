from django.db import connection
from django.shortcuts import render, redirect
from .models import Customer, CarouselSlide
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
# Updated home view (manual session check)
def home(request):
    if not request.session.get('customer_id'):
        return redirect('login')

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

    slides = CarouselSlide.objects.all()

    context = {
        'theaters': theaters,
        'movies': movies,
        'slides': slides,
        'request': request,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'star_cinema_app/home.html', context)


# Movie detail view
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


# Signup view
def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        phone_number = request.POST['phone_number']
        password = request.POST['password']

        hashed_password = make_password(password)

        with connection.cursor() as cursor:
            cursor.execute("""
                INSERT INTO star_cinema_app_customer (username, email, phone_number, password)
                VALUES (%s, %s, %s, %s)
            """, [username, email, phone_number, hashed_password])

        return redirect('login')

    return render(request, 'star_cinema_app/signup.html')


# Login view with manual auth
from django.contrib.auth.hashers import check_password

def login_view(request):
    if request.session.get('customer_id'):
        return redirect('home')  # Already logged in

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        with connection.cursor() as cursor:
            cursor.execute("SELECT id, username, email, password FROM star_cinema_app_customer WHERE email = %s", [email])
            customer = cursor.fetchone()

        if customer and check_password(password, customer[3]):
            # Login successful, set session
            request.session['customer_id'] = customer[0]
            request.session['customer_name'] = customer[1]
            return redirect('home')
        else:
            return render(request, 'star_cinema_app/login.html', {'error': 'Invalid email or password'})

    return render(request, 'star_cinema_app/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def book_movie(request, movie_id):
    with connection.cursor() as cursor:
        # Fetch movie details including poster image
        cursor.execute("""
            SELECT id, title, genre, duration, description, poster_image 
            FROM star_cinema_app_movie
            WHERE id = %s
        """, [movie_id])
        movie_row = cursor.fetchone()

        if not movie_row:
            messages.error(request, "Movie not found.")
            return redirect('home')

        movie = {
            'id': movie_row[0],
            'title': movie_row[1],
            'genre': movie_row[2],
            'duration': movie_row[3],
            'description': movie_row[4],
            'poster_image': movie_row[5],  # Include this
        }

        # Fetch shows of that movie
        cursor.execute("""
            SELECT s.id, t.name, s.show_date, s.show_time, s.available_seats
            FROM star_cinema_app_show_table s
            JOIN star_cinema_app_theater t ON s.theater_id = t.id
            WHERE s.movie_id = %s
            ORDER BY s.show_date, s.show_time
        """, [movie_id])
        shows = cursor.fetchall()

    context = {
        'movie': movie,
        'shows': shows
    }

    return render(request, 'star_cinema_app/book_movie.html', context)


def select_seats(request, show_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT s.id, s.seat_number, s.seat_type_id, st.name, st.price
            FROM seat s
            JOIN seat_type st ON s.seat_type_id = st.id
            WHERE s.theater_id = (
                SELECT theater_id FROM star_cinema_app_show_table WHERE id = %s
            )
        """, [show_id])
        seats = cursor.fetchall()

    return render(request, 'star_cinema_app/select_seats.html', {
        'show_id': show_id,
        'seats': seats
    })