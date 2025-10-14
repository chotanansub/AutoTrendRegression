// Main entry point - imports and initializes all modules

import { initNavigation } from './navigation.js';
import { initMobileMenu } from './mobileMenu.js';
import { initCopyFunctionality } from './copyFunctionality.js';
import { initBackToTop } from './backToTop.js';
import { initAnimations } from './animations.js';

// Initialize all modules when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initNavigation();
    initMobileMenu();
    initCopyFunctionality();
    initBackToTop();
    initAnimations();
    
    // Console message
    console.log('%c📈 AutoTrend', 'font-size: 20px; font-weight: bold; color: #2563eb;');
    console.log('%cLocal Linear Trend Extraction for Time Series', 'font-size: 14px; color: #6b7280;');
    console.log('%cGitHub: https://github.com/chotanansub/autotrend', 'font-size: 12px; color: #3b82f6;');
});