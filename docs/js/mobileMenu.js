// Mobile menu functionality: hamburger toggle and responsive navigation

export function initMobileMenu() {
    const navbar = document.querySelector('.navbar');
    const navContainer = navbar.querySelector('.container');
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
            z-index: 1001;
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
                z-index: 1000;
            }
            
            .nav-links.active {
                max-height: 400px;
            }
            
            .nav-links li {
                width: 100%;
                text-align: center;
            }
            
            .nav-links a {
                display: block;
                padding: 0.75rem;
                width: 100%;
            }
        }
    `;
    document.head.appendChild(hamburgerStyle);
    
    // Insert hamburger before nav links
    navContainer.insertBefore(hamburger, navLinks);
    
    // Toggle menu
    hamburger.addEventListener('click', (e) => {
        e.stopPropagation();
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
    
    // Close menu when clicking outside
    document.addEventListener('click', (e) => {
        if (!navbar.contains(e.target)) {
            hamburger.classList.remove('active');
            navLinks.classList.remove('active');
        }
    });
}