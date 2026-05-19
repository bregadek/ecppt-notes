// eCPPT Progress Tracking - localStorage based
(function() {
  const STORAGE_KEY = "ecppt-progress";

  function loadProgress() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"); }
    catch (e) { return {}; }
  }
  function saveProgress(p) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(p));
  }
  function pageKey() {
    return location.pathname.replace(/\/$/, "");
  }

  function injectCheckbox() {
    const h1 = document.querySelector("article.md-content__inner > h1");
    if (!h1) return;
    if (document.getElementById("ecppt-progress-box")) return;
    const progress = loadProgress();
    const key = pageKey();
    const wrap = document.createElement("div");
    wrap.id = "ecppt-progress-box";
    wrap.className = "ecppt-progress-box";
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.id = "ecppt-progress-cb";
    cb.checked = !!progress[key];
    const lbl = document.createElement("label");
    lbl.htmlFor = "ecppt-progress-cb";
    lbl.textContent = cb.checked ? " ✔ Studiato" : " ☐ Segna come studiato";
    cb.addEventListener("change", () => {
      const p = loadProgress();
      if (cb.checked) p[key] = true;
      else delete p[key];
      saveProgress(p);
      lbl.textContent = cb.checked ? " ✔ Studiato" : " ☐ Segna come studiato";
      updateGlobalSummary();
    });
    wrap.appendChild(cb);
    wrap.appendChild(lbl);
    h1.parentNode.insertBefore(wrap, h1.nextSibling);
  }

  function updateGlobalSummary() {
    // Inietta/aggiorna il riepilogo nella landing page.
    const target = document.getElementById("ecppt-global-progress");
    if (!target) return;
    const total = parseInt(target.dataset.total || "0", 10);
    const progress = loadProgress();
    const done = Object.keys(progress).length;
    const pct = total ? Math.round((done / total) * 100) : 0;
    target.innerHTML = `
      <div class="ecppt-progress-summary">
        <div class="ecppt-progress-summary-text"><strong>${done}/${total}</strong> pagine studiate (${pct}%)</div>
        <div class="ecppt-progress-bar"><div class="ecppt-progress-bar-fill" style="width:${pct}%"></div></div>
        <button id="ecppt-progress-reset" class="md-button md-button--secondary" style="margin-top:.8rem">Reset progress</button>
      </div>`;
    const btn = document.getElementById("ecppt-progress-reset");
    if (btn) {
      btn.onclick = () => {
        if (confirm("Sicuro? Cancella tutto il progresso.")) {
          localStorage.removeItem(STORAGE_KEY);
          updateGlobalSummary();
        }
      };
    }
  }

  function init() {
    injectCheckbox();
    updateGlobalSummary();
  }

  // MkDocs Material usa instant navigation: hook su location$ + DOMContentLoaded
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  }
})();
