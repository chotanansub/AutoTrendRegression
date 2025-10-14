// Animation on scroll functionality

export function initAnimations() {
    // Lazy load images (exclude hero images from fade effect)
    const images = document.querySelectorAll('img[src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                
                // Skip animation for hero section images
                if (img.closest('.hero')) {
                    observer.unobserve(img);
                    return;
                }
                
                img.style.opacity = '0';
                img.style.transition = 'opacity 0.5s';
                
                img.addEventListener('load', () => {
                    img.style.opacity = '1';
                });
                
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => {
        // Don't observe hero images
        if (!img.closest('.hero')) {
            imageObserver.observe(img);
        }
    });

    // Add animation on scroll for elements
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe elements for animation (exclude hero section elements)
    const animatedElements = document.querySelectorAll('.feature-card, .doc-section');
    
    animatedElements.forEach(el => {
        // Skip hero section elements
        if (el.closest('.hero')) {
            return;
        }
        
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
}