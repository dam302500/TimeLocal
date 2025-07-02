// TimeLocal - Client JavaScript pour Hostinger Business
(function() {
    'use strict';
    
    // Configuration - REMPLACEZ par l'URL de votre API
    const CONFIG = {
        API_BASE: 'https://YOUR_API_URL', // Remplacez par votre URL API
        WEBSOCKET_URL: 'https://YOUR_API_URL/socket.io',
        VERSION: '2.0.0',
        LOCAL_API: '/app' // Fallback local
    };
    
    // Détection de l'environnement
    const isProduction = window.location.hostname !== 'localhost';
    const API_URL = isProduction ? CONFIG.API_BASE : CONFIG.LOCAL_API;
    
    // Utility functions
    const utils = {
        // Smooth scroll to element
        scrollTo: function(element) {
            if (element) {
                element.scrollIntoView({ 
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        },
        
        // Debounce function
        debounce: function(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        },
        
        // Show loading state
        showLoading: function(button) {
            const originalText = button.textContent;
            button.innerHTML = '<span class="loading"></span> Chargement...';
            button.disabled = true;
            
            return function hideLoading() {
                button.innerHTML = originalText;
                button.disabled = false;
            };
        },
        
        // API call helper
        apiCall: async function(endpoint, options = {}) {
            const url = `${API_URL}${endpoint}`;
            const defaultOptions = {
                headers: {
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                credentials: 'include' // Pour les cookies de session
            };
            
            const finalOptions = { ...defaultOptions, ...options };
            
            try {
                const response = await fetch(url, finalOptions);
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                const contentType = response.headers.get('content-type');
                if (contentType && contentType.includes('application/json')) {
                    return await response.json();
                }
                
                return await response.text();
            } catch (error) {
                console.error('API call failed:', error);
                throw error;
            }
        }
    };
    
    // DOM Ready
    document.addEventListener('DOMContentLoaded', function() {
        initializeApp();
    });
    
    function initializeApp() {
        // Initialize smooth scrolling for anchor links
        initSmoothScrolling();
        
        // Initialize app access button
        initAppAccess();
        
        // Initialize animations
        initAnimations();
        
        // Initialize PWA
        initPWA();
        
        // Check API connectivity
        checkAPIConnectivity();
        
        console.log(`TimeLocal v${CONFIG.VERSION} initialized`);
        console.log(`API URL: ${API_URL}`);
    }
    
    // Check API connectivity
    async function checkAPIConnectivity() {
        try {
            await utils.apiCall('/health');
            console.log('✅ API connectivity: OK');
            
            // Show online indicator
            showConnectionStatus('online');
        } catch (error) {
            console.warn('⚠️ API connectivity: Failed', error);
            
            // Show offline indicator
            showConnectionStatus('offline');
        }
    }
    
    // Show connection status
    function showConnectionStatus(status) {
        const indicator = document.createElement('div');
        indicator.className = `connection-status ${status}`;
        indicator.innerHTML = status === 'online' 
            ? '🟢 API connectée' 
            : '🔴 API déconnectée';
        
        indicator.style.cssText = `
            position: fixed;
            top: 10px;
            right: 10px;
            padding: 8px 12px;
            border-radius: 20px;
            font-size: 12px;
            z-index: 1000;
            color: white;
            background: ${status === 'online' ? '#10b981' : '#ef4444'};
        `;
        
        document.body.appendChild(indicator);
        
        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (indicator.parentNode) {
                indicator.remove();
            }
        }, 3000);
    }
    
    // Smooth scrolling for internal links
    function initSmoothScrolling() {
        const links = document.querySelectorAll('a[href^="#"]');
        
        links.forEach(link => {
            link.addEventListener('click', function(e) {
                e.preventDefault();
                const targetId = this.getAttribute('href').substring(1);
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    utils.scrollTo(targetElement);
                }
            });
        });
    }
    
    // App access functionality
    function initAppAccess() {
        const appButton = document.querySelector('a[href="/app"]');
        
        if (appButton) {
            appButton.addEventListener('click', async function(e) {
                e.preventDefault();
                
                const hideLoading = utils.showLoading(this);
                
                try {
                    // Check if app is available
                    await utils.apiCall('/health');
                    
                    // Redirect to app
                    window.location.href = '/app';
                } catch (error) {
                    console.error('App access error:', error);
                    
                    // Show user-friendly error
                    const message = error.message.includes('Failed to fetch') 
                        ? 'L\'application n\'est pas encore disponible. Veuillez vérifier la configuration de l\'API.'
                        : 'Erreur de connexion à l\'application. Veuillez réessayer plus tard.';
                    
                    alert(message);
                } finally {
                    hideLoading();
                }
            });
        }
    }
    
    // Initialize animations
    function initAnimations() {
        // Intersection Observer for fade-in animations
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };
        
        const observer = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, observerOptions);
        
        // Observe elements for animation
        const animatedElements = document.querySelectorAll('.feature, .stat');
        animatedElements.forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(20px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }
    
    // Progressive Web App functionality
    function initPWA() {
        // Register service worker
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js')
                .then(registration => {
                    console.log('SW registered:', registration);
                })
                .catch(error => {
                    console.log('SW registration failed:', error);
                });
        }
        
        // Handle app install prompt
        let deferredPrompt;
        
        window.addEventListener('beforeinstallprompt', (e) => {
            e.preventDefault();
            deferredPrompt = e;
            showInstallButton();
        });
        
        function showInstallButton() {
            const installButton = document.createElement('button');
            installButton.textContent = '📱 Installer l\'app';
            installButton.className = 'btn btn-secondary install-btn';
            installButton.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                z-index: 1000;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            `;
            
            installButton.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const { outcome } = await deferredPrompt.userChoice;
                    
                    if (outcome === 'accepted') {
                        console.log('User accepted the install prompt');
                    }
                    
                    deferredPrompt = null;
                    installButton.remove();
                }
            });
            
            document.body.appendChild(installButton);
            
            // Auto-hide after 10 seconds
            setTimeout(() => {
                if (installButton.parentNode) {
                    installButton.remove();
                }
            }, 10000);
        }
    }
    
    // Performance monitoring
    window.addEventListener('load', function() {
        // Log performance metrics
        if ('performance' in window) {
            const perfData = performance.getEntriesByType('navigation')[0];
            console.log('Page load time:', perfData.loadEventEnd - perfData.fetchStart, 'ms');
        }
    });
    
    // Error handling
    window.addEventListener('error', function(e) {
        console.error('Global error:', e.error);
        // Could send to error reporting service
    });
    
    // Expose utils for debugging
    window.TimeLocal = {
        utils: utils,
        config: CONFIG,
        version: CONFIG.VERSION,
        apiUrl: API_URL
    };
})();