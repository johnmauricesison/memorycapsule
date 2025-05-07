function updateMovieStatus(movieId, statusType, statusValue) {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
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
            const btns = {
                liked: 'like-btn',
                watched: 'watched-btn',
                watchlist: 'watchlist-btn'
            };
            const btn = document.getElementById(btns[statusType]);
            if (statusValue) {
                btn.classList.replace(`btn-outline-${statusType}`, `btn-${statusType}`);
                btn.innerHTML = `<i class="fas fa-${statusType === 'liked' ? 'heart' : 'eye'}"></i> ${statusType.charAt(0).toUpperCase() + statusType.slice(1)}`;
            } else {
                btn.classList.replace(`btn-${statusType}`, `btn-outline-${statusType}`);
                btn.innerHTML = `<i class="fas fa-${statusType === 'liked' ? 'heart' : 'eye'}"></i> Mark ${statusType.charAt(0).toUpperCase() + statusType.slice(1)}`;
            }
        }
    })
    .catch(error => console.error('Error:', error));
}
