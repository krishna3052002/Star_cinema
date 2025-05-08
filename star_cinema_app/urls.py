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
]
