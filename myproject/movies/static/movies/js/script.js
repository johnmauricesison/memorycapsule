function updateMovieStatus(movieId, statusType, statusValue) {
    // Get CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Send AJAX request
    fetch(`/movie/${movieId}/update-status/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: `status_type=${statusType}&status_value=${statusValue}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Update UI based on status type
            if (statusType === 'liked') {
                const likeBtn = document.getElementById('like-btn');
                if (statusValue) {
                    likeBtn.classList.remove('btn-outline-danger');
                    likeBtn.classList.add('btn-danger');
                    likeBtn.innerHTML = '<i class="fas fa-heart"></i> Liked';
                } else {
                    likeBtn.classList.remove('btn-danger');
                    likeBtn.classList.add('btn-outline-danger');
                    likeBtn.innerHTML = '<i class="fas fa-heart"></i> Like';
                }
            } else if (statusType === 'watched') {
                const watchedBtn = document.getElementById('watched-btn');
                if (statusValue) {
                    watchedBtn.classList.remove('btn-outline-success');
                    watchedBtn.classList.add('btn-success');
                    watchedBtn.innerHTML = '<i class="fas fa-eye"></i> Watched';
                } else {
                    watchedBtn.classList.remove('btn-success');
                    watchedBtn.classList.add('btn-outline-success');
                    watchedBtn.innerHTML = '<i class="fas fa-eye"></i> Mark Watched';
                }
            } else if (statusType === 'watchlist') {
                const watchlistBtn = document.getElementById('watchlist-btn');
                if (statusValue) {
                    watchlistBtn.classList.remove('btn-outline-warning');
                    watchlistBtn.classList.add('btn-warning');
                    watchlistBtn.innerHTML = '<i class="fas fa-check-circle"></i> On Watchlist';
                } else {
                    watchlistBtn.classList.remove('btn-warning');
                    watchlistBtn.classList.add('btn-outline-warning');
                    watchlistBtn.innerHTML = '<i class="fas fa-plus-circle"></i> Add to Watchlist';
                }
            }
        }
    })
    .catch(error => console.error('Error:', error));
}