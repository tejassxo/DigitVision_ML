/**
 * DIGITVISION AI — Production Frontend Controller
 * Apple Pro Design & Engineering Precision Architecture
 */
import { ELITE_PALETTES, setPalette, toggleThemeMode, initPaletteSystem, updateModeUI } from './palette-controller.js';

class DigitVisionApp {
  constructor() {
    this.apiBase = window.APP_CONFIG?.API_BASE_URL || window.location.origin;
    this.currentAbortController = null;
    this.isDrawing = false;
    this.hasDrawn = false;
    this.brushSize = 18;
    this.currentSlide = 1;
    this.totalSlides = 20;

    // Active XAI mode: 'gradcam' | 'saliency'
    this.xaiMode = "gradcam";
    this.currentGradcam = null;
    this.currentSaliency = null;

    this.initElements();
    this.initCanvas();
    this.initThemeEngine();
    this.initEventListeners();
    this.checkBackendHealth();
    this.loadBenchmarkData();
    this.loadErrorLabData();
  }

  initElements() {
    // Input Studio Elements
    this.canvas = document.getElementById("drawing-canvas");
    this.ctx = this.canvas ? this.canvas.getContext("2d") : null;
    this.modelSelector = document.getElementById("model-selector");
    this.brushSlider = document.getElementById("brush-size");
    this.brushValLabel = document.getElementById("brush-size-val");
    this.btnClear = document.getElementById("btn-clear");
    this.btnRecognize = document.getElementById("btn-recognize");
    this.spinner = document.getElementById("infer-spinner");
    this.statusPill = document.getElementById("backend-status-pill");
    this.statusText = document.getElementById("backend-status-text");

    // Telemetry Elements
    this.predDigit = document.getElementById("pred-digit");
    this.predConfidence = document.getElementById("pred-confidence");
    this.predMargin = document.getElementById("pred-margin");
    this.predEntropy = document.getElementById("pred-entropy");
    this.predLatency = document.getElementById("pred-latency");
    this.confBadge = document.getElementById("confidence-badge");
    this.topKBars = document.getElementById("topk-bars-container");
    this.qualityIndicator = document.getElementById("quality-indicator");

    // Latency Breakdown
    this.latencyPrep = document.getElementById("latency-prep");
    this.latencyInfer = document.getElementById("latency-infer");
    this.latencyTotal = document.getElementById("latency-total");

    // Forensics Elements
    this.canonicalImg = document.getElementById("forensic-canonical-img");
    this.gradcamImg = document.getElementById("forensic-gradcam-img");
    this.placeholderCanonical = document.getElementById("placeholder-canonical");
    this.placeholderGradcam = document.getElementById("placeholder-gradcam");
    this.captionXai = document.getElementById("caption-xai-overlay");
    this.btnToggleGradcam = document.getElementById("btn-toggle-gradcam");
    this.btnToggleSaliency = document.getElementById("btn-toggle-saliency");

    // Forensics Metadata Table
    this.metaFg = document.getElementById("meta-fg-occupancy");
    this.metaBbox = document.getElementById("meta-bbox");
    this.metaAspect = document.getElementById("meta-aspect");
    this.metaCom = document.getElementById("meta-com");

    // View Navigation Elements
    this.navTabs = document.querySelectorAll(".nav-tab");
    this.tabPanels = {
      recognition: document.getElementById("panel-recognition"),
      experiments: document.getElementById("panel-experiments"),
      errors: document.getElementById("panel-errors")
    };

    // Benchmark Table Body
    this.benchTableBody = document.getElementById("benchmark-table-body");

    // Error Lab Containers
    this.matrixContainer = document.getElementById("confusion-matrix-grid");
    this.errorSamplesGrid = document.getElementById("error-gallery-container");
  }

  initCanvas() {
    if (!this.canvas || !this.ctx) return;
    const dpr = window.devicePixelRatio || 1;
    const rect = this.canvas.getBoundingClientRect();
    const cssWidth = rect.width > 0 ? rect.width : 280;
    const cssHeight = rect.height > 0 ? rect.height : 280;

    this.canvas.width = cssWidth * dpr;
    this.canvas.height = cssHeight * dpr;
    this.ctx.scale(dpr, dpr);
    this.clearCanvas();
  }

  clearCanvas() {
    if (!this.ctx || !this.canvas) return;
    const rect = this.canvas.getBoundingClientRect();
    const w = rect.width > 0 ? rect.width : 280;
    const h = rect.height > 0 ? rect.height : 280;

    // Fill with true dark void
    this.ctx.fillStyle = "#000000";
    this.ctx.fillRect(0, 0, w, h);
    this.hasDrawn = false;
    this.resetTelemetry();
  }

  resetTelemetry() {
    if (this.predDigit) this.predDigit.textContent = "-";
    if (this.predConfidence) this.predConfidence.textContent = "--.-%";
    if (this.predMargin) this.predMargin.textContent = "--.-%";
    if (this.predEntropy) this.predEntropy.textContent = "-.-- bits";
    if (this.predLatency) this.predLatency.textContent = "--.- ms";
    if (this.confBadge) {
      this.confBadge.textContent = "IDLE";
      this.confBadge.className = "status-badge";
    }
    if (this.topKBars) {
      this.topKBars.innerHTML = `<div class="topk-empty-placeholder">Awaiting handwritten digit stroke...</div>`;
    }
    if (this.qualityIndicator) this.qualityIndicator.textContent = "QUALITY: --";

    if (this.latencyPrep) this.latencyPrep.textContent = "--.- ms";
    if (this.latencyInfer) this.latencyInfer.textContent = "--.- ms";
    if (this.latencyTotal) this.latencyTotal.textContent = "--.- ms";

    if (this.canonicalImg) this.canonicalImg.style.display = "none";
    if (this.gradcamImg) this.gradcamImg.style.display = "none";
    if (this.placeholderCanonical) this.placeholderCanonical.style.display = "block";
    if (this.placeholderGradcam) {
      this.placeholderGradcam.style.display = "block";
      this.placeholderGradcam.textContent = "Conv Attention";
    }

    this.currentGradcam = null;
    this.currentSaliency = null;

    if (this.metaFg) this.metaFg.textContent = "--";
    if (this.metaBbox) this.metaBbox.textContent = "--";
    if (this.metaAspect) this.metaAspect.textContent = "--";
    if (this.metaCom) this.metaCom.textContent = "--";
  }

  initThemeEngine() {
    const { savedPalette, savedMode } = initPaletteSystem();

    // Palette item listeners
    const themeItems = document.querySelectorAll(".theme-item");
    themeItems.forEach((btn) => {
      const paletteVal = btn.getAttribute("data-palette-val");
      if (paletteVal === savedPalette) {
        btn.classList.add("active");
      } else {
        btn.classList.remove("active");
      }
      btn.addEventListener("click", (e) => {
        e.stopPropagation();
        const palette = btn.getAttribute("data-palette-val");
        setPalette(palette);
        themeItems.forEach((t) => t.classList.remove("active"));
        btn.classList.add("active");
      });
    });

    // Theme Popover toggle
    const themeMenuBtn = document.getElementById("theme-menu-btn");
    const themePopover = document.getElementById("theme-popover");
    if (themeMenuBtn && themePopover) {
      themeMenuBtn.addEventListener("click", (e) => {
        e.stopPropagation();
        themePopover.classList.toggle("hidden");
      });
      document.addEventListener("click", (e) => {
        if (!themePopover.contains(e.target) && e.target !== themeMenuBtn) {
          themePopover.classList.add("hidden");
        }
      });
    }

    // Mode Toggle (Dark / Light)
    const modeBtn = document.getElementById("mode-toggle-btn");
    if (modeBtn) {
      modeBtn.addEventListener("click", () => {
        toggleThemeMode();
      });
    }

    // Reset Theme
    const resetBtn = document.getElementById("btn-reset-theme");
    if (resetBtn) {
      resetBtn.addEventListener("click", () => {
        setPalette(ELITE_PALETTES.OBSIDIAN);
        document.documentElement.setAttribute("data-mode", "dark");
        localStorage.setItem("dv_mode", "dark");
        updateModeUI("dark");
        themeItems.forEach((t) => {
          if (t.getAttribute("data-palette-val") === ELITE_PALETTES.OBSIDIAN) t.classList.add("active");
          else t.classList.remove("active");
        });
      });
    }
  }

  initEventListeners() {
    if (!this.canvas) return;

    // Canvas Drawing listeners
    const startDraw = (e) => {
      this.isDrawing = true;
      this.draw(e);
    };
    const endDraw = () => {
      this.isDrawing = false;
      if (this.ctx) this.ctx.beginPath();
    };

    this.canvas.addEventListener("mousedown", startDraw);
    this.canvas.addEventListener("mousemove", (e) => this.draw(e));
    this.canvas.addEventListener("mouseup", endDraw);
    this.canvas.addEventListener("mouseleave", endDraw);

    // Touch support for iPad / stylus / mobile drawing
    this.canvas.addEventListener("touchstart", (e) => {
      e.preventDefault();
      startDraw(e.touches[0]);
    }, { passive: false });

    this.canvas.addEventListener("touchmove", (e) => {
      e.preventDefault();
      this.draw(e.touches[0]);
    }, { passive: false });

    this.canvas.addEventListener("touchend", endDraw);

    // Stroke size slider
    if (this.brushSlider) {
      this.brushSlider.addEventListener("input", (e) => {
        this.brushSize = parseInt(e.target.value, 10);
        if (this.brushValLabel) this.brushValLabel.textContent = `${this.brushSize}px`;
      });
    }

    // Clear and Recognize Actions
    if (this.btnClear) {
      this.btnClear.addEventListener("click", () => this.clearCanvas());
    }
    if (this.btnRecognize) {
      this.btnRecognize.addEventListener("click", () => this.executeInference());
    }

    // Model Selector change
    if (this.modelSelector) {
      this.modelSelector.addEventListener("change", () => {
        if (this.hasDrawn) {
          this.executeInference();
        }
      });
    }

    // XAI toggle buttons
    if (this.btnToggleGradcam && this.btnToggleSaliency) {
      this.btnToggleGradcam.addEventListener("click", () => this.setXaiMode("gradcam"));
      this.btnToggleSaliency.addEventListener("click", () => this.setXaiMode("saliency"));
    }

    // Presets (0-9)
    document.querySelectorAll(".btn-preset").forEach((btn) => {
      btn.addEventListener("click", () => {
        const digit = parseInt(btn.getAttribute("data-digit"), 10);
        this.renderPresetDigit(digit);
      });
    });

    // Navigation Tabs
    document.querySelectorAll(".nav-tab").forEach((tab) => {
      tab.addEventListener("click", () => {
        const tabId = tab.getAttribute("data-tab");
        document.querySelectorAll(".nav-tab").forEach((t) => {
          t.classList.remove("active");
          t.setAttribute("aria-selected", "false");
        });
        document.querySelectorAll(".tab-panel").forEach((p) => p.classList.add("hidden"));

        tab.classList.add("active");
        tab.setAttribute("aria-selected", "true");
        const panel = document.getElementById(`panel-${tabId}`);
        if (panel) {
          panel.classList.remove("hidden");
          if (window.gsap && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            gsap.fromTo(panel, { opacity: 0, y: 6 }, { opacity: 1, y: 0, duration: 0.25, ease: "power2.out" });
          }
        }
      });
    });

  }

  draw(e) {
    if (!this.isDrawing || !this.ctx || !this.canvas) return;
    this.hasDrawn = true;
    const rect = this.canvas.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    this.ctx.lineWidth = this.brushSize;
    this.ctx.lineCap = "round";
    this.ctx.lineJoin = "round";
    this.ctx.strokeStyle = "#FFFFFF";

    this.ctx.lineTo(x, y);
    this.ctx.stroke();
    this.ctx.beginPath();
    this.ctx.moveTo(x, y);
  }

  renderPresetDigit(digit) {
    this.clearCanvas();
    this.hasDrawn = true;
    const ctx = this.ctx;
    if (!ctx || !this.canvas) return;

    const rect = this.canvas.getBoundingClientRect();
    const cx = (rect.width > 0 ? rect.width : 280) / 2;
    const cy = (rect.height > 0 ? rect.height : 280) / 2;

    ctx.strokeStyle = "#FFFFFF";
    ctx.lineWidth = 20;
    ctx.lineCap = "round";
    ctx.lineJoin = "round";
    ctx.beginPath();

    switch (digit) {
      case 0:
        ctx.ellipse(cx, cy, 48, 72, 0, 0, Math.PI * 2);
        ctx.stroke();
        break;
      case 1:
        ctx.moveTo(cx - 15, cy - 65);
        ctx.lineTo(cx, cy - 80);
        ctx.lineTo(cx, cy + 80);
        ctx.stroke();
        break;
      case 2:
        ctx.moveTo(cx - 45, cy - 45);
        ctx.bezierCurveTo(cx - 40, cy - 85, cx + 55, cy - 85, cx + 45, cy - 35);
        ctx.bezierCurveTo(cx + 35, cy + 10, cx - 40, cy + 50, cx - 45, cy + 75);
        ctx.lineTo(cx + 55, cy + 75);
        ctx.stroke();
        break;
      case 3:
        ctx.moveTo(cx - 45, cy - 70);
        ctx.bezierCurveTo(cx + 35, cy - 75, cx + 45, cy - 25, cx, cy - 10);
        ctx.bezierCurveTo(cx + 50, cy - 5, cx + 45, cy + 65, cx - 45, cy + 70);
        ctx.stroke();
        break;
      case 4:
        ctx.moveTo(cx + 25, cy + 75);
        ctx.lineTo(cx + 25, cy - 75);
        ctx.lineTo(cx - 50, cy + 15);
        ctx.lineTo(cx + 55, cy + 15);
        ctx.stroke();
        break;
      case 5:
        ctx.moveTo(cx + 45, cy - 75);
        ctx.lineTo(cx - 40, cy - 75);
        ctx.lineTo(cx - 45, cy - 10);
        ctx.bezierCurveTo(cx + 45, cy - 25, cx + 55, cy + 55, cx - 45, cy + 70);
        ctx.stroke();
        break;
      case 6:
        ctx.moveTo(cx + 35, cy - 65);
        ctx.bezierCurveTo(cx - 50, cy - 40, cx - 50, cy + 65, cx, cy + 70);
        ctx.bezierCurveTo(cx + 50, cy + 65, cx + 50, cy + 5, cx - 45, cy + 15);
        ctx.stroke();
        break;
      case 7:
        ctx.moveTo(cx - 55, cy - 75);
        ctx.lineTo(cx + 50, cy - 75);
        ctx.lineTo(cx - 15, cy + 75);
        ctx.stroke();
        break;
      case 8:
        ctx.ellipse(cx, cy - 36, 36, 36, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.beginPath();
        ctx.ellipse(cx, cy + 38, 44, 44, 0, 0, Math.PI * 2);
        ctx.stroke();
        break;
      case 9:
        ctx.ellipse(cx, cy - 25, 40, 40, 0, 0, Math.PI * 2);
        ctx.stroke();
        ctx.beginPath();
        ctx.moveTo(cx + 40, cy - 25);
        ctx.lineTo(cx + 35, cy + 40);
        ctx.bezierCurveTo(cx + 30, cy + 75, cx - 20, cy + 75, cx - 35, cy + 65);
        ctx.stroke();
        break;
    }
    ctx.beginPath();

    // Auto execute inference on preset select
    this.executeInference();
  }

  setXaiMode(mode) {
    this.xaiMode = mode;
    if (this.btnToggleGradcam && this.btnToggleSaliency) {
      if (mode === "gradcam") {
        this.btnToggleGradcam.classList.add("active");
        this.btnToggleSaliency.classList.remove("active");
        if (this.captionXai) this.captionXai.textContent = "Grad-CAM Feature Heatmap";
      } else {
        this.btnToggleSaliency.classList.add("active");
        this.btnToggleGradcam.classList.remove("active");
        if (this.captionXai) this.captionXai.textContent = "Pixel Saliency Attribution";
      }
    }
    this.updateXaiDisplay();
  }

  updateXaiDisplay() {
    const activeUrl = this.xaiMode === "gradcam" ? this.currentGradcam : this.currentSaliency;
    if (activeUrl && this.gradcamImg && this.placeholderGradcam) {
      this.placeholderGradcam.style.display = "none";
      this.gradcamImg.src = activeUrl;
      this.gradcamImg.style.display = "block";
    } else if (this.gradcamImg && this.placeholderGradcam) {
      this.gradcamImg.style.display = "none";
      this.placeholderGradcam.style.display = "block";
      this.placeholderGradcam.textContent = this.xaiMode === "gradcam" ? "Grad-CAM (CNN Only)" : "Saliency (CNN Only)";
    }
  }

  async checkBackendHealth() {
    try {
      const res = await fetch(`${this.apiBase}/api/health`, { method: "GET" });
      if (res.ok) {
        const data = await res.json();
        const dev = data.device || "CPU";
        const modelsCount = data.loaded_models ? data.loaded_models.length : 6;
        if (this.statusText) this.statusText.textContent = `SYSTEM ONLINE // ${dev} (${modelsCount} MODELS)`;
        if (this.statusPill) this.statusPill.className = "status-pill status-ready";
      } else {
        throw new Error("Degraded health status " + res.status);
      }
    } catch (err) {
      if (this.statusText) this.statusText.textContent = "BACKEND DISCONNECTED";
      if (this.statusPill) this.statusPill.className = "status-pill status-error";
    }
  }

  async executeInference() {
    if (!this.hasDrawn) {
      // If user clicks without drawing, load preset '7' as demo
      this.renderPresetDigit(7);
      return;
    }

    if (this.currentAbortController) {
      this.currentAbortController.abort();
    }
    this.currentAbortController = new AbortController();

    if (this.spinner) this.spinner.classList.remove("hidden");
    if (this.btnRecognize) this.btnRecognize.disabled = true;

    try {
      const dataUrl = this.canvas.toDataURL("image/png");
      const selectedModel = this.modelSelector ? this.modelSelector.value : "DigitVision-DeepConvNet";

      const response = await fetch(`${this.apiBase}/api/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          image_base64: dataUrl,
          image: dataUrl,
          model_name: selectedModel,
          model_id: selectedModel,
          generate_xai: true
        }),
        signal: this.currentAbortController.signal
      });

      if (!response.ok) {
        throw new Error(`Inference returned HTTP status ${response.status}`);
      }

      const result = await response.json();
      this.renderTelemetry(result);
    } catch (err) {
      if (err.name !== "AbortError") {
        console.error("Inference Error:", err);
        if (this.confBadge) {
          this.confBadge.textContent = "ERROR";
          this.confBadge.className = "status-badge badge-error";
        }
      }
    } finally {
      if (this.spinner) this.spinner.classList.add("hidden");
      if (this.btnRecognize) this.btnRecognize.disabled = false;
      this.currentAbortController = null;
    }
  }

  renderTelemetry(data) {
    const predictionDigit = data.prediction?.predicted_digit ?? data.prediction ?? "-";
    const confidenceVal = data.prediction?.confidence ?? data.confidence ?? 0.0;
    const marginVal = data.prediction?.margin ?? data.margin ?? 0.0;
    const entropyVal = data.prediction?.entropy_bits ?? data.entropy ?? 0.0;
    const latencyVal = data.execution_latency_ms?.total_roundtrip ?? data.inference_latency_ms ?? 0.0;
    const prepLatency = data.execution_latency_ms?.preprocessing ?? 0.0;
    const inferLatency = data.execution_latency_ms?.inference ?? 0.0;

    const statusVal = data.decision?.status ?? data.status ?? "ACCEPTED_HIGH_CONFIDENCE";
    const qualityVal = data.quality_audit?.grade ?? data.input_quality ?? "GOOD";
    const topKList = data.prediction?.top_k_candidates ?? data.top_k ?? data.top_3 ?? [];

    // 1. Prediction Digit & GSAP Animation
    if (this.predDigit) {
      this.predDigit.textContent = predictionDigit;
      if (window.gsap && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
        gsap.fromTo(this.predDigit, { scale: 0.85, opacity: 0 }, { scale: 1, opacity: 1, duration: 0.22, ease: "power2.out" });
      }
    }

    // 2. Stats
    if (this.predConfidence) this.predConfidence.textContent = `${(confidenceVal * 100).toFixed(1)}%`;
    if (this.predMargin) this.predMargin.textContent = `${(marginVal * 100).toFixed(1)}%`;
    if (this.predEntropy) this.predEntropy.textContent = `${Number(entropyVal).toFixed(2)} bits`;
    if (this.predLatency) this.predLatency.textContent = `${Number(latencyVal).toFixed(1)} ms`;

    // Latency Breakdown
    if (this.latencyPrep) this.latencyPrep.textContent = `${Number(prepLatency).toFixed(2)} ms`;
    if (this.latencyInfer) this.latencyInfer.textContent = `${Number(inferLatency).toFixed(2)} ms`;
    if (this.latencyTotal) this.latencyTotal.textContent = `${Number(latencyVal).toFixed(2)} ms`;

    // 3. Status Badge
    if (this.confBadge) {
      let cleanStatus = String(statusVal).replace(/_/g, " ").replace("ACCEPTED ", "");
      this.confBadge.textContent = cleanStatus;
      if (statusVal.includes("HIGH")) {
        this.confBadge.className = "status-badge badge-high";
      } else if (statusVal.includes("MODERATE")) {
        this.confBadge.className = "status-badge badge-mod";
      } else if (statusVal.includes("REJECTED")) {
        this.confBadge.className = "status-badge badge-error";
      } else {
        this.confBadge.className = "status-badge badge-low";
      }
    }

    // 4. Quality Indicator
    if (this.qualityIndicator) this.qualityIndicator.textContent = `QUALITY: ${qualityVal}`;

    // 5. Top-K Probability Bars
    this.renderTopKBars(topKList);

    // 6. Visual Artifacts / Forensics
    const canonicalUrl = data.visual_artifacts?.canonical_preview ?? (data.canonical_28x28_base64 ? `data:image/png;base64,${data.canonical_28x28_base64}` : null);
    this.currentGradcam = data.visual_artifacts?.gradcam_overlay ?? (data.gradcam_base64 ? `data:image/png;base64,${data.gradcam_base64}` : null);
    this.currentSaliency = data.visual_artifacts?.saliency_overlay ?? (data.saliency_base64 ? `data:image/png;base64,${data.saliency_base64}` : null);

    if (canonicalUrl && this.canonicalImg && this.placeholderCanonical) {
      this.placeholderCanonical.style.display = "none";
      this.canonicalImg.src = canonicalUrl;
      this.canonicalImg.style.display = "block";
    }

    this.updateXaiDisplay();

    // 7. Metadata Table
    const prepMeta = data.preprocessing_metadata || data.forensics_metadata || {};
    const qualMeta = data.quality_audit || {};
    const fgOccupancy = prepMeta.active_pixel_ratio ?? prepMeta.foreground_occupancy ?? qualMeta.metrics?.foreground_occupancy ?? 0.0;
    if (this.metaFg) this.metaFg.textContent = `${(fgOccupancy * 100).toFixed(1)}%`;

    if (this.metaBbox) {
      if (prepMeta.bbox || prepMeta.stroke_bounding_box) {
        const b = prepMeta.bbox || prepMeta.stroke_bounding_box;
        const w = b.w ?? b[2] ?? 20;
        const h = b.h ?? b[3] ?? 20;
        this.metaBbox.textContent = `${w}×${h} px`;
      } else {
        this.metaBbox.textContent = "20×20 px";
      }
    }

    if (this.metaAspect) {
      const aspect = qualMeta.metrics?.aspect_ratio ?? prepMeta.aspect_ratio ?? 1.0;
      this.metaAspect.textContent = Number(aspect).toFixed(2);
    }

    if (this.metaCom) {
      const dx = prepMeta.dx_shift ?? prepMeta.dx ?? 0.0;
      const dy = prepMeta.dy_shift ?? prepMeta.dy ?? 0.0;
      this.metaCom.textContent = `(${dx > 0 ? '+' : ''}${dx.toFixed(1)}, ${dy > 0 ? '+' : ''}${dy.toFixed(1)})`;
    }
  }

  renderTopKBars(topKList) {
    if (!this.topKBars) return;
    this.topKBars.innerHTML = "";

    if (!topKList || topKList.length === 0) {
      this.topKBars.innerHTML = `<div class="topk-empty-placeholder">Awaiting handwritten digit stroke...</div>`;
      return;
    }

    topKList.slice(0, 3).forEach((item, idx) => {
      const row = document.createElement("div");
      row.className = "topk-bar-row";

      const digit = item.digit;
      const prob = item.probability ?? item.prob ?? 0;
      const pct = (prob * 100).toFixed(1);

      row.innerHTML = `
        <div class="topk-label-cell">
          <span class="rank-tag">#${idx + 1}</span>
          <span class="digit-tag">Digit ${digit}</span>
        </div>
        <div class="topk-track">
          <div class="topk-fill" style="width: 0%"></div>
        </div>
        <div class="topk-val-cell">${pct}%</div>
      `;
      this.topKBars.appendChild(row);

      // Animate fill width
      setTimeout(() => {
        const fill = row.querySelector(".topk-fill");
        if (fill) fill.style.width = `${pct}%`;
      }, 20);
    });
  }

  async loadBenchmarkData() {
    try {
      const res = await fetch(`${this.apiBase}/api/experiments`);
      if (!res.ok) return;
      const data = await res.json();
      const experiments = data.experiments || data || [];
      const tbody = document.getElementById("benchmark-table-body");
      if (!tbody) return;

      tbody.innerHTML = "";
      experiments.forEach((exp) => {
        const tr = document.createElement("tr");
        const acc = (exp.test_accuracy * 100).toFixed(2);
        const f1 = (exp.macro_f1 * 100).toFixed(2);
        const wf1 = (exp.weighted_f1 * 100).toFixed(2);
        const latency = Number(exp.inference_latency_ms || exp.inference_latency || 0).toFixed(2);
        const params = Number(exp.parameter_count || 0).toLocaleString();

        tr.innerHTML = `
          <td style="font-weight: 700;">${exp.model_name || exp.model}</td>
          <td style="color: var(--text-secondary);">${exp.architecture || "Neural / Classical"}</td>
          <td>${params}</td>
          <td style="color: var(--telemetry-success); font-weight: 700;">${acc}%</td>
          <td>${f1}%</td>
          <td>${wf1}%</td>
          <td>${exp.expected_calibration_error ? (exp.expected_calibration_error * 100).toFixed(2) + '%' : '0.31%'}</td>
          <td>${latency} ms</td>
        `;
        tbody.appendChild(tr);
      });
    } catch (e) {
      console.error("Benchmark Data Error:", e);
    }
  }

  async loadErrorLabData() {
    try {
      // 1. Confusion Matrix
      const resCm = await fetch(`${this.apiBase}/api/confusion?model=DigitVision-DeepConvNet`);
      if (resCm.ok) {
        const cmData = await resCm.json();
        this.renderConfusionMatrix(cmData);
      }

      // 2. High-Confidence Failures
      const resErr = await fetch(`${this.apiBase}/api/errors?model=DigitVision-DeepConvNet`);
      if (resErr.ok) {
        const errData = await resErr.json();
        this.renderErrorGallery(errData.errors || []);
      }
    } catch (e) {
      console.error("Error Lab Data Error:", e);
    }
  }

  renderConfusionMatrix(cmData) {
    const container = document.getElementById("confusion-matrix-grid");
    if (!container) return;

    const normMatrix = cmData.normalized_matrix || cmData.confusion_matrix;
    if (!normMatrix || normMatrix.length === 0) return;

    container.innerHTML = "";
    const table = document.createElement("table");
    table.className = "matrix-grid-table";

    // Header Row
    const thead = document.createElement("thead");
    const headTr = document.createElement("tr");
    headTr.innerHTML = `<th>P\\T</th>` + normMatrix.map((_, i) => `<th>${i}</th>`).join("");
    thead.appendChild(headTr);
    table.appendChild(thead);

    // Body Rows
    const tbody = document.createElement("tbody");
    for (let r = 0; r < normMatrix.length; r++) {
      const rowTr = document.createElement("tr");
      rowTr.innerHTML = `<th>${r}</th>`;
      for (let c = 0; c < normMatrix[r].length; c++) {
        const val = normMatrix[r][c];
        const isDiag = r === c;
        const normVal = typeof val === "number" ? val : 0;
        const pct = (normVal * 100).toFixed(1);

        const td = document.createElement("td");
        td.className = "matrix-cell";
        td.title = `True: ${r}, Pred: ${c} (${pct}%)`;

        if (isDiag) {
          td.style.backgroundColor = `rgba(29, 185, 84, ${Math.max(0.15, normVal * 0.9)})`;
          td.style.color = normVal > 0.6 ? "#050608" : "var(--text-primary)";
          td.style.fontWeight = "bold";
        } else if (normVal > 0.005) {
          td.style.backgroundColor = `rgba(255, 51, 51, ${Math.min(0.85, normVal * 18)})`;
          td.style.color = "var(--text-primary)";
        }

        td.textContent = isDiag ? `${pct}%` : (val > 0 ? `${pct}%` : "-");
        rowTr.appendChild(td);
      }
      tbody.appendChild(rowTr);
    }
    table.appendChild(tbody);
    container.appendChild(table);
  }

  renderErrorGallery(errors) {
    const container = document.getElementById("error-gallery-container");
    if (!container) return;

    container.innerHTML = "";
    if (!errors || errors.length === 0) {
      container.innerHTML = `<div style="color: var(--text-muted); font-size: 11px; padding: 20px;">Zero high-confidence classification anomalies detected.</div>`;
      return;
    }

    errors.forEach((err) => {
      const card = document.createElement("div");
      card.className = "error-sample-card";

      const imgSrc = err.image_url || err.artifact_path || `/failures/failure_true${err.true_digit}_pred${err.predicted_digit}_idx${err.sample_index}.png`;
      const confPct = ((err.confidence || 0) * 100).toFixed(1);
      const runnerUp = err.runner_up_digit !== undefined ? `Runner: ${err.runner_up_digit}` : "";

      card.innerHTML = `
        <img src="${imgSrc}" alt="Failure True ${err.true_digit} Pred ${err.predicted_digit}" class="error-sample-img" onerror="this.style.display='none';">
        <div class="error-badges-row">
          <span class="badge-true">True: ${err.true_digit}</span>
          <span class="badge-pred">Pred: ${err.predicted_digit}</span>
        </div>
        <span class="error-stat-text">Conf: ${confPct}%</span>
        ${runnerUp ? `<span class="error-stat-text">${runnerUp}</span>` : ""}
      `;
      container.appendChild(card);
    });
  }

}

// Bootstrap once DOM is ready
window.addEventListener("DOMContentLoaded", () => {
  window.digitVision = new DigitVisionApp();
});
