/**
 * DIGITVISION AI — Frontend Client Application
 * Deep Obsidian Telemetry & Inference Controller
 */

// State
let isDrawing = false;
let canvas, ctx;
let brushSize = 18;
let liveMode = false;
let debounceTimer = null;
let currentModelId = "DigitVision-DeepConvNet";

// Preset digit stroke paths (relative coordinates [0-1])
const PRESET_STROKES = {
  0: [[0.5, 0.2], [0.3, 0.3], [0.25, 0.5], [0.3, 0.7], [0.5, 0.8], [0.7, 0.7], [0.75, 0.5], [0.7, 0.3], [0.5, 0.2]],
  1: [[0.45, 0.25], [0.52, 0.2], [0.52, 0.8]],
  2: [[0.3, 0.3], [0.5, 0.2], [0.7, 0.3], [0.65, 0.5], [0.3, 0.8], [0.75, 0.8]],
  3: [[0.3, 0.25], [0.65, 0.25], [0.45, 0.48], [0.7, 0.55], [0.65, 0.75], [0.35, 0.8]],
  4: [[0.65, 0.75], [0.65, 0.2], [0.25, 0.55], [0.75, 0.55]],
  5: [[0.7, 0.22], [0.35, 0.22], [0.32, 0.48], [0.65, 0.48], [0.7, 0.7], [0.35, 0.8]],
  6: [[0.65, 0.25], [0.35, 0.45], [0.3, 0.65], [0.5, 0.8], [0.7, 0.65], [0.5, 0.5], [0.32, 0.6]],
  7: [[0.28, 0.25], [0.72, 0.25], [0.45, 0.8]],
  8: [[0.5, 0.22], [0.32, 0.35], [0.5, 0.5], [0.68, 0.65], [0.5, 0.8], [0.32, 0.65], [0.5, 0.5], [0.68, 0.35], [0.5, 0.22]],
  9: [[0.68, 0.55], [0.5, 0.5], [0.32, 0.35], [0.5, 0.22], [0.68, 0.35], [0.68, 0.8]]
};

document.addEventListener("DOMContentLoaded", () => {
  initCanvas();
  initNavigation();
  initControls();
  fetchModelCatalog();
  fetchBenchmarks();
});

function initCanvas() {
  canvas = document.getElementById("digit-canvas");
  ctx = canvas.getContext("2d", { willReadFrequently: true });

  // Black background
  clearCanvas();

  // Mouse events
  canvas.addEventListener("mousedown", startDrawing);
  canvas.addEventListener("mousemove", draw);
  canvas.addEventListener("mouseup", stopDrawing);
  canvas.addEventListener("mouseleave", stopDrawing);

  // Touch events for tablet/mobile stylus
  canvas.addEventListener("touchstart", (e) => {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent("mousedown", {
      clientX: touch.clientX,
      clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
  });

  canvas.addEventListener("touchmove", (e) => {
    e.preventDefault();
    const touch = e.touches[0];
    const mouseEvent = new MouseEvent("mousemove", {
      clientX: touch.clientX,
      clientY: touch.clientY
    });
    canvas.dispatchEvent(mouseEvent);
  });

  canvas.addEventListener("touchend", () => {
    canvas.dispatchEvent(new MouseEvent("mouseup", {}));
  });
}

function startDrawing(e) {
  isDrawing = true;
  ctx.beginPath();
  const rect = canvas.getBoundingClientRect();
  ctx.moveTo(e.clientX - rect.left, e.clientY - rect.top);
  draw(e);
}

function draw(e) {
  if (!isDrawing) return;
  const rect = canvas.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;

  ctx.lineWidth = brushSize;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.strokeStyle = "#FFFFFF";

  ctx.lineTo(x, y);
  ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(x, y);

  if (liveMode) {
    scheduleInference();
  }
}

function stopDrawing() {
  if (!isDrawing) return;
  isDrawing = false;
  ctx.beginPath();
  scheduleInference();
}

function clearCanvas() {
  ctx.fillStyle = "#000000";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  resetHUD();
}

function resetHUD() {
  document.getElementById("pred-digit").innerText = "—";
  document.getElementById("pred-confidence").innerText = "0.0%";
  document.getElementById("pred-confidence").style.color = "var(--text-primary)";
  const decisionBadge = document.getElementById("pred-status-badge");
  decisionBadge.innerText = "STANDBY";
  decisionBadge.style.backgroundColor = "var(--bg-surface)";
  decisionBadge.style.color = "var(--text-telemetry)";

  document.getElementById("top-k-bars").innerHTML = '<div style="color:var(--text-telemetry);font-size:11px;">Draw a digit on the canvas to begin telemetry.</div>';
  document.getElementById("preview-canonical").src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";
  document.getElementById("preview-gradcam").src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";
  document.getElementById("preview-saliency").src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";
}

function scheduleInference() {
  if (debounceTimer) clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    executeInference();
  }, 220);
}

async function executeInference() {
  const dataUrl = canvas.toDataURL("image/png");

  try {
    const res = await fetch("/api/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        image: dataUrl,
        model_id: currentModelId,
        generate_xai: true
      })
    });

    if (!res.ok) {
      const err = await res.json();
      console.warn("Prediction service notice:", err.detail);
      return;
    }

    const telemetry = await res.json();
    renderTelemetryHUD(telemetry);
  } catch (err) {
    console.error("Inference request failed:", err);
  }
}

function renderTelemetryHUD(data) {
  const pred = data.prediction;
  const quality = data.quality_audit;
  const decision = data.decision;
  const latencies = data.execution_latency_ms;

  // Header quick latency
  document.getElementById("header-latency").innerText = `${latencies.total_roundtrip.toFixed(1)} ms`;

  // Main Prediction Display
  const digitEl = document.getElementById("pred-digit");
  const confEl = document.getElementById("pred-confidence");
  const badgeEl = document.getElementById("pred-status-badge");

  if (!quality.is_valid) {
    digitEl.innerText = "∅";
    confEl.innerText = "REJECT";
    confEl.style.color = "var(--accent-confidence-low)";
    badgeEl.innerText = quality.warnings[0] || "QUALITY_REJECT";
    badgeEl.style.backgroundColor = "rgba(255, 51, 51, 0.15)";
    badgeEl.style.color = "var(--accent-confidence-low)";
  } else {
    digitEl.innerText = pred.predicted_digit;
    confEl.innerText = `${pred.confidence_percentage}%`;
    confEl.style.color = pred.theme_color;
    badgeEl.innerText = decision.status;
    badgeEl.style.backgroundColor = `${pred.theme_color}22`;
    badgeEl.style.color = pred.theme_color;
  }

  // Top-K Probabilities
  const topKContainer = document.getElementById("top-k-bars");
  topKContainer.innerHTML = "";

  if (quality.is_valid && pred.top_k) {
    pred.top_k.forEach((item) => {
      const row = document.createElement("div");
      row.className = "top-k-item";
      row.innerHTML = `
        <div class="top-k-header">
          <span>#${item.rank} DIGIT <strong>${item.digit}</strong></span>
          <span>${item.percentage.toFixed(1)}%</span>
        </div>
        <div class="top-k-bar-track">
          <div class="top-k-bar-fill" style="width: ${item.percentage}%; background-color: ${item.rank === 1 ? pred.theme_color : 'var(--text-telemetry)'};"></div>
        </div>
      `;
      topKContainer.appendChild(row);
    });
  }

  // Telemetry Table
  document.getElementById("telem-entropy").innerText = `${pred.entropy_bits.toFixed(3)} bits`;
  document.getElementById("telem-margin").innerText = `${pred.margin.toFixed(3)}`;
  document.getElementById("telem-quality-score").innerText = `${quality.quality_score} / 100`;
  document.getElementById("telem-stroke-pixels").innerText = quality.stroke_pixel_count;
  document.getElementById("telem-centroid-offset").innerText = `${quality.centroid_offset.toFixed(2)} px`;
  document.getElementById("telem-sharpness").innerText = quality.sharpness.toFixed(1);

  // Latency breakdown
  document.getElementById("telem-lat-prep").innerText = `${latencies.preprocessing.toFixed(2)} ms`;
  document.getElementById("telem-lat-infer").innerText = `${latencies.inference.toFixed(2)} ms`;
  document.getElementById("telem-lat-total").innerText = `${latencies.total_roundtrip.toFixed(2)} ms`;

  // Visual artifacts
  if (data.visual_artifacts.canonical_preview) {
    document.getElementById("preview-canonical").src = data.visual_artifacts.canonical_preview;
  }
  if (data.visual_artifacts.gradcam_overlay) {
    document.getElementById("preview-gradcam").src = data.visual_artifacts.gradcam_overlay;
  }
  if (data.visual_artifacts.saliency_overlay) {
    document.getElementById("preview-saliency").src = data.visual_artifacts.saliency_overlay;
  }
}

function loadPreset(digit) {
  clearCanvas();
  const strokes = PRESET_STROKES[digit];
  if (!strokes) return;

  const w = canvas.width;
  const h = canvas.height;

  ctx.lineWidth = brushSize;
  ctx.lineCap = "round";
  ctx.lineJoin = "round";
  ctx.strokeStyle = "#FFFFFF";

  ctx.beginPath();
  strokes.forEach((pt, idx) => {
    const x = pt[0] * w;
    const y = pt[1] * h;
    if (idx === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();

  scheduleInference();
}

function initControls() {
  document.getElementById("btn-clear").addEventListener("click", clearCanvas);
  document.getElementById("btn-infer").addEventListener("click", executeInference);

  const brushInput = document.getElementById("brush-size");
  brushInput.addEventListener("input", (e) => {
    brushSize = parseInt(e.target.value);
    document.getElementById("brush-size-val").innerText = `${brushSize}px`;
  });

  const modelSelect = document.getElementById("model-select");
  modelSelect.addEventListener("change", (e) => {
    currentModelId = e.target.value;
    document.getElementById("header-model-name").innerText = currentModelId;
    scheduleInference();
  });

  const liveCheck = document.getElementById("check-live");
  liveCheck.addEventListener("change", (e) => {
    liveMode = e.target.checked;
  });

  // Presets buttons
  for (let i = 0; i <= 9; i++) {
    const btn = document.getElementById(`preset-${i}`);
    if (btn) {
      btn.addEventListener("click", () => loadPreset(i));
    }
  }
}

function initNavigation() {
  const tabs = document.querySelectorAll(".nav-tab-btn");
  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      tabs.forEach((t) => t.classList.remove("active"));
      tab.classList.add("active");

      const targetPane = tab.getAttribute("data-tab");
      document.querySelectorAll(".tab-pane").forEach((pane) => pane.classList.remove("active"));
      document.getElementById(targetPane).classList.add("active");
    });
  });
}

async function fetchModelCatalog() {
  try {
    const res = await fetch("/api/models");
    if (!res.ok) return;
    const data = await res.json();
    const select = document.getElementById("model-select");
    select.innerHTML = "";
    data.models.forEach((m) => {
      const opt = document.createElement("option");
      opt.value = m.id;
      opt.innerText = m.name;
      if (m.is_default) opt.selected = true;
      select.appendChild(opt);
    });
  } catch (e) {
    console.error("Could not fetch model catalog", e);
  }
}

async function fetchBenchmarks() {
  try {
    const res = await fetch("/api/experiments");
    if (!res.ok) return;
    const exp = await res.json();

    // Populate comparison table
    const tbody = document.getElementById("benchmark-table-body");
    tbody.innerHTML = "";

    const models = exp.models;
    for (const mName in models) {
      const m = models[mName];
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td><strong>${m.model_name}</strong></td>
        <td><span style="color:var(--accent-confidence-high);font-weight:700;">${m.accuracy_pct}%</span></td>
        <td>${m.macro_f1.toFixed(4)}</td>
        <td>${m.expected_calibration_error.toFixed(4)}</td>
        <td>${m.latency.mean_latency_ms.toFixed(2)} ms</td>
        <td>${m.latency.throughput_samples_per_sec}</td>
      `;
      tbody.appendChild(tr);
    }

    // Populate failures gallery
    const failContainer = document.getElementById("failures-gallery");
    failContainer.innerHTML = "";
    const convnetData = models["DigitVision-DeepConvNet"];
    if (convnetData && convnetData.high_confidence_failures) {
      convnetData.high_confidence_failures.forEach((f) => {
        const div = document.createElement("div");
        div.className = "failure-card";
        div.innerHTML = `
          <img src="/failures/failure_true${f.true_digit}_pred${f.predicted_digit}_idx${f.sample_index}.png" alt="Failure">
          <div class="failure-meta">
            <div>TRUE: <strong>${f.true_digit}</strong> | PREDICTED: <span class="failure-tag">${f.predicted_digit}</span></div>
            <div>CONFIDENCE: ${(f.confidence * 100).toFixed(1)}%</div>
            <div>RUNNER-UP: ${f.runner_up_digit} (${(f.runner_up_prob * 100).toFixed(1)}%)</div>
            <div style="color:var(--text-telemetry)">ENTROPY: ${f.entropy_bits.toFixed(2)} bits</div>
          </div>
        `;
        failContainer.appendChild(div);
      });
    }
  } catch (e) {
    console.error("Error fetching benchmarks:", e);
  }
}
