
from rest_framework import serializers
from .models import Genre, Movie, Review, UserMovieStatus, MemoryNote

class MemoryNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemoryNote
        fields = ['id', 'note_title', 'note_body', 'unlock_on', 'user']  # Include user field

    def create(self, validated_data):
        # Automatically set the user field to the current logged-in user
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
    

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['id', 'name']

class MovieSerializer(serializers.ModelSerializer):
    genres = serializers.PrimaryKeyRelatedField(queryset=Genre.objects.all(), many=True)
    average_rating = serializers.FloatField(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'director', 'release_year', 'genres',
            'synopsis', 'poster', 'runtime', 'date_added',
            'average_rating', 'likes_count'
        ]

class ReviewSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)

    class Meta:
        model = Review
        fields = ['id', 'movie', 'movie_title', 'user', 'content', 'rating', 'created_date']

class UserMovieStatusSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source='movie.title', read_only=True)
    users = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserMovieStatus
        fields = [
            'id', 'users', 'movie', 'movie_title',
            'watched', 'on_watchlist', 'liked'
        ]
