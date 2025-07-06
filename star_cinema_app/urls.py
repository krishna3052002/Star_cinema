from django.urls import path
from . import views  # Import your views
from .views import logout_view
urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('book/<int:movie_id>/', views.book_movie, name='book_movie'),
    path('select-seats/<int:show_id>/', views.select_seats, name='select_seats'),
    path('get_seat_layout/<int:show_id>/', views.get_seat_layout, name='get_seat_layout'),
    path('confirm-booking/', views.confirm_booking, name='confirm_booking'),
    path('book-ticket/<int:show_id>/', views.book_ticket, name='book_ticket'),
    path('about/', views.about, name='about'), 
    path('showtimes/', views.showtimes, name='showtimes'),
    path('booked_tickets/', views.booked_tickets, name='booked_tickets'),
    path('booking/<int:booking_id>/summary/', views.booking_summary, name='booking_summary'),
    path('download_ticket/<int:booking_id>/', views.download_ticket, name='download_ticket'),
]
