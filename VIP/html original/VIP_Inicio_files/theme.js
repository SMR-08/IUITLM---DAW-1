(function() {
    const themeToggleBtn = document.getElementById('theme-toggle-btn');
    const themeIcon = themeToggleBtn.querySelector('i');
    
    const THEMES = {
      LIGHT: 'light',
      DARK: 'dark'
    };
    
    const ICONS = {
      LIGHT: 'fa-solid fa-moon',
      DARK: 'fa-solid fa-sun'
    };
    
    const STORAGE_KEY = 'vip-theme-preference';
    
    function setTheme(theme) {
      document.documentElement.setAttribute('data-theme', theme);
      themeIcon.className = theme === THEMES.DARK ? ICONS.DARK : ICONS.LIGHT;
      localStorage.setItem(STORAGE_KEY, theme);
    }
    
    function toggleTheme() {
      themeIcon.classList.add('theme-icon-animate');
      
      setTimeout(() => {
        themeIcon.classList.remove('theme-icon-animate');
      }, 500);
      
      const currentTheme = document.documentElement.getAttribute('data-theme') || THEMES.LIGHT;
      const newTheme = currentTheme === THEMES.LIGHT ? THEMES.DARK : THEMES.LIGHT;
      
      setTheme(newTheme);
    }
    
    function initTheme() {
      const savedTheme = localStorage.getItem(STORAGE_KEY);
      
      if (savedTheme) {
        setTheme(savedTheme);
      } else {
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
        setTheme(prefersDark ? THEMES.DARK : THEMES.LIGHT);
      }
    }
    
    function listenForSystemThemeChanges() {
      window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
        if (!localStorage.getItem(STORAGE_KEY)) {
          setTheme(e.matches ? THEMES.DARK : THEMES.LIGHT);
        }
      });
    }
    
    themeToggleBtn.addEventListener('click', toggleTheme);
    
    initTheme();
    listenForSystemThemeChanges();
  })();