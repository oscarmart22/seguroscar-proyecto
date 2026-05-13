/* =============================================
   SEGUROSCAR — Interactive Scripts (Cloudflare-Inspired)
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {
    
    // Helper to get CSRF token from cookie
    function getCSRFToken() {
        const tag = document.querySelector('meta[name="csrf-token"]');
        return tag ? tag.getAttribute('content') : '';
    }

    // ─── Navbar scroll effect ───
    const navbar = document.getElementById('navbar');
    const handleNavScroll = () => {
        navbar.classList.toggle('scrolled', window.scrollY > 60);
    };
    window.addEventListener('scroll', handleNavScroll, { passive: true });
    handleNavScroll();

    // ─── Mobile menu toggle ───
    const navToggle = document.getElementById('navToggle');
    const mobileMenu = document.getElementById('mobile-menu');
    const closeMobileMenuBtn = document.getElementById('closeMobileMenu');

    function openMenu() {
        if(mobileMenu) mobileMenu.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeMenu() {
        if(mobileMenu) mobileMenu.classList.remove('active');
        if(navToggle) navToggle.classList.remove('active');
        document.body.style.overflow = '';
    }

    // --- Password Strength Logic ---
    const passwordInput = document.getElementById('password');
    const strengthMeter = document.getElementById('passwordStrength');
    const strengthFill = document.querySelector('.strength-meter-fill');
    const strengthText = document.getElementById('passwordStrengthText');

    if (passwordInput) {
        passwordInput.addEventListener('input', () => {
            // Only show strength meter for registration
            if (isLoginMode) {
                if (strengthMeter) strengthMeter.style.display = 'none';
                if (strengthText) strengthText.style.display = 'none';
                return;
            }
            const val = passwordInput.value;
            if (!val) {
                if (strengthMeter) strengthMeter.style.display = 'none';
                if (strengthText) strengthText.style.display = 'none';
                return;
            }
            if (strengthMeter) strengthMeter.style.display = 'block';
            if (strengthText) strengthText.style.display = 'block';
            
            let score = 0;
            if (val.length >= 8) score++;
            if (/[0-9]/.test(val)) score++;
            if (/[^A-Za-z0-9]/.test(val)) score++;
            
            let color = '#ff4d6a'; // weak
            let width = '33%';
            let label = 'Débil';
            
            if (score === 2) {
                color = '#ffd166'; // medium
                width = '66%';
                label = 'Media';
            } else if (score === 3) {
                color = '#00ffa3'; // strong
                width = '100%';
                label = 'Fuerte';
            }
            
            if (strengthFill) {
                strengthFill.style.width = width;
                strengthFill.style.backgroundColor = color;
            }
            if (strengthText) {
                strengthText.textContent = 'Fuerza: ' + label;
                strengthText.style.color = color;
            }
        });
    }

    if (navToggle) {
        navToggle.addEventListener('click', () => {
            navToggle.classList.add('active');
            openMenu();
        });
    }

    if (closeMobileMenuBtn) {
        closeMobileMenuBtn.addEventListener('click', closeMenu);
    }

    if (mobileMenu) {
        mobileMenu.querySelectorAll('a').forEach(link => {
            link.addEventListener('click', closeMenu);
        });
    }

    // ─── Smooth scroll for nav links ───
    document.querySelectorAll('a[href^="#"], a[href^="/#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            if (window.location.pathname !== '/' && window.location.pathname !== '/index.html') {
                return; // Let default navigation happen if not on main page
            }
            const href = this.getAttribute('href').replace('/', '');
            if (href === '#') return;
            const target = document.querySelector(href);
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    });

    // ─── Rotating Hero Text ───
    const rotatingText = document.getElementById('rotatingText');
    if (rotatingText) {
        const words = ['proteger', 'monitorear', 'blindar', 'encriptar', 'asegurar'];
        let currentIndex = 0;

        setInterval(() => {
            rotatingText.classList.add('fade-out');

            setTimeout(() => {
                currentIndex = (currentIndex + 1) % words.length;
                rotatingText.textContent = words[currentIndex];
                rotatingText.classList.remove('fade-out');
                rotatingText.classList.add('fade-in');

                setTimeout(() => {
                    rotatingText.classList.remove('fade-in');
                }, 400);
            }, 400);
        }, 2800);
    }

    // ─── Product Tabs ───
    const tabButtons = document.querySelectorAll('.product-tabs__tab');
    const tabPanels = document.querySelectorAll('.product-tabs__panel');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.dataset.tab;

            // Remove active from all tabs and panels
            tabButtons.forEach(b => b.classList.remove('product-tabs__tab--active'));
            tabPanels.forEach(p => p.classList.remove('product-tabs__panel--active'));

            // Activate clicked tab and corresponding panel
            btn.classList.add('product-tabs__tab--active');
            const panel = document.getElementById(`tab-${tabId}`);
            if (panel) {
                panel.classList.add('product-tabs__panel--active');
            }
        });
    });

    // ─── Scroll Reveal (Intersection Observer) ───
    const revealElements = document.querySelectorAll('.reveal');
    const revealObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.classList.add('visible');
                }, index * 80);
                revealObserver.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.12,
        rootMargin: '0px 0px -40px 0px'
    });

    revealElements.forEach(el => revealObserver.observe(el));

    // ─── Counter Animation (stats grid) ───
    const counters = document.querySelectorAll('.stats-grid__number[data-target]');
    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                animateCounter(entry.target);
                counterObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    counters.forEach(counter => counterObserver.observe(counter));

    function animateCounter(el) {
        const target = parseInt(el.dataset.target, 10);
        const duration = 1800;
        const startTime = performance.now();

        function update(currentTime) {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);
            const eased = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(target * eased);
            if (progress < 1) requestAnimationFrame(update);
        }
        requestAnimationFrame(update);
    }

    // ─── Video Explicativo Play Button ───
    const videoPlayer = document.getElementById('videoExplicativo');
    const videoPlayBtn = document.getElementById('videoPlayBtn');

    if (videoPlayer && videoPlayBtn) {
        let videoStarted = false;

        videoPlayBtn.addEventListener('click', () => {
            videoPlayer.play();
            videoPlayBtn.classList.add('hidden');
            videoStarted = true;
        });

        videoPlayer.addEventListener('play', () => {
            if (!videoStarted) {
                videoPlayBtn.classList.add('hidden');
                videoStarted = true;
            }
        });

        videoPlayer.addEventListener('ended', () => {
            videoStarted = false;
            videoPlayBtn.classList.remove('hidden');
        });
    }

    // ─── Parallax effect for hero video on scroll ───
    const heroVideo = document.querySelector('.hero-section__video');
    if (heroVideo) {
        window.addEventListener('scroll', () => {
            const scrollY = window.scrollY;
            const heroHeight = document.querySelector('.hero-section').offsetHeight;
            if (scrollY < heroHeight) {
                const progress = scrollY / heroHeight;
                heroVideo.style.opacity = Math.max(0.85 - progress * 0.6, 0.05);
                heroVideo.style.transform = `translate(-50%, -50%) scale(${1.2 + progress * 0.1})`;
            }
        }, { passive: true });
    }

    // ─── Navbar active link highlight on scroll ───
    const sections = document.querySelectorAll('section[id]');
    const navLinkElements = document.querySelectorAll('.navbar__link');

    function highlightNavLink() {
        const scrollPos = window.scrollY + 150;

        sections.forEach(section => {
            const top = section.offsetTop;
            const height = section.offsetHeight;
            const id = section.getAttribute('id');

            if (scrollPos >= top && scrollPos < top + height) {
                navLinkElements.forEach(link => {
                    link.classList.remove('active');
                    const href = link.getAttribute('href');
                    if (href === `#${id}` || href === `/#${id}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }

    window.addEventListener('scroll', highlightNavLink, { passive: true });

    // ─── Contact Form Validation ───
    const contactForm = document.getElementById('contactForm');
    const submitBtn = document.getElementById('submitBtn');

    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const name = document.getElementById('name').value.trim();
            const email = document.getElementById('email').value.trim();
            const message = document.getElementById('message').value.trim();

            if (!name || !email || !message) {
                showFormMessage('Por favor completa todos los campos requeridos.', 'error');
                return;
            }

            if (!isValidEmail(email)) {
                showFormMessage('Por favor ingresa un correo electrónico válido.', 'error');
                return;
            }

            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span>Enviando...</span>';

            setTimeout(() => {
                showFormMessage('¡Mensaje enviado exitosamente! Nos pondremos en contacto pronto.', 'success');
                contactForm.reset();
                submitBtn.disabled = false;
                submitBtn.innerHTML = `<span>Enviar Mensaje</span>
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>`;
            }, 1500);
        });
    }

    function isValidEmail(email) {
        return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
    }

    function showFormMessage(msg, type) {
        const existing = document.querySelector('.form-message');
        if (existing) existing.remove();

        const div = document.createElement('div');
        div.className = `form-message form-message--${type}`;
        div.textContent = msg;
        div.style.cssText = `
            padding: 0.75rem 1rem;
            border-radius: 8px;
            font-size: 0.875rem;
            margin-top: 1rem;
            background: ${type === 'error' ? 'rgba(255, 77, 106, 0.1)' : 'rgba(0, 255, 163, 0.1)'};
            color: ${type === 'error' ? '#ff4d6a' : '#00ffa3'};
            border: 1px solid ${type === 'error' ? 'rgba(255, 77, 106, 0.2)' : 'rgba(0, 255, 163, 0.2)'};
        `;
        contactForm.appendChild(div);

        setTimeout(() => div.remove(), 5000);
    }

});

/* =============================================
   AUTHENTICATION LOGIC (Login/Register)
   ============================================= */
document.addEventListener('DOMContentLoaded', () => {
    const authSection = document.getElementById('authSection');
    const authModal = document.getElementById('authModal');
    const closeModalBtn = document.getElementById('closeModal');
    const authForm = document.getElementById('authForm');
    const authToggleLink = document.getElementById('authToggleLink');
    const modalTitle = document.getElementById('modalTitle');
    const authSubmit = document.getElementById('authSubmit');
    const authToggleText = document.getElementById('authToggleText');
    const authError = document.getElementById('authError');
    
    let isLoginMode = true;

    // Check user session
    function checkAuth() {
        fetch('/api/me')
            .then(res => res.json())
            .then(data => {
                if (data.logged_in) {
                    authSection.innerHTML = `
                        <span style="color: var(--color-text-heading); font-weight: 600; margin-right: 1rem;">Hola, ${data.username}</span>
                        <a href="#" id="logoutBtn" class="navbar__btn navbar__btn--outline" style="border: 1px solid var(--color-danger); color: var(--color-danger);">Cerrar Sesión</a>
                    `;
                    document.getElementById('logoutBtn').addEventListener('click', (e) => {
                        e.preventDefault();
                        fetch('/logout', { 
                            method: 'POST',
                            headers: { 'X-CSRFToken': getCSRFToken() }
                        }).then(() => {
                            window.location.reload();
                        });
                    });
                    
                    const mobileAuth = document.getElementById('mobileOverlayAuthContainer');
                    if (mobileAuth) {
                        mobileAuth.innerHTML = `
                            <span class="mobile-menu-link" style="color: var(--color-text-heading); font-weight: 600;">Hola, ${data.username}</span>
                            <a href="#" id="mobileLogoutBtn" class="mobile-menu-link" style="color: var(--color-danger);">Cerrar Sesión</a>
                        `;
                        document.getElementById('mobileLogoutBtn').addEventListener('click', (e) => {
                            e.preventDefault();
                            fetch('/logout', { method: 'POST' }).then(() => window.location.reload());
                        });
                    }
                } else {
                    // Make sure login btn listener is re-attached if rendered again
                    const loginBtn = document.getElementById('loginBtn');
                    if(loginBtn) {
                        loginBtn.addEventListener('click', (e) => {
                            e.preventDefault();
                            openModal(true);
                        });
                    }
                    
                    const mobileAuth = document.getElementById('mobileOverlayAuthContainer');
                    if (mobileAuth) {
                        mobileAuth.innerHTML = `<a href="/login" class="mobile-menu-link" id="mobileLoginBtnFallback">Iniciar Sesión</a>`;
                        const fb = document.getElementById('mobileLoginBtnFallback');
                        if (fb) {
                            fb.addEventListener('click', (e) => {
                                e.preventDefault();
                                openModal(true);
                                if (typeof closeMenu === 'function') closeMenu();
                            });
                        }
                    }
                }
            })
            .catch(err => console.error("Error checking auth:", err));
    }

    // Initialize check
    checkAuth();

    // Auto-open modal if URL path is /login or /register
    if (window.location.pathname === '/login') {
        openModal(true);
    } else if (window.location.pathname === '/register') {
        openModal(false);
    }

    function openModal(loginMode) {
        isLoginMode = loginMode;
        authError.textContent = '';
        authForm.reset();
        
        const confirmGroup = document.getElementById('confirmPasswordGroup');
        const confirmInput = document.getElementById('confirm_password');

        if (isLoginMode) {
            modalTitle.textContent = 'Iniciar Sesión';
            authSubmit.textContent = 'Ingresar';
            authToggleText.textContent = '¿No tienes cuenta?';
            authToggleLink.textContent = 'Regístrate';
            if (confirmGroup) confirmGroup.style.display = 'none';
            if (confirmInput) confirmInput.required = false;
        } else {
            modalTitle.textContent = 'Crear Cuenta';
            authSubmit.textContent = 'Registrarse';
            authToggleText.textContent = '¿Ya tienes cuenta?';
            authToggleLink.textContent = 'Inicia sesión';
            if (confirmGroup) confirmGroup.style.display = 'block';
            if (confirmInput) confirmInput.required = true;
        }
        
        authModal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeAuthModal() {
        authModal.classList.remove('active');
        document.body.style.overflow = '';
    }

    if(closeModalBtn) {
        closeModalBtn.addEventListener('click', closeAuthModal);
    }
    
    if(authModal) {
        authModal.addEventListener('click', (e) => {
            if (e.target === authModal) closeAuthModal();
        });
    }

    if(authToggleLink) {
        authToggleLink.addEventListener('click', (e) => {
            e.preventDefault();
            openModal(!isLoginMode);
        });
    }

    if(authForm) {
        authForm.addEventListener('submit', (e) => {
            e.preventDefault();
            authError.textContent = '';
            
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const endpoint = isLoginMode ? '/login' : '/register';
            
            const payload = { username, password };
            if (!isLoginMode) {
                payload.confirm_password = document.getElementById('confirm_password').value;
            }

            authSubmit.disabled = true;
            authSubmit.textContent = 'Procesando...';

            fetch(endpoint, {
                method: 'POST',
                headers: { 
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(payload)
            })
            .then(res => {
                return res.json()
                    .catch(() => ({ error: 'Respuesta inválida del servidor' }))
                    .then(data => ({ status: res.status, body: data }));
            })
            .then(res => {
                authSubmit.disabled = false;
                if (res.status >= 200 && res.status < 300) {
                    const urlParams = new URLSearchParams(window.location.search);
                    const nextUrl = urlParams.get('next');
                    if (nextUrl) {
                        window.location.href = nextUrl;
                    } else {
                        closeAuthModal();
                        checkAuth();
                        if (window.location.pathname === '/login' || window.location.pathname === '/register') {
                            window.location.href = '/';
                        }
                    }
                } else {
                    authError.textContent = res.body.error || 'Error en la petición';
                    authSubmit.textContent = isLoginMode ? 'Ingresar' : 'Registrarse';
                }
            })
            .catch(err => {
                authSubmit.disabled = false;
                authError.textContent = 'Error de conexión o seguridad';
                authSubmit.textContent = isLoginMode ? 'Ingresar' : 'Registrarse';
                console.error("Auth Error:", err);
            });
        });
    }
});
