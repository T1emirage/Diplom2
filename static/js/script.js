
document.addEventListener('DOMContentLoaded', function() {
    const header = document.getElementById('header');
    const scrollThreshold = 50; // Порог скролла в пикселях
    
    window.addEventListener('scroll', function() {
        if (window.scrollY > scrollThreshold) {
            header.classList.add('shrink');
        } else {
            header.classList.remove('shrink');
        }
    });
});


