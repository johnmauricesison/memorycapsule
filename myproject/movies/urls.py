from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', views.TokenObtainPairView.as_view(), name='token_obtain_pair'),  
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', auth_views.LoginView.as_view(template_name='movies/login.html'), name='login'),

    path('', views.dashboard, name='dashboard'),
    path('search/', views.search_results, name='search_results'),
    path('movie/<int:movie_id>/', views.movie_detail, name='movie_detail'),
    path('movie/<int:movie_id>/update-status/', views.update_movie_status, name='update_movie_status'),
    path('movies/liked_movies/', views.liked_movies, name="liked-movies"),
    path('movies/watchlist_movies/', views.watchlist_movies, name="watchlist-movies"),
    path('movies/watched_movies/', views.watched_movies, name="watched-movies"),
    path('my-reviews/', views.my_reviews, name='my-reviews'),
    path('review/delete/<int:review_id>/', views.delete_review, name='delete_review'),

    path('api/movies/', views.MovieListCreateView.as_view(), name='movie-list-create'),
    path('api/movies/<int:pk>/', views.MovieDetailView.as_view(), name='movie-detail'),
    path('api/genre/', views.GenreListCreateView.as_view(), name='genre-create'),
    path('api/genre/<int:pk>/', views.GenreDetailView.as_view(), name='genre-detail'),
    path('api/reviews/', views.ReviewListCreateView.as_view(), name='review-list-create'),
    path('api/status/', views.UserMovieStatusListCreateView.as_view(), name='status-list-create'),


    path('memories/', views.home, name='home'),
    path('new/', views.add_memory, name='add_memory'),
    path('edit/<int:memory_id>/', views.edit_memory, name='edit_memory'),
    path('delete/<int:pk>/', views.delete_memory, name='delete_memory'),
    path('memory/<int:pk>/', views.memory_detail, name='memory_detail'),
    path('memory/locked/', views.memory_locked, name='memory_locked'),

    path('api/memory/', views.MemoryNoteListCreateView.as_view(), name='api_memory_create'),
    path('api/memory/<int:pk>/', views.MemoryNoteRetrieveUpdateDestroyView.as_view(), name='api_memory_detail'),
]