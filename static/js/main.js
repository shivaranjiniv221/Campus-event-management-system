document.addEventListener('DOMContentLoaded', () => {
    console.log('CampusEvents loaded!');

    // Subtle parallax effect for hero
    const hero = document.querySelector('.hero');
    window.addEventListener('scroll', () => {
        const scroll = window.pageYOffset;
        if (hero) {
            hero.style.backgroundPositionY = `${scroll * 0.5}px`;
        }
    });

    // Dark/Light Theme Switcher Logic
    const themeBtn = document.getElementById('themeToggleBtn');
    const themeIcon = document.getElementById('themeToggleIcon');
    const themeText = document.getElementById('themeToggleText');
    const body = document.body;

    // Load theme setting from localStorage
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'light') {
        body.classList.add('light-theme');
        if (themeIcon) themeIcon.textContent = '☀️';
        if (themeText) themeText.textContent = 'Light Mode';
    }

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            body.classList.toggle('light-theme');
            const isLight = body.classList.contains('light-theme');
            
            if (isLight) {
                localStorage.setItem('theme', 'light');
                if (themeIcon) themeIcon.textContent = '☀️';
                if (themeText) themeText.textContent = 'Light Mode';
            } else {
                localStorage.setItem('theme', 'dark');
                if (themeIcon) themeIcon.textContent = '🌙';
                if (themeText) themeText.textContent = 'Dark Mode';
            }
        });
    }
});
