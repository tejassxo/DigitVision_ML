/**
 * DIGITVISION AI — Elite Palette Controller
 * Carbon Monochrome & Achromatic Precision Switcher
 */

export const ELITE_PALETTES = {
  ZINC: "zinc-neutral",
  OBSIDIAN: "studio-obsidian",
  AVIATION: "tactical-aviation",
  TITANIUM: "titanium-minimalist"
};

export function setPalette(paletteName) {
  if (Object.values(ELITE_PALETTES).includes(paletteName)) {
    document.documentElement.setAttribute("data-palette", paletteName);
    localStorage.setItem("dv_palette", paletteName);
  }
}

export function toggleThemeMode() {
  const current = document.documentElement.getAttribute("data-mode") || "dark";
  const target = current === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-mode", target);
  localStorage.setItem("dv_mode", target);
}

export function initPaletteSystem() {
  const savedPalette = localStorage.getItem("dv_palette") || ELITE_PALETTES.OBSIDIAN;
  const savedMode = localStorage.getItem("dv_mode") || "dark";

  setPalette(savedPalette);
  document.documentElement.setAttribute("data-mode", savedMode);

  return { savedPalette, savedMode };
}
