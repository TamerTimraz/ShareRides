document.addEventListener('DOMContentLoaded', function() {
    // Animate vehicle/collection cards on scroll with staggered delay
    const cards = document.querySelectorAll('.product-card');
    
    if (cards.length > 0) {
        cards.forEach((card, index) => {
            const delay = index % 4 * 100;
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            card.style.transition = `opacity 0.5s ease ${delay}ms, transform 0.5s ease ${delay}ms`;
            
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 100);
        });
    }
    
    // Add hover effect to buttons
    const buttons = document.querySelectorAll('.btn:not(.dropdown-toggle)');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Navbar shadow on scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (window.scrollY > 10) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Add heart toggle functionality
    const hearts = document.querySelectorAll('.fa-heart');
    hearts.forEach(heart => {
        heart.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            this.classList.toggle('far');
            this.classList.toggle('fas');
            this.classList.toggle('text-danger');
            
            // Add little bounce animation
            this.style.transform = 'scale(1.3)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 200);
        });
    });
});
