import { createContext, useContext, useState, useEffect } from "react";

// Create a Context for the theme
const ThemeContext = createContext();

// ThemeProvider component to wrap the application
export function ThemeProvider({ children }) {
  // State to hold the current theme ('light' or 'dark')
  const [theme, setTheme] = useState(() => {
    // Initialize theme from localStorage or system preference
    if (typeof window !== "undefined") {
      // Check localStorage first
      const storedTheme = localStorage.getItem("theme");
      if (storedTheme) {
        return storedTheme;
      }
      // If no theme in localStorage, check system preference
      return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
    }
    // Default to light theme if window is not defined (e.g., during SSR)
    return "light";
  });

  // Effect to apply the theme class to the root HTML element and update localStorage
  useEffect(() => {
    const root = document.documentElement;
    if (theme === "dark") {
      // Add the dark theme class
      root.classList.add("dark-theme");
    } else {
      // Remove the dark theme class
      root.classList.remove("dark-theme");
    }
    // Update the theme in localStorage
    localStorage.setItem("theme", theme);
  }, [theme]); // Re-run effect when the theme state changes

  // Function to toggle between light and dark themes
  const toggleTheme = () => {
    setTheme(currentTheme => (currentTheme === "dark" ? "light" : "dark"));
  };

  // Provide the theme state and toggle function to the context
  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// Custom hook to easily access the theme context
export function useTheme() {
  const context = useContext(ThemeContext);
  // Throw an error if the hook is not used within a ThemeProvider
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider");
  }
  return context;
}