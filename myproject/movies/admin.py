# movies/admin.py
from django.contrib import admin
from .models import Movie, Genre, Review, UserMovieStatus, MemoryNote

class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ('user', 'rating', 'content', 'created_date')
    can_delete = True

class MemoryNoteAdmin(admin.ModelAdmin):
    list_display = ('note_title', 'user', 'get_movie_title', 'unlock_on', 'is_opened', 'date_written')
    list_filter = ('unlock_on', 'movie__title')  # Filter by the related movie's title
    search_fields = ('note_title', 'note_body', 'user__username', 'movie__title')
    readonly_fields = ('date_written',)

    def get_movie_title(self, obj):
        return obj.movie.title if obj.movie else 'No Movie'
    get_movie_title.short_description = 'Related Movie'

@admin.register(MemoryNote)
class MemoryNoteAdmin(admin.ModelAdmin):
    list_display = ('note_title', 'user', 'get_movie_title', 'unlock_on', 'is_opened', 'date_written')  # Use get_movie_title
    list_filter = ('unlock_on', 'movie__title') 
    search_fields = ('note_title', 'note_body', 'user__username', 'movie__title')
    readonly_fields = ('date_written',)

    def get_movie_title(self, obj):
        return obj.movie.title if obj.movie else 'No Movie'
    get_movie_title.short_description = 'Related Movie'


class UserStatusInline(admin.TabularInline):
    model = UserMovieStatus
    extra = 0
    readonly_fields = ('user', 'watched', 'on_watchlist', 'liked')
    can_delete = True

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'director', 'release_year', 'get_genres', 'average_rating', 'likes_count')
    list_filter = ('release_year', 'genres')
    search_fields = ('title', 'director', 'synopsis')
    filter_horizontal = ('genres',)
    inlines = [ReviewInline, UserStatusInline]
    
    def get_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])
    get_genres.short_description = 'Genres'

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('movie', 'user', 'rating', 'created_date')
    list_filter = ('rating', 'created_date')
    search_fields = ('movie__title', 'user', 'content')
    readonly_fields = ('created_date',)

@admin.register(UserMovieStatus)
class UserMovieStatusAdmin(admin.ModelAdmin):
    list_display = ('user', 'movie', 'watched', 'on_watchlist', 'liked')
    list_filter = ('watched', 'on_watchlist', 'liked')
    search_fields = ('user', 'movie__title')