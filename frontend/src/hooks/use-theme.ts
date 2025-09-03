import { useTheme as useNextThemes } from "next-themes";

export function useTheme() {
  return useNextThemes();
}

// Helper function for theme-aware class names
export function themeClasses(
  lightClasses: string,
  darkClasses: string
): string {
  return `${lightClasses} dark:${darkClasses}`;
}
