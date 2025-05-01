from django.db import connection
from django.shortcuts import render, redirect
from .models import Customer, CarouselSlide
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout
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