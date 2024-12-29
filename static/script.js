document.addEventListener('DOMContentLoaded', () => {
    // Smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });

    // Animated background for hero section
    const hero = document.querySelector('.hero');
    for (let i = 0; i < 50; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        star.style.left = `${Math.random() * 100}%`;
        star.style.top = `${Math.random() * 100}%`;
        star.style.animationDuration = `${Math.random() * 3 + 2}s`;
        star.style.animationDelay = `${Math.random() * 2}s`;
        hero.appendChild(star);
    }

    // File input animation
    const fileInput = document.getElementById('file-input');
    const fileLabel = document.querySelector('.file-input-wrapper label span');
    const originalText = fileLabel.textContent;

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            fileLabel.textContent = e.target.files[0].name;
        } else {
            fileLabel.textContent = originalText;
        }
    });

    // Animate feature cards on scroll
    const featureCards = document.querySelectorAll('.feature-card');
    const animateOnScroll = (entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = 1;
                entry.target.style.transform = 'translateY(0)';
            }
        });
    };

    const observer = new IntersectionObserver(animateOnScroll, {
        root: null,
        threshold: 0.1
    });

    featureCards.forEach(card => {
        card.style.opacity = 0;
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        observer.observe(card);
    });

    // Animate steps on scroll
    const steps = document.querySelectorAll('.step');
    steps.forEach((step, index) => {
        step.style.opacity = 0;
        step.style.transform = 'translateX(50px)';
        step.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
        step.style.transitionDelay = `${index * 0.2}s`;
        observer.observe(step);
    });

    // Testimonial slider
    const testimonialSlider = document.querySelector('.testimonial-slider');
    const testimonials = document.querySelectorAll('.testimonial');
    let currentTestimonial = 0;

    function showTestimonial(index) {
        testimonialSlider.style.transform = `translateX(-${index * 100}%)`;
    }

    function nextTestimonial() {
        currentTestimonial = (currentTestimonial + 1) % testimonials.length;
        showTestimonial(currentTestimonial);
    }

    setInterval(nextTestimonial, 5000);

    // Parallax effect for How It Works section
    const howItWorks = document.querySelector('.how-it-works');
    window.addEventListener('scroll', () => {
        const scrollPosition = window.pageYOffset;
        howItWorks.style.backgroundPositionY = `${scrollPosition * 0.5}px`;
    });

    // Form submission animation
    const form = document.querySelector('.contact-form');
    form.addEventListener('submit', (e) => {
        e.preventDefault();
        const button = form.querySelector('button');
        button.textContent = 'Sending...';
        button.disabled = true;
        
        // Simulate form submission
        setTimeout(() => {
            button.textContent = 'Message Sent!';
            button.style.backgroundColor = var(--accent-color);
            form.reset();
            
            setTimeout(() => {
                button.textContent = 'Send Message';
                button.style.backgroundColor = '';
                button.disabled = false;
            }, 3000);
        }, 2000);
    });

    // Floating animation for feature icons
    const featureIcons = document.querySelectorAll('.feature-card i');
    featureIcons.forEach(icon => {
        icon.style.animation = 'float 3s ease-in-out infinite';
    });
});

