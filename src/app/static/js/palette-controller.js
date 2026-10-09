/**
 * DIGITVISION AI — Elite Palette & Mode Controller
 * Apple Pro Design & Precision Switcher
 */

export const ELITE_PALETTES = {
  OBSIDIAN: "studio-obsidian",
  AZURE: "cyber-azure",
  VIOLET: "electric-violet",
  AVIATION: "tactical-aviation",
  ZINC: "zinc-neutral",
  TITANIUM: "titanium-minimalist"
};

export const PALETTE_COLORS = {
  "studio-obsidian": "#1db954",
  "cyber-azure": "#0a84ff",
  "electric-violet": "#bf5af2",
  "tactical-aviation": "#ff9f0a",
  "zinc-neutral": "#fafafa",
  "titanium-minimalist": "#e5e5e5"
};

export function updateModeUI(mode) {
  const modeBtn = document.getElementById("mode-toggle-btn");
  if (!modeBtn) return;
  
  if (mode === "light") {
    // Show Moon icon for switching to dark
    modeBtn.innerHTML = `
      <svg class="icon-moon" viewBox="0 0 24 24" width="15" height="15" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"></path>
      </svg>
    `;
    modeBtn.setAttribute("title", "Switch to Dark Mode");
    modeBtn.setAttribute("aria-label", "Switch to Dark Mode");
  } else {
    // Show Sun icon for switching to light
    modeBtn.innerHTML = `
      <svg class="icon-sun" viewBox="0 0 24 24" width="15" height="15" stroke="currentColor" fill="none" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="5"></circle>
        <line x1="12" y1="1" x2="12" y2="3"></line>
        <line x1="12" y1="21" x2="12" y2="23"></line>
        <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"></line>
        <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"></line>
        <line x1="1" y1="12" x2="3" y2="12"></line>
        <line x1="21" y1="12" x2="23" y2="12"></line>
        <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"></line>
        <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"></line>
      </svg>
    `;
    modeBtn.setAttribute("title", "Switch to Light Mode");
    modeBtn.setAttribute("aria-label", "Switch to Light Mode");
  }
}

export function updateSwatchUI(paletteName) {
  const swatch = document.querySelector(".current-swatch");
  if (swatch && PALETTE_COLORS[paletteName]) {
    swatch.style.backgroundColor = PALETTE_COLORS[paletteName];
  }
}

export function setPalette(paletteName) {
  if (Object.values(ELITE_PALETTES).includes(paletteName)) {
    document.documentElement.setAttribute("data-palette", paletteName);
    localStorage.setItem("dv_palette", paletteName);
    updateSwatchUI(paletteName);
  }
}

export function toggleThemeMode() {
  const current = document.documentElement.getAttribute("data-mode") || "dark";
  const target = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-mode", target);
  localStorage.setItem("dv_mode", target);
  updateModeUI(target);
  return target;
}

export function initPaletteSystem() {
  const savedPalette = localStorage.getItem("dv_palette") || ELITE_PALETTES.OBSIDIAN;
  const savedMode = localStorage.getItem("dv_mode") || "dark";

  setPalette(savedPalette);
  document.documentElement.setAttribute("data-mode", savedMode);
  updateModeUI(savedMode);
  updateSwatchUI(savedPalette);

  return { savedPalette, savedMode };
}
