// eCPPT - rende collapsible le voci del TOC integrato nella sidebar sinistra.
// Default: TUTTO CHIUSO. localStorage memorizza i CAPITOLI APERTI dall'utente.
(function() {
  const STORAGE_KEY = "ecppt-nav-open";
  const PRIMARY = ".md-sidebar--primary .md-nav";

  function loadOpen() {
    try { return new Set(JSON.parse(localStorage.getItem(STORAGE_KEY) || "[]")); }
    catch (e) { return new Set(); }
  }
  function saveOpen(set) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(set)));
  }

  function nodeKey(item) {
    const a = item.querySelector(":scope > .md-nav__link, :scope > a");
    return a ? (a.textContent || "").trim() : "";
  }

  function setState(item, childNav, toggle, open) {
    if (open) {
      childNav.style.display = "";
      item.classList.remove("ecppt-closed");
      item.classList.add("ecppt-open");
      toggle.innerHTML = "▾";
    } else {
      childNav.style.display = "none";
      item.classList.remove("ecppt-open");
      item.classList.add("ecppt-closed");
      toggle.innerHTML = "▸";
    }
  }

  function applyCollapsible(root) {
    const open = loadOpen();
    const items = root.querySelectorAll("li.md-nav__item");
    items.forEach(item => {
      const childNav = item.querySelector(":scope > nav.md-nav");
      if (!childNav) return;
      if (item.dataset.ecpptInit) return;
      item.dataset.ecpptInit = "1";
      item.classList.add("ecppt-collapsible");
      const key = nodeKey(item);
      const link = item.querySelector(":scope > .md-nav__link, :scope > a");
      if (!link) return;

      // Toggle visivo (chevron) + link in un wrapper flex sulla stessa riga,
      // cosi' il chevron sta a fianco del titolo e non a meta' del childNav.
      const toggle = document.createElement("button");
      toggle.type = "button";
      toggle.className = "ecppt-toggle";
      toggle.setAttribute("aria-label", "Espandi/comprimi sezione");

      const row = document.createElement("div");
      row.className = "ecppt-row";
      link.parentNode.insertBefore(row, link);
      row.appendChild(toggle);
      row.appendChild(link);

      // Stato iniziale: CHIUSO di default.
      setState(item, childNav, toggle, open.has(key));

      toggle.addEventListener("click", (e) => {
        e.preventDefault();
        e.stopPropagation();
        const wasOpen = item.classList.contains("ecppt-open");
        setState(item, childNav, toggle, !wasOpen);
        const s = loadOpen();
        if (wasOpen) s.delete(key); else s.add(key);
        saveOpen(s);
      });

      // Doppio-click sul testo del link = toggle anche quello
      link.addEventListener("dblclick", (e) => {
        e.preventDefault();
        const wasOpen = item.classList.contains("ecppt-open");
        setState(item, childNav, toggle, !wasOpen);
        const s = loadOpen();
        if (wasOpen) s.delete(key); else s.add(key);
        saveOpen(s);
      });
    });
  }

  function init() {
    const root = document.querySelector(PRIMARY);
    if (!root) return;
    applyCollapsible(root);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(init);
  }
})();
