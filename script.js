/* =============================================
   SEGUROSCAR — Interactive Scripts (Cloudflare-Inspired)
   ============================================= */

document.addEventListener('DOMContentLoaded', () => {

    // ─── Navbar scroll effect ───
    const navbar = document.getElementById('navbar');
    const handleNavScroll = () => {
        navbar.classList.toggle('scrolled', window.scrollY > 60);
    };
    window.addEventListener('scroll', handleNavScroll, { passive: true });
    handleNavScroll();

    // ─── Mobile menu toggle ───
    const navToggle = document.getElementById('navToggle');
    const navLinks = document.getElementById('navLinks');

    navToggle.addEventListener('click', () => {
        navToggle.classList.toggle('active');
        navLinks.classList.toggle('open');
        document.body.style.overflow = navLinks.classList.contains('open') ? 'hidden' : '';
    });

    navLinks.querySelectorAll('a').forEach(link => {
        link.addEventListener('click', () => {
            navToggle.classList.remove('active');
            navLinks.classList.remove('open');
            document.body.style.overflow = '';
        });
    });

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
                        <a href="#planes" class="navbar__btn navbar__btn--cta">Comenzar</a>
                    `;
                    document.getElementById('logoutBtn').addEventListener('click', (e) => {
                        e.preventDefault();
                        fetch('/logout', { method: 'POST' }).then(() => {
                            window.location.reload();
                        });
                    });
                } else {
                    // Make sure login btn listener is re-attached if rendered again
                    const loginBtn = document.getElementById('loginBtn');
                    if(loginBtn) {
                        loginBtn.addEventListener('click', (e) => {
                            e.preventDefault();
                            openModal(true);
                        });
                    }
                }
            })
            .catch(err => console.error("Error checking auth:", err));
    }

    // Initialize check
    checkAuth();

    function openModal(loginMode) {
        isLoginMode = loginMode;
        authError.textContent = '';
        authForm.reset();
        
        if (isLoginMode) {
            modalTitle.textContent = 'Iniciar Sesión';
            authSubmit.textContent = 'Ingresar';
            authToggleText.textContent = '¿No tienes cuenta?';
            authToggleLink.textContent = 'Regístrate';
        } else {
            modalTitle.textContent = 'Crear Cuenta';
            authSubmit.textContent = 'Registrarse';
            authToggleText.textContent = '¿Ya tienes cuenta?';
            authToggleLink.textContent = 'Inicia sesión';
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
            
            authSubmit.disabled = true;
            authSubmit.textContent = 'Procesando...';

            fetch(endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            })
            .then(res => res.json().then(data => ({ status: res.status, body: data })))
            .then(res => {
                authSubmit.disabled = false;
                if (res.status >= 200 && res.status < 300) {
                    closeAuthModal();
                    checkAuth();
                } else {
                    authError.textContent = res.body.error || 'Ocurrió un error inesperado';
                    authSubmit.textContent = isLoginMode ? 'Ingresar' : 'Registrarse';
                }
            })
            .catch(err => {
                authSubmit.disabled = false;
                authError.textContent = 'Error de conexión';
                authSubmit.textContent = isLoginMode ? 'Ingresar' : 'Registrarse';
            });
        });
    }
});
