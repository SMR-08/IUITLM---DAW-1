/**
 * Theme.js - Light/Dark mode toggle functionality
 * This script handles theme switching, saving preferences, and system preference detection
 */

(function() {
    // DOM elements
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeIcon = themeToggleBtn.querySelector('i');
    
    // Theme settings
    const THEMES = {
      LIGHT: 'light',
      DARK: 'dark'
    };
    
    const ICONS = {
      LIGHT: 'fa-solid fa-moon', // Show moon when in light mode (to switch to dark)
      DARK: 'fa-solid fa-sun'    // Show sun when in dark mode (to switch to light)
    };
    
    const STORAGE_KEY = 'vip-theme-preference';
    
    /**
     * Set the theme
     * @param {string} theme - 'light' or 'dark'
     */
    function setTheme(theme) {
      // Update data attribute on document
      document.documentElement.setAttribute('data-theme', theme);
      
      // Update icon
      themeIcon.className = theme === THEMES.DARK ? ICONS.DARK : ICONS.LIGHT;
      
      // Save preference
      localStorage.setItem(STORAGE_KEY, theme);
    }
    
    /**
     * Toggle between light and dark themes
     */
    function toggleTheme() {
      // Add animation class
      themeIcon.classList.add('theme-icon-animate');
      
      // Remove animation class after animation completes
      setTimeout(() => {
        themeIcon.classList.remove('theme-icon-animate');
      }, 500);
      
      // Get current theme
      const currentTheme = document.documentElement.getAttribute('data-theme') || THEMES.LIGHT;
      
      // Toggle theme
      const newTheme = currentTheme === THEMES.LIGHT ? THEMES.DARK : THEMES.LIGHT;
      
      // Set new theme
      setTheme(newTheme);
    }
    
    /**
     * Initialize theme based on saved preference or system preference
     */
    function initTheme() {
      // Check for saved preference
      const savedTheme = localStorage.getItem(STORAGE_KEY);
      
      if (savedTheme) {
        // Use saved preference
        setTheme(savedTheme);
      } else {
        // Check for system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setTheme(prefersDark ? THEMES.DARK : THEMES.LIGHT);
      }
    }
    
    /**
     * Listen for system theme changes
     */
    function listenForSystemThemeChanges() {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        // Only change theme if user hasn't set a preference
        if (!localStorage.getItem(STORAGE_KEY)) {
          setTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
        }
      });
    }
    
    // Event listeners
    themeToggleBtn.addEventListener('click', toggleTheme);
    
    // Initialize
    initTheme();
    listenForSystemThemeChanges();
  })();