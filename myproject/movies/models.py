from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class MemoryNote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    note_title = models.CharField(max_length=100)
    note_body = models.TextField()
    unlock_on = models.DateField()
    movie = models.ForeignKey('Movie', on_delete=models.SET_NULL, null=True, blank=True)  # Add Movie foreign key
    date_written = models.DateTimeField(auto_now_add=True)

    def is_opened(self):
        return timezone.now().date() >= self.unlock_on

    def __str__(self):
        return self.note_title

class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    
    def __str__(self):
        return self.name

class Movie(models.Model):
    title = models.CharField(max_length=200)
    director = models.CharField(max_length=100, default="none")
    release_year = models.PositiveIntegerField()
    genres = models.ManyToManyField(Genre)
    synopsis = models.TextField()
    poster = models.ImageField(upload_to='posters/', blank=True, null=True)
    runtime = models.PositiveIntegerField(help_text="Runtime in minutes", default=0)
    date_added = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"{self.title} ({self.release_year})"
    
    def average_rating(self):
        reviews = self.review_set.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0
    
    def likes_count(self):
        return self.usermoviestatus_set.filter(liked=True).count()
    
    class Meta:
        ordering = ['-date_added']

class Review(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars"
    )
    created_date = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Review of {self.movie.title} by {self.user.username if self.user else 'Anonymous'}"
    
    class Meta:
        ordering = ['-created_date']

class UserMovieStatus(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    watched = models.BooleanField(default=False)
    on_watchlist = models.BooleanField(default=False)
    liked = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'movie')  
        ordering = ['user', 'movie']

    def __str__(self):
        return f"Status for {self.movie.title} - User: {self.user.username if self.user else 'Anonymous'}"  
