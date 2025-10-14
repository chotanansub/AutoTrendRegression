// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            const navHeight = document.querySelector('.navbar').offsetHeight;
            const targetPosition = target.offsetTop - navHeight;
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    });
});

// Active navigation link highlighting
const sections = document.querySelectorAll('section');
const navLinks = document.querySelectorAll('.nav-links a');

function updateActiveNavLink() {
    let currentSection = '';
    const navHeight = document.querySelector('.navbar').offsetHeight;
    
    sections.forEach(section => {
        const sectionTop = section.offsetTop - navHeight - 100;
        const sectionHeight = section.offsetHeight;
        
        if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
            currentSection = section.getAttribute('id');
        }
    });
    
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('href') === `#${currentSection}`) {
            link.classList.add('active');
        }
    });
}

window.addEventListener('scroll', updateActiveNavLink);
window.addEventListener('load', updateActiveNavLink);

// Copy functionality for installation box - IMPROVED VERSION
function initializeInstallCopyButton() {
    const installCopyBtn = document.querySelector('.install-copy-btn');
    
    if (!installCopyBtn) {
        console.log('Install copy button not found');
        return;
    }
    
    installCopyBtn.addEventListener('click', function(e) {
        e.preventDefault();
        const command = 'pip install autotrend';
        
        // Try modern clipboard API first
        if (navigator.clipboard && navigator.clipboard.writeText) {
            navigator.clipboard.writeText(command).then(() => {
                // Success
                installCopyBtn.innerHTML = '<i class="fas fa-check"></i>';
                installCopyBtn.classList.add('copied');
                
                setTimeout(() => {
                    installCopyBtn.innerHTML = '<i class="fas fa-copy"></i>';
                    installCopyBtn.classList.remove('copied');
                }, 2000);
            }).catch(err => {
                console.error('Clipboard API failed:', err);
                fallbackCopy(command, installCopyBtn);
            });
        } else {
            // Use fallback for browsers without Clipboard API
            fallbackCopy(command, installCopyBtn);
        }
    });
}

// Fallback copy method for older browsers or when Clipboard API fails
function fallbackCopy(text, button) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = '0';
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            button.innerHTML = '<i class="fas fa-check"></i>';
            button.classList.add('copied');
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-copy"></i>';
                button.classList.remove('copied');
            }, 2000);
        } else {
            console.error('Fallback copy failed');
            alert('Copy failed. Please copy manually: ' + text);
        }
    } catch (err) {
        console.error('Fallback copy error:', err);
        alert('Copy failed. Please copy manually: ' + text);
    }
    
    document.body.removeChild(textArea);
}

// Initialize install copy button when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeInstallCopyButton);
} else {
    initializeInstallCopyButton();
}

// Copy code block functionality - IMPROVED VERSION
function initializeCodeBlockCopy() {
    document.querySelectorAll('pre code').forEach(block => {
        const pre = block.parentElement;
        
        // Check if button already exists
        if (pre.querySelector('.copy-button')) {
            return;
        }
        
        // Create copy button
        const copyButton = document.createElement('button');
        copyButton.className = 'copy-button';
        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
        copyButton.title = 'Copy to clipboard';
        
        // Add button to pre element
        pre.style.position = 'relative';
        pre.appendChild(copyButton);
        
        // Copy functionality
        copyButton.addEventListener('click', function(e) {
            e.preventDefault();
            const code = block.textContent;
            
            if (navigator.clipboard && navigator.clipboard.writeText) {
                navigator.clipboard.writeText(code).then(() => {
                    copyButton.innerHTML = '<i class="fas fa-check"></i>';
                    copyButton.style.color = '#10b981';
                    
                    setTimeout(() => {
                        copyButton.innerHTML = '<i class="fas fa-copy"></i>';
                        copyButton.style.color = '';
                    }, 2000);
                }).catch(err => {
                    console.error('Code copy failed:', err);
                    fallbackCopyCode(code, copyButton);
                });
            } else {
                fallbackCopyCode(code, copyButton);
            }
        });
    });
}

function fallbackCopyCode(code, button) {
    const textArea = document.createElement('textarea');
    textArea.value = code;
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();
    
    try {
        const successful = document.execCommand('copy');
        if (successful) {
            button.innerHTML = '<i class="fas fa-check"></i>';
            button.style.color = '#10b981';
            setTimeout(() => {
                button.innerHTML = '<i class="fas fa-copy"></i>';
                button.style.color = '';
            }, 2000);
        }
    } catch (err) {
        console.error('Fallback code copy failed:', err);
    }
    
    document.body.removeChild(textArea);
}

// Initialize code block copy when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeCodeBlockCopy);
} else {
    initializeCodeBlockCopy();
}

// Add CSS for copy buttons dynamically
const style = document.createElement('style');
style.textContent = `
    pre {
        position: relative;
    }
    
    .copy-button {
        position: absolute;
        top: 10px;
        right: 10px;
        background-color: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        color: #e2e8f0;
        padding: 0.5rem 0.75rem;
        border-radius: 6px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.3s;
        opacity: 0;
        z-index: 10;
    }
    
    pre:hover .copy-button {
        opacity: 1;
    }
    
    .copy-button:hover {
        background-color: rgba(255, 255, 255, 0.2);
        border-color: rgba(255, 255, 255, 0.3);
    }
    
    .copy-button:active {
        transform: scale(0.95);
    }
`;
document.head.appendChild(style);

// Lazy load images - FIXED VERSION (exclude badges)
document.addEventListener('DOMContentLoaded', () => {
    // Only lazy load large images, not badges
    const images = document.querySelectorAll('img[src]:not(.badges img)');
    const demoGif = document.querySelector('.demo-gif');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                
                // Don't apply fade animation if already loaded
                if (!img.complete) {
                    img.style.opacity = '0';
                    img.style.transition = 'opacity 0.5s';
                    
                    img.addEventListener('load', () => {
                        img.style.opacity = '1';
                    });
                } else {
                    img.style.opacity = '1';
                }
                
                observer.unobserve(img);
            }
        });
    });
    
    // Only observe the demo GIF, not the badges
    if (demoGif) {
        imageObserver.observe(demoGif);
    }
});

// Back to top button
const backToTopButton = document.createElement('button');
backToTopButton.id = 'back-to-top';
backToTopButton.innerHTML = '<i class="fas fa-arrow-up"></i>';
backToTopButton.title = 'Back to top';
document.body.appendChild(backToTopButton);

// Back to top button styles
const backToTopStyle = document.createElement('style');
backToTopStyle.textContent = `
    #back-to-top {
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background-color: var(--primary-color);
        color: white;
        border: none;
        cursor: pointer;
        font-size: 1.2rem;
        box-shadow: var(--shadow-lg);
        transition: all 0.3s;
        opacity: 0;
        visibility: hidden;
        z-index: 999;
    }
    
    #back-to-top.visible {
        opacity: 1;
        visibility: visible;
    }
    
    #back-to-top:hover {
        background-color: var(--secondary-color);
        transform: translateY(-3px);
    }
    
    #back-to-top:active {
        transform: translateY(-1px);
    }
    
    @media (max-width: 768px) {
        #back-to-top {
            bottom: 20px;
            right: 20px;
            width: 45px;
            height: 45px;
            font-size: 1rem;
        }
    }
`;
document.head.appendChild(backToTopStyle);

// Show/hide back to top button
window.addEventListener('scroll', () => {
    if (window.scrollY > 300) {
        backToTopButton.classList.add('visible');
    } else {
        backToTopButton.classList.remove('visible');
    }
});

// Back to top functionality
backToTopButton.addEventListener('click', () => {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
});

// Add animation on scroll - EXCLUDE HERO SECTION
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

// Observe elements for animation - EXCLUDE elements in hero section
document.addEventListener('DOMContentLoaded', () => {
    const animatedElements = document.querySelectorAll('.feature-card, .doc-section');
    
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(20px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
});

// Mobile menu toggle
const createMobileMenu = () => {
    const nav = document.querySelector('.navbar');
    const navLinks = document.querySelector('.nav-links');
    
    // Create hamburger button
    const hamburger = document.createElement('button');
    hamburger.className = 'hamburger';
    hamburger.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;
    
    // Add styles for hamburger
    const hamburgerStyle = document.createElement('style');
    hamburgerStyle.textContent = `
        .hamburger {
            display: none;
            flex-direction: column;
            gap: 4px;
            background: none;
            border: none;
            cursor: pointer;
            padding: 5px;
        }
        
        .hamburger span {
            width: 25px;
            height: 3px;
            background-color: var(--text-color);
            transition: all 0.3s;
            border-radius: 2px;
        }
        
        .hamburger.active span:nth-child(1) {
            transform: rotate(45deg) translate(5px, 5px);
        }
        
        .hamburger.active span:nth-child(2) {
            opacity: 0;
        }
        
        .hamburger.active span:nth-child(3) {
            transform: rotate(-45deg) translate(7px, -6px);
        }
        
        @media (max-width: 768px) {
            .hamburger {
                display: flex;
            }
            
            .nav-links {
                position: absolute;
                top: 100%;
                left: 0;
                right: 0;
                background-color: white;
                flex-direction: column;
                padding: 1rem;
                box-shadow: var(--shadow);
                max-height: 0;
                overflow: hidden;
                transition: max-height 0.3s ease;
            }
            
            .nav-links.active {
                max-height: 300px;
            }
        }
    `;
    document.head.appendChild(hamburgerStyle);
    
    // Insert hamburger before nav links
    nav.querySelector('.container').insertBefore(hamburger, navLinks);
    
    // Toggle menu
    hamburger.addEventListener('click', () => {
        hamburger.classList.toggle('active');
        navLinks.classList.toggle('active');
    });
    
    // Close menu when clicking a link
    document.querySelectorAll('.nav-links a').forEach(link => {
        link.addEventListener('click', () => {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
        });
    });
};

// Initialize mobile menu
createMobileMenu();

// Console message
console.log('%c📈 AutoTrend', 'font-size: 20px; font-weight: bold; color: #2563eb;');
console.log('%cLocal Linear Trend Extraction for Time Series', 'font-size: 14px; color: #6b7280;');
console.log('%cGitHub: https://github.com/chotanansub/autotrend', 'font-size: 12px; color: #3b82f6;');