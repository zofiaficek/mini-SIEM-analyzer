import { initDashboard } from './dashboard.js';
import { initAdmin } from './admin.js';

function setupTheme() {
    const htmlElement = document.getElementById('mainHtml');
    const themeToggle = document.getElementById('themeToggle');
    const themeIcon = document.getElementById('themeIcon');

    // 1. Pobierz zapisany motyw lub sprawdź preferencje systemowe
    const savedTheme = localStorage.getItem('theme') || 
                      (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');

    // 2. Funkcja aplikująca motyw
    const applyTheme = (theme) => {
        htmlElement.setAttribute('data-bs-theme', theme);
        localStorage.setItem('theme', theme);
        themeIcon.textContent = theme === 'dark' ? '☀️' : '🌙';
    };

    // Uruchom przy starcie
    applyTheme(savedTheme);

    // 3. Obsługa kliknięcia
    if (themeToggle) {
        themeToggle.addEventListener('click', () => {
            const currentTheme = htmlElement.getAttribute('data-bs-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        });
    }
}

function main() {
    
    // Inicjalizacja motywu dla każdej strony
    setupTheme();
    const path = window.location.pathname;

    if (path === '/' || path === '/index') {
        console.log("Inicjalizacja Dashboardu");
        initDashboard();
    } 
    else if (path === '/config') {
        console.log("Inicjalizacja Panelu Admina");
        initAdmin();
    }
}

main();