from django.urls import path
from . import views  # Import your views

urlpatterns = [
    path('', views.home, name='home'),  # Home page
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
]
