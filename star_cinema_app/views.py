from django.db import connection
from django.shortcuts import render, redirect
from .models import Customer, CarouselSlide
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import logout
from django.contrib import messages
from django.conf import settings
import re
from .models import Show_Table as Show, Seat, SeatType, BookingSeat
from .models import Booking

# Updated home view (manual session check)

def home(request):
    if not request.session.get('customer_id'):
        return redirect('login')

    theater_id = request.GET.get('theater_id')
    search_query = request.GET.get('q', '').strip()

    with connection.cursor() as cursor:
        # Fetch all theaters for dropdown
        cursor.execute("SELECT id, name FROM star_cinema_app_theater")
        theaters = cursor.fetchall()

        # Base SQL query
        sql = """
            SELECT m.id, m.title, m.genre, m.poster_image, t.name AS theater_name, s.show_time 
            FROM star_cinema_app_movie m
            JOIN star_cinema_app_show_table s ON m.id = s.movie_id
            JOIN star_cinema_app_theater t ON t.id = s.theater_id
        """

        params = []

        # Add WHERE clause if needed
        where_clauses = []

        if theater_id:
            where_clauses.append("t.id = %s")
            params.append(theater_id)

        if search_query:
            where_clauses.append("m.title LIKE %s")
            params.append(f"%{search_query}%")

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        # Execute query with dynamic filters
        cursor.execute(sql, params)
        movies = cursor.fetchall()

    # Load carousel slides
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
from django.conf import settings
from django.shortcuts import render
from django.db import connection

def extract_youtube_id(url):
    if not url:
        return None
    match = re.search(r'(?:v=|youtu\.be/|embed/)([^&]+)', url)
    if match:
        return match.group(1)
    return None

def movie_detail(request, movie_id):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT m.id, m.title, m.genre, m.description, m.poster_image, m.trailer_url, t.name AS theater_name, s.show_time
            FROM star_cinema_app_movie m
            JOIN star_cinema_app_show_table s ON m.id = s.movie_id
            JOIN star_cinema_app_theater t ON t.id = s.theater_id
            WHERE m.id = %s
        """, [movie_id])
        movie_data = cursor.fetchall()

    if not movie_data:
        return render(request, 'star_cinema_app/movie_not_found.html')

    trailer_url = movie_data[0][5]
    youtube_id = extract_youtube_id(trailer_url)

    movie = {
        'id': movie_data[0][0],
        'title': movie_data[0][1],
        'genre': movie_data[0][2],
        'description': movie_data[0][3],
        'poster_image': movie_data[0][4],
        'trailer_url': trailer_url,
        'youtube_id': youtube_id,  # ✅ Add this
    }

    shows = [
        {
            'theater_name': row[6],
            'show_time': row[7],
        }
        for row in movie_data
    ]

    context = {
        'movie': movie,
        'shows': shows,
        'MEDIA_URL': settings.MEDIA_URL,
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
        'shows': shows,
        'MEDIA_URL': settings.MEDIA_URL,
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

from django.template.loader import render_to_string
from django.http import HttpResponse

def get_seat_layout(request, show_id):
    show = Show.objects.get(id=show_id)
    seat_types = SeatType.objects.all()
    seats = Seat.objects.filter(theater=show.theater).order_by('seat_number')
    booked_seats = BookingSeat.objects.filter(show=show).values_list('seat_id', flat=True)

    html = render_to_string('partials/seat_layout.html', {
        'show': show,
        'seat_types': seat_types,
        'seats': seats,
        'booked_seats': list(booked_seats),
    })

    context = {
    'show': show,
    'seat_types': seat_types,
    'seats': seats,
    'booked_seats': list(booked_seats),
    }
    return render(request, 'star_cinema_app/seat_layout.html', context)


from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import io
from .models import Booking, BookingSeat, Seat, Show_Table, Customer

from django.shortcuts import redirect

def confirm_booking(request):
    if request.method == 'POST':
        customer_id = request.session.get('customer_id')
        show_id = request.POST.get('show_id')
        seat_ids = request.POST.getlist('seats')

        if not customer_id or not seat_ids:
            return HttpResponse("Invalid request")

        if len(seat_ids) > 4:
            return HttpResponse("You can select a maximum of 4 seats.")

        customer = Customer.objects.get(id=customer_id)
        show = Show_Table.objects.get(id=show_id)

        # Create booking record
        booking = Booking.objects.create(customer=customer, show=show)

        # Save selected seats
        for seat_id in seat_ids:
            seat = Seat.objects.get(id=seat_id)
            BookingSeat.objects.create(booking=booking, seat=seat, show=show)

        return redirect('booking_summary', booking_id=booking.id)
    else:
        return HttpResponse("Method not allowed")


from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection

def book_ticket(request, show_id):
    with connection.cursor() as cursor:
        # Get show, movie, theater
        cursor.execute("""
            SELECT s.id, s.show_date, s.show_time, m.id, m.title, m.genre, m.poster_image,
                   t.id, t.name, t.rows, t.columns
            FROM star_cinema_app_show_table s
            JOIN star_cinema_app_movie m ON s.movie_id = m.id
            JOIN star_cinema_app_theater t ON s.theater_id = t.id
            WHERE s.id = %s
        """, [show_id])
        row = cursor.fetchone()
        if not row:
            return HttpResponse("Show not found")

        show = {
            'id': row[0], 'show_date': row[1], 'show_time': row[2],
        }
        movie = {
            'id': row[3], 'title': row[4], 'genre': row[5], 'poster_image': row[6],'poster_url': settings.MEDIA_URL + row[6]  # <-- Add this
        }
        theater = {
            'id': row[7], 'name': row[8], 'rows': row[9], 'columns': row[10],
        }

        # Get seat types (✅ use correct table name)
        cursor.execute("SELECT id, name, price FROM star_cinema_app_seattype")
        seat_types = [{'id': r[0], 'name': r[1], 'price': r[2]} for r in cursor.fetchall()]

        # Get all seats (✅ use correct table name)
        cursor.execute("""
            SELECT id, seat_number, seat_type_id FROM star_cinema_app_seat
            WHERE theater_id = %s
        """, [theater['id']])
        seats = cursor.fetchall()
        seat_map = {r[1]: {'id': r[0], 'number': r[1], 'type_id': r[2]} for r in seats}

        # Get booked seats
        cursor.execute("""
            SELECT seat_id FROM star_cinema_app_bookingseat WHERE show_id = %s
        """, [show_id])
        booked_seat_ids = [r[0] for r in cursor.fetchall()]

    # Build seat matrix
    seat_matrix = []
    for row in range(theater['rows']):
        row_letter = chr(ord('A') + row)
        row_data = []
        for col in range(1, theater['columns'] + 1):
            seat_no = f"{row_letter}{col}"
            seat = seat_map.get(seat_no)
            row_data.append(seat)
        seat_matrix.append(row_data)

    return render(request, 'star_cinema_app/book_ticket.html', {
        'show': show,
        'movie': movie,
        'theater': theater,
        'seat_types': seat_types,
        'seat_matrix': seat_matrix,
        'booked_seat_ids': booked_seat_ids,
    })


from django.shortcuts import render
from django.db import connection

def showtimes(request):
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                m.poster_image,
                m.title,
                t.name AS theater_name,
                s.show_date,
                s.show_time
            FROM star_cinema_app_movie AS m
            JOIN star_cinema_app_show_table AS s ON m.id = s.movie_id
            JOIN star_cinema_app_theater AS t ON s.theater_id = t.id
            ORDER BY s.show_date, s.show_time
        """)
        showtimes_data = cursor.fetchall()

    context = {
        'showtimes': showtimes_data,
        'MEDIA_URL': settings.MEDIA_URL,
    }
    return render(request, 'star_cinema_app/showtimes.html', context)

def about(request):
    return render(request, 'star_cinema_app/about.html')



from django.shortcuts import redirect


def booked_tickets(request):
    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')  # User not logged in

    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                b.id,
                m.title,
                t.name AS theater_name,
                s.show_time,
                b.booking_time,
                GROUP_CONCAT(seat.seat_number ORDER BY seat.seat_number) AS seats
            FROM star_cinema_app_booking AS b
            JOIN star_cinema_app_show_table AS s ON b.show_id = s.id
            JOIN star_cinema_app_movie AS m ON s.movie_id = m.id
            JOIN star_cinema_app_theater AS t ON s.theater_id = t.id
            JOIN star_cinema_app_bookingseat AS bs ON b.id = bs.booking_id
            JOIN star_cinema_app_seat AS seat ON bs.seat_id = seat.id
            WHERE b.customer_id = %s
            GROUP BY b.id, m.title, t.name, s.show_time, b.booking_time
            ORDER BY b.booking_time DESC
        """, [customer_id])

        bookings = cursor.fetchall()

    return render(request, 'star_cinema_app/booked_tickets.html', {'bookings': bookings})



from django.shortcuts import get_object_or_404

def download_ticket(request, booking_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')

    booking = get_object_or_404(Booking, id=booking_id, customer_id=customer_id)
    show = booking.show
    customer = booking.customer
    booking_seats = BookingSeat.objects.filter(booking=booking)
    seats = [bs.seat for bs in booking_seats]

    # ✅ Calculate total cost correctly
    total_price = sum(seat.seat_type.price for seat in seats)

    context = {
        'booking': booking,
        'customer': customer,
        'show': show,
        'seats': seats,
        'total_price': total_price,  # ✅ pass it
    }

    html = render_to_string('star_cinema_app/ticket_pdf.html', context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="ticket_{booking.id}.pdf"'
    pisa_status = pisa.CreatePDF(io.StringIO(html), dest=response)

    if pisa_status.err:
        return HttpResponse("Error generating PDF")
    return response



from django.shortcuts import get_object_or_404, render

def booking_summary(request, booking_id):
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('login')

    booking = get_object_or_404(Booking, id=booking_id, customer_id=customer_id)
    show = booking.show
    movie = show.movie
    theater = show.theater
    customer = booking.customer
    seats = [bs.seat for bs in BookingSeat.objects.filter(booking=booking)]

    # ✅ Calculate total price
    total_price = sum(seat.seat_type.price for seat in seats)

    return render(request, 'star_cinema_app/booking_summary.html', {
        'booking': booking,
        'customer': customer,
        'movie': movie,
        'show': show,
        'theater': theater,
        'seats': seats,
        'total_price': total_price,  # ✅ Pass it to template
    })
