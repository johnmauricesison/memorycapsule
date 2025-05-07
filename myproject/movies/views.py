from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Avg, Q
from django.http import JsonResponse
from rest_framework import permissions, request
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.views import TokenObtainPairView
from .models import Genre, Movie, Review, UserMovieStatus, MemoryNote
from .forms import SearchForm, ReviewForm, MemoryNoteForm
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import GenreSerializer, MovieSerializer, ReviewSerializer, UserMovieStatusSerializer, MemoryNoteSerializer
from rest_framework.pagination import PageNumberPagination
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'


class JWTAuthenticatedView(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]  # Add JWT authentication
    permission_classes = [IsAuthenticated]

class LoginView(TokenObtainPairView):
    permission_classes = (permissions.AllowAny,)


def logout_view(request):
    logout(request)
    return redirect('dashboard')

@login_required
def home(request):
    notes = MemoryNote.objects.filter(user=request.user)
    return render(request, 'movies/home.html', {'notes': notes})



def add_memory(request):
    if request.method == 'POST':
        form = MemoryNoteForm(request.POST)
        movie_id = request.POST.get('movie')  
        if form.is_valid():
            memory_note = form.save(commit=False)
            memory_note.user = request.user  

            if movie_id:
                memory_note.movie = Movie.objects.get(id=movie_id)

            memory_note.save()  
            return redirect('home')  
    else:
        form = MemoryNoteForm()  

    movies = Movie.objects.all()
    context = {
        'form': form,
        'movies': movies,
        'today': timezone.now().date().isoformat()
    }
    return render(request, 'movies/add_memory.html', context)

# This is for editing a memory
@login_required
def edit_memory(request, memory_id):  
    memory = get_object_or_404(MemoryNote, pk=memory_id, user=request.user)  # Ensure the user is the owner of the memory

    if not memory.is_opened():  # Check if the memory is locked
        return redirect('memory_locked')  # Redirect to the memory_locked view if the memory is locked

    if request.method == 'POST':
        form = MemoryNoteForm(request.POST, instance=memory)
        movie_id = request.POST.get('movie')  # Get the movie from the POST data
        if form.is_valid():
            memory_note = form.save(commit=False)
            memory_note.user = request.user  # Ensure the memory belongs to the current user

            if movie_id:
                memory_note.movie = Movie.objects.get(id=movie_id)
            else:
                memory_note.movie = None  # Clear the movie if none is selected

            memory_note.save()  # Save the updated memory
            return redirect('home')  # Redirect to the home page after saving
    else:
        form = MemoryNoteForm(instance=memory)  # Load the form with the existing memory data

    movies = Movie.objects.all()  # Fetch all movies for the dropdown
    return render(request, 'movies/edit_memory.html', {
        'form': form,
        'movies': movies,
        'memory': memory
    })


# This is for deleting a memory
def delete_memory(request, pk):
    memory = get_object_or_404(MemoryNote, pk=pk)

    if request.method == 'POST':
        memory.delete() #Deletes memory
        return redirect('home')  

    return render(request, 'movies/delete_memory.html', {'memory': memory})

# View to show individual memory detail if it's unlocked
@login_required
def memory_detail(request, pk):
    memory = get_object_or_404(MemoryNote, pk=pk, user=request.user)
    
    if not memory.is_opened():
        return redirect('memory_locked')  
    
    return render(request, 'movies/memory_detail.html', {'memory': memory})

# View to show a message if the memory is still locked
@login_required
def memory_locked(request):
    return render(request, 'movies/memory_locked.html')


class MemoryNoteListCreateView(JWTAuthenticatedView, generics.ListCreateAPIView):
    serializer_class = MemoryNoteSerializer
    def get_queryset(self):
        return MemoryNote.objects.filter(user=self.request.user)
    pagination_class = StandardResultsSetPagination

class MemoryNoteRetrieveUpdateDestroyView(JWTAuthenticatedView, generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MemoryNoteSerializer
    def get_queryset(self):
        return MemoryNote.objects.filter(user=self.request.user)

# List all movies and create new movie
class MovieListCreateView(JWTAuthenticatedView, generics.ListCreateAPIView):
    serializer_class = MovieSerializer
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        return Movie.objects.filter(user=self.request.user)

    

# Retrieve, update, or delete one movie
class MovieDetailView(JWTAuthenticatedView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


# List and create reviews
class ReviewListCreateView(JWTAuthenticatedView, generics.ListCreateAPIView):
    serializer_class = ReviewSerializer
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        return Review.objects.filter(user=self.request.user)


# List and create user movie status
class UserMovieStatusListCreateView(JWTAuthenticatedView, generics.ListCreateAPIView):
    queryset = UserMovieStatus.objects.all()
    serializer_class = UserMovieStatusSerializer
    pagination_class = StandardResultsSetPagination


class GenreListCreateView(JWTAuthenticatedView, generics.ListCreateAPIView):
    serializer_class = GenreSerializer
    pagination_class = StandardResultsSetPagination
    def get_queryset(self):
        return Genre.objects.filter(user=self.request.user)


class GenreDetailView(JWTAuthenticatedView, generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


@login_required
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Protect the dashboard
    
    user = request.user
    
    # Get statistics
    total_movies = Movie.objects.count()
    recently_added = Movie.objects.order_by('-date_added')[:5]
    
    # Get user-specific stats
    user_stats = {
        'watched_count': UserMovieStatus.objects.filter(user=user, watched=True).count(),
        'watchlist_count': UserMovieStatus.objects.filter(user=user, on_watchlist=True).count(),
        'liked_count': UserMovieStatus.objects.filter(user=user, liked=True).count(),
    }
    
    # Get movies on user's watchlist
    watchlist_movies = Movie.objects.filter(
        usermoviestatus__user=user,
        usermoviestatus__on_watchlist=True
    )[:5]

    liked_movies = Movie.objects.filter(
        usermoviestatus__user=user,
        usermoviestatus__liked=True
    )[:5]
    
    # Get watched movies
    watched_movies = Movie.objects.filter(
        usermoviestatus__user=user,
        usermoviestatus__watched=True
    )[:5]
    
    # Get highly rated movies (not already watched)
    highly_rated = Movie.objects.annotate(
        avg_rating=Avg('review__rating')
    ).filter(
        avg_rating__gte=4
    ).exclude(
        usermoviestatus__user=user,
        usermoviestatus__watched=True
    ).order_by('-avg_rating')[:5]
    
    # Handle search form
    search_form = SearchForm()
    
    context = {
        'total_movies': total_movies,
        'recently_added': recently_added,
        'user_stats': user_stats,
        'watchlist_movies': watchlist_movies,
        'watched_movies': watched_movies,
        'liked_movies': liked_movies,
        'highly_rated': highly_rated,
        'search_form': search_form,
    }
    
    return render(request, 'movies/dashboard.html', context)

@login_required
def liked_movies(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Protect the dashboard
    
    user = request.user
    
    # Get user-specific stats
    user_stats = {
        'liked_count': UserMovieStatus.objects.filter(user=user, liked=True).count(),
    }
    
    liked_movies = Movie.objects.filter(
        usermoviestatus__user=user,
        usermoviestatus__liked=True
    )
    
    # Handle search form
    search_form = SearchForm()
    
    context = {
        'user_stats': user_stats,
        'liked_movies': liked_movies,
        'search_form': search_form,
    }
    
    return render(request, 'movies/liked_movies.html', context)

@login_required
def watchlist_movies(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Protect the dashboard
    
    user = request.user
    
    # Get user-specific stats
    user_stats = {
        'watchlist_count': UserMovieStatus.objects.filter(user=user, on_watchlist=True).count(),
    }
    
    # Get movies on user's watchlist
    watchlist_movies = Movie.objects.filter(
        usermoviestatus__user=user,
        usermoviestatus__on_watchlist=True
    )
    
    # Handle search form
    search_form = SearchForm()
    
    context = {
        
        'user_stats': user_stats,
        'watchlist_movies': watchlist_movies,
        'search_form': search_form,
    }
    
    return render(request, 'movies/watchlist.html', context)

@login_required
def watched_movies(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Protect the dashboard
    
    user = request.user
    
    user_stats = {
        'watched_count': UserMovieStatus.objects.filter(user=user, watched=True).count(),
    }
    
    # Get watched movies
    watched_movies = Movie.objects.filter(
        usermoviestatus__user=user,
        usermoviestatus__watched=True
    )
    
    # Handle search form
    search_form = SearchForm()
    
    context = {
        'user_stats': user_stats,
        'watched_movies': watched_movies,
        'search_form': search_form,
    }
    
    return render(request, 'movies/watched.html', context)

@login_required
def my_reviews(request):
    reviews = Review.objects.filter(user=request.user).select_related('movie').order_by('-created_date')

    context = {
        'reviews': reviews,
    }
    return render(request, 'movies/reviews.html', context)

@login_required
def search_results(request):
    """Display search results based on query"""
    search_form = SearchForm(request.GET)
    query = request.GET.get('query', '')
    
    results = []
    if query:
        results = Movie.objects.filter(
            Q(title__icontains=query) | 
            Q(director__icontains=query) |
            Q(genres__name__icontains=query)
        ).distinct()
    
    context = {
        'search_form': search_form,
        'query': query,
        'results': results,
    }
    
    return render(request, 'movies/search_results.html', context)

@login_required
def movie_detail(request, movie_id):
    movie = get_object_or_404(Movie, pk=movie_id)

    if request.user.is_authenticated:
        user = request.user

        user_status = UserMovieStatus.objects.get_or_create(
            user=user,
            movie=movie,
        )
        
        # Handle review submission
        if request.method == 'POST':
            review_form = ReviewForm(request.POST)
            if review_form.is_valid():
                review = review_form.save(commit=False)
                review.movie = movie
                review.user = request.user  # Use the authenticated user
                review.save()
                return redirect('movie_detail', movie_id=movie_id)
        else:
            review_form = ReviewForm()
        
        # Get reviews for this movie
        reviews = Review.objects.filter(movie=movie).order_by('-created_date')
        
        context = {
            'movie': movie,
            'user_status': user_status,
            'review_form': review_form,
            'reviews': reviews,
            'search_form': SearchForm(),
            'user': user,
        }
    else:
        context = {
            'error_message': 'You need to be logged in to submit a review.',
        }

    
    return render(request, 'movies/movie_detail.html', context)


@csrf_exempt
def update_movie_status(request, movie_id):
    """Update user's status for a movie (watched, watchlist, liked)"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Not authenticated'}, status=401)
        
        movie = get_object_or_404(Movie, pk=movie_id)
        user = request.user
        
        status_type = request.POST.get('status_type')
        status_value = request.POST.get('status_value') == 'true'
        
        user_status, created = UserMovieStatus.objects.get_or_create(
            user=user,
            movie=movie,
        )
        
        if status_type == 'watched':
            user_status.watched = status_value
        elif status_type == 'watchlist':
            user_status.on_watchlist = status_value
        elif status_type == 'liked':
            user_status.liked = status_value
        else:
            return JsonResponse({'success': False, 'message': 'Invalid status type'}, status=400)
        
        user_status.save()
        
        return JsonResponse({
            'success': True,
            'movie_id': movie_id,
            'status_type': status_type,
            'status_value': status_value,
        })
    
    logger.info("User %s updated movie status", request.user.username)
    
    return JsonResponse({'success': False}, status=400)


@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)

    if review.user == request.user:
        review.delete() 
        return redirect('dashboard') 
    else:
        return redirect('dashboard')