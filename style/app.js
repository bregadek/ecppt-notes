// notes-app.js — motore dell'app appunti eCPPT
// Legge window.NOTES_DATA generato da _tools/build_notes_data.py
// Rendering: marked.js + highlight.js  |  No dipendenze extra

(function () {
  // ── Dati ──────────────────────────────────────────────────────────────────
  const DATA = window.NOTES_DATA;
  if (!DATA) {
    console.error('window.NOTES_DATA non trovato. Esegui _tools/build_notes_data.py prima di aprire il sito.');
    return;
  }
  const MODULES = DATA.modules;   // [{id, title, sections:[{slug,title}], content}]
  const CHEATSHEET_MD = DATA.cheatsheet;

  // ── Stato ─────────────────────────────────────────────────────────────────
  let currentModId = MODULES[0].id;
  let currentView  = 'notes';
  let activeSection = null;       // slug dell'H2 attiva (per TOC + sidebar)
  const DONE_KEY = 'ecppt-done';

  function getDone() {
    try { return new Set(JSON.parse(localStorage.getItem(DONE_KEY) || '[]')); }
    catch { return new Set(); }
  }
  function saveDone(set) {
    localStorage.setItem(DONE_KEY, JSON.stringify([...set]));
  }

  // ── Slug ──────────────────────────────────────────────────────────────────
  // Deve corrispondere esattamente a build_notes_data.py::slugify
  function slugify(text) {
    return text.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
  }

  // ── Progress topbar ───────────────────────────────────────────────────────
  function updateProgress() {
    const done = getDone();
    const total = MODULES.length;
    const count = MODULES.filter(m => done.has(m.id)).length;
    const fill = document.getElementById('progress-fill');
    const label = document.getElementById('progress-label');
    if (fill) fill.style.width = (count / total * 100) + '%';
    if (label) label.textContent = `${count} / ${total}`;
  }

  // ── Sidebar ────────────────────────────────────────────────────────────────
  function renderSidebar() {
    const tree = document.getElementById('module-tree');
    if (!tree) return;
    const done = getDone();
    tree.innerHTML = '';

    MODULES.forEach(m => {
      const isActive = m.id === currentModId;
      const wrap = document.createElement('div');
      wrap.className = 'module' + (isActive ? ' open' : '');
      wrap.dataset.module = m.id;

      // Calcola quante sezioni sono "viste" (stesso modulo = tutte visibili)
      const secCount = m.sections.length;
      const isDone = done.has(m.id);

      // Testa del modulo
      const head = document.createElement('div');
      head.className = 'module-head' + (isActive ? ' active-mod' : '');
      head.innerHTML = `
        <svg class="chev" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="m9 18 6-6-6-6"/>
        </svg>
        <span class="mod-num">${m.id}</span>
        <span class="mod-title">${m.title}</span>
        <button class="done-btn${isDone ? ' is-done' : ''}" title="Segna come completato" type="button">
          ${isDone ? '✓' : ''}
        </button>
      `;

      // Click sull'header → espandi + carica modulo
      head.addEventListener('click', () => {
        const wasOpen = wrap.classList.contains('open');
        if (!wasOpen) {
          wrap.classList.add('open');
          loadModule(m.id);
        } else if (m.id !== currentModId) {
          loadModule(m.id);
        } else {
          wrap.classList.toggle('open');
        }
      });

      // Click sul bottone done → toggle completato (senza propagare al head)
      head.querySelector('.done-btn').addEventListener('click', e => {
        e.stopPropagation();
        const d = getDone();
        d.has(m.id) ? d.delete(m.id) : d.add(m.id);
        saveDone(d);
        renderSidebar();
        updateProgress();
      });

      // Sezioni H2
      const secList = document.createElement('div');
      secList.className = 'sections';

      m.sections.forEach(sec => {
        const el = document.createElement('div');
        const isActiveSec = isActive && activeSection === sec.slug;
        el.className = 'section-item' + (isActiveSec ? ' active-sec' : '');
        el.dataset.slug = sec.slug;
        el.innerHTML = `<span class="sec-title">${escHtml(sec.title)}</span>`;
        el.addEventListener('click', e => {
          e.stopPropagation();
          if (m.id !== currentModId) {
            loadModule(m.id, sec.slug);
          } else {
            scrollToSlug(sec.slug);
          }
        });
        secList.appendChild(el);
      });

      wrap.appendChild(head);
      wrap.appendChild(secList);
      tree.appendChild(wrap);
    });
  }

  // ── Content ────────────────────────────────────────────────────────────────
  function loadModule(id, scrollToSlugAfter) {
    currentModId = id;
    activeSection = null;
    switchToView('notes');

    const mod = MODULES.find(m => m.id === id);
    if (!mod) return;

    // Fade-out
    const content = document.getElementById('notes-view') || document.querySelector('.content');
    const docEl = document.getElementById('doc');
    if (docEl) {
      docEl.style.opacity = '0';
      docEl.style.transition = 'opacity 0.15s ease';
    }

    requestAnimationFrame(() => {
      renderContent(mod, scrollToSlugAfter);
      if (docEl) {
        docEl.style.opacity = '0';
        // Trigger reflow per animazione fade-in
        void docEl.offsetWidth;
        docEl.style.opacity = '1';
      }
      if (content) content.scrollTop = 0;
      renderSidebar();
    });
  }

  function renderContent(mod, scrollToSlugAfter) {
    const docEl = document.getElementById('doc');
    if (!docEl) return;

    const html = window.marked ? window.marked.parse(mod.content) : escHtml(mod.content);

    docEl.innerHTML = html;

    // Genera ID sugli heading e arricchisce i code block
    assignHeadingIds(docEl);
    enhanceCodeBlocks(docEl);
    enhanceBlockquotes(docEl);
    interceptCheatsheetLinks(docEl);

    renderBreadcrumb(mod);
    renderToc(docEl);
    renderPager(mod.id);
    renderQuiz(mod);

    if (scrollToSlugAfter) {
      // Piccolo delay per lasciare finire il render
      requestAnimationFrame(() => scrollToSlug(scrollToSlugAfter));
    }

    setupTocObserver(docEl);
  }

  function assignHeadingIds(container) {
    container.querySelectorAll('h2, h3').forEach((h, idx) => {
      const slug = slugify(h.textContent || '') || `h-${idx}`;
      h.id = slug;
      // Aggiunge ancoraggio visivo
      h.style.scrollMarginTop = '68px';
    });
  }

  function enhanceCodeBlocks(container) {
    container.querySelectorAll('pre').forEach(pre => {
      const code = pre.querySelector('code');
      if (!code) return;
      const match = code.className.match(/language-(\w+)/);
      const lang = match ? match[1] : 'shell';

      const head = document.createElement('div');
      head.className = 'codehead';
      head.innerHTML = `
        <span class="code-lang">${lang}</span>
        <button class="copy-btn" type="button">Copia</button>
      `;
      pre.insertBefore(head, code);

      if (window.hljs) {
        try { window.hljs.highlightElement(code); } catch (_) {}
      }

      head.querySelector('.copy-btn').addEventListener('click', () => {
        if (navigator.clipboard) {
          navigator.clipboard.writeText(code.textContent).then(() => {
            const btn = head.querySelector('.copy-btn');
            btn.textContent = '✓ Copiato';
            btn.classList.add('copied');
            setTimeout(() => { btn.textContent = 'Copia'; btn.classList.remove('copied'); }, 1400);
          });
        }
      });
    });
  }

  function enhanceBlockquotes(container) {
    container.querySelectorAll('blockquote').forEach(bq => {
      if (/attenzione|warning|⚠|attn/i.test(bq.textContent)) {
        bq.classList.add('warn');
      }
    });
  }

  // ── Breadcrumb ─────────────────────────────────────────────────────────────
  function renderBreadcrumb(mod) {
    const el = document.getElementById('breadcrumb');
    if (!el) return;
    el.innerHTML = `
      <span class="crumb">Appunti</span>
      <span class="sep">/</span>
      <span class="crumb active-crumb">${escHtml(mod.title)}</span>
    `;
  }

  // ── TOC ────────────────────────────────────────────────────────────────────
  function renderToc(container) {
    const list = document.getElementById('toc-list');
    if (!list) return;
    list.innerHTML = '';
    container.querySelectorAll('h2, h3').forEach(h => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `#${h.id}`;
      a.textContent = h.textContent;
      if (h.tagName === 'H3') a.classList.add('h3');
      a.addEventListener('click', e => {
        e.preventDefault();
        scrollToSlug(h.id);
      });
      li.appendChild(a);
      list.appendChild(li);
    });
  }

  let tocObserver = null;
  function setupTocObserver(container) {
    if (tocObserver) tocObserver.disconnect();
    const headings = [...container.querySelectorAll('h2, h3')];
    if (!headings.length) return;

    tocObserver = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        const id = entry.target.id;
        const link = document.querySelector(`#toc-list a[href="#${CSS.escape(id)}"]`);
        if (link) link.classList.toggle('active', entry.isIntersecting);
        if (entry.isIntersecting) {
          activeSection = id;
          highlightSidebarSection(id);
        }
      });
    }, { rootMargin: '-10% 0px -80% 0px' });

    headings.forEach(h => tocObserver.observe(h));
  }

  function highlightSidebarSection(slug) {
    document.querySelectorAll('.section-item').forEach(el => {
      el.classList.toggle('active-sec', el.dataset.slug === slug);
    });
  }

  // ── Pager ──────────────────────────────────────────────────────────────────
  function renderPager(currentId) {
    const pager = document.getElementById('pager');
    if (!pager) return;
    const idx = MODULES.findIndex(m => m.id === currentId);
    const prev = idx > 0 ? MODULES[idx - 1] : null;
    const next = idx < MODULES.length - 1 ? MODULES[idx + 1] : null;
    pager.innerHTML = '';

    if (prev) {
      const a = makePagerBtn('prev', '← Precedente', prev.title);
      a.addEventListener('click', () => loadModule(prev.id));
      pager.appendChild(a);
    } else {
      pager.appendChild(document.createElement('span'));
    }

    if (next) {
      const a = makePagerBtn('next', 'Successivo →', next.title);
      a.addEventListener('click', () => loadModule(next.id));
      pager.appendChild(a);
    } else {
      pager.appendChild(document.createElement('span'));
    }
  }

  function makePagerBtn(cls, label, title) {
    const a = document.createElement('a');
    a.className = cls;
    a.innerHTML = `<span class="pager-label">${label}</span><span class="pager-title">${escHtml(title)}</span>`;
    return a;
  }

  // ── Scroll ─────────────────────────────────────────────────────────────────
  function scrollToSlug(slug) {
    const target = document.getElementById(slug);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      activeSection = slug;
      highlightSidebarSection(slug);
    }
  }

  // ── Views ──────────────────────────────────────────────────────────────────
  function switchToView(view) {
    document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.view === view));
    if (currentView === view) return;
    currentView = view;

    const notesView   = document.getElementById('notes-view');
    const csView      = document.getElementById('cheatsheet-view');
    const toc         = document.getElementById('toc');
    const tocCs       = document.getElementById('toc-cs');
    const moduleTree  = document.getElementById('module-tree');
    const csNav       = document.getElementById('cs-nav');
    const navLabel    = document.getElementById('nav-label');
    const searchInput = document.getElementById('search-input');

    if (view === 'notes') {
      notesView  && (notesView.style.display = '');
      csView     && csView.classList.remove('active');
      toc        && (toc.style.display = '');
      tocCs      && tocCs.classList.remove('active');
      moduleTree && (moduleTree.style.display = '');
      csNav      && csNav.classList.remove('active');
      if (navLabel)   navLabel.textContent = 'Moduli';
      if (searchInput) searchInput.placeholder = 'Cerca moduli e sezioni…';
      document.getElementById('cs-back')?.setAttribute('hidden', '');
    } else {
      notesView  && (notesView.style.display = 'none');
      csView     && csView.classList.add('active');
      toc        && (toc.style.display = 'none');
      tocCs      && tocCs.classList.add('active');
      moduleTree && (moduleTree.style.display = 'none');
      renderCheatsheet();
      renderCheatsheetNav();
      renderCheatsheetToc();
      csNav      && csNav.classList.add('active');
      if (navLabel)   navLabel.textContent = 'Sezioni';
      if (searchInput) searchInput.placeholder = 'Cerca sezioni…';
    }
  }

  // ── Cheatsheet links (intercept ../10_Cheatsheet.md#... → navigate in app) ──
  function findHeadingByFragment(container, fragment) {
    const norm = fragment.replace(/[^a-z0-9]/g, '');
    for (const h of container.querySelectorAll('h2, h3')) {
      if (h.id.replace(/[^a-z0-9]/g, '') === norm) return h;
    }
    return null;
  }

  function interceptCheatsheetLinks(container) {
    container.querySelectorAll('a[href*="10_Cheatsheet"]').forEach(a => {
      const fragment = (a.getAttribute('href').split('#')[1] || '').toLowerCase();
      a.setAttribute('href', '#');
      a.classList.add('cs-link');
      a.addEventListener('click', e => {
        e.preventDefault();
        // Show back button pointing to current module
        const backEl = document.getElementById('cs-back');
        if (backEl) {
          const mod = MODULES.find(m => m.id === currentModId);
          backEl.querySelector('.cs-back-label').textContent = mod ? mod.title : 'Appunti';
          backEl.removeAttribute('hidden');
        }
        switchToView('cheatsheet');
        if (!fragment) return;
        requestAnimationFrame(() => {
          const csDoc = document.getElementById('cheatsheet-doc');
          if (!csDoc) return;
          const h = findHeadingByFragment(csDoc, fragment);
          if (h) h.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
      });
    });
  }

  // ── Quiz ──────────────────────────────────────────────────────────────────
  function renderQuiz(mod) {
    document.getElementById('quiz-section')?.remove();
    if (!mod.quiz || !mod.quiz.length) return;

    // Fisher-Yates shuffle → pick 10
    const pool = [...mod.quiz];
    for (let i = pool.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [pool[i], pool[j]] = [pool[j], pool[i]];
    }
    const qs = pool.slice(0, Math.min(10, pool.length));

    const section = document.createElement('section');
    section.id = 'quiz-section';
    section.innerHTML = `
      <div class="quiz-header">
        <h2 class="quiz-title">Quiz · ${escHtml(mod.title)}</h2>
        <span class="quiz-badge">${qs.length} domande casuali</span>
      </div>
      <div class="quiz-body"></div>
      <div class="quiz-footer">
        <button class="quiz-submit" type="button">Controlla risposte</button>
        <div class="quiz-score" hidden></div>
        <button class="quiz-retry" type="button" hidden>Nuovo quiz</button>
      </div>
    `;

    const body = section.querySelector('.quiz-body');
    qs.forEach((q, idx) => {
      const div = document.createElement('div');
      div.className = 'quiz-q';
      div.dataset.correct = q.correct;
      div.innerHTML = `
        <p class="qnum">${idx + 1}<span class="qnum-of"> / ${qs.length}</span></p>
        <p class="qtext">${escHtml(q.q)}</p>
        <div class="qchoices">${q.choices.map((c, ci) => `
          <label class="qchoice">
            <input type="radio" name="q${idx}" value="${ci}">
            <span>${escHtml(c)}</span>
          </label>`).join('')}
        </div>
        ${q.explanation ? `<p class="qexp" hidden>${escHtml(q.explanation)}</p>` : ''}
      `;
      body.appendChild(div);
    });

    section.querySelector('.quiz-submit').addEventListener('click', () => {
      let score = 0;
      body.querySelectorAll('.quiz-q').forEach((qEl, idx) => {
        const correct = parseInt(qEl.dataset.correct);
        const chosen  = qEl.querySelector(`input[name="q${idx}"]:checked`);
        qEl.querySelectorAll('input').forEach(i => (i.disabled = true));
        qEl.querySelectorAll('.qchoice').forEach((lbl, ci) => {
          if (ci === correct) lbl.classList.add('correct');
          else if (chosen && parseInt(chosen.value) === ci) lbl.classList.add('wrong');
        });
        if (chosen && parseInt(chosen.value) === correct) score++;
        qEl.querySelector('.qexp')?.removeAttribute('hidden');
      });

      const pct = Math.round(score / qs.length * 100);
      const cls = pct >= 80 ? 'score-hi' : pct >= 50 ? 'score-mid' : 'score-lo';
      const scoreEl = section.querySelector('.quiz-score');
      scoreEl.innerHTML = `<span class="${cls}">${score}/${qs.length} corrette &middot; ${pct}%</span>`;
      scoreEl.removeAttribute('hidden');
      section.querySelector('.quiz-submit').setAttribute('hidden', '');
      section.querySelector('.quiz-retry').removeAttribute('hidden');
    });

    section.querySelector('.quiz-retry').addEventListener('click', () => {
      renderQuiz(mod);
      requestAnimationFrame(() =>
        document.getElementById('quiz-section')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
      );
    });

    const pager = document.getElementById('pager');
    if (pager) pager.before(section);
    else document.getElementById('notes-view')?.appendChild(section);
  }

  // ── Cheatsheet content ─────────────────────────────────────────────────────
  let cheatsheetRendered = false;
  function renderCheatsheet() {
    if (cheatsheetRendered) return;
    const el = document.getElementById('cheatsheet-doc');
    if (!el || !CHEATSHEET_MD) return;
    const html = window.marked ? window.marked.parse(CHEATSHEET_MD) : escHtml(CHEATSHEET_MD);
    el.innerHTML = html;
    assignHeadingIds(el);
    enhanceCodeBlocks(el);
    enhanceBlockquotes(el);
    cheatsheetRendered = true;
  }

  // ── Cheatsheet TOC ─────────────────────────────────────────────────────────
  let csTocRendered = false;
  function renderCheatsheetToc() {
    if (csTocRendered) return;
    const csDoc = document.getElementById('cheatsheet-doc');
    const csTocList = document.getElementById('toc-cs-list');
    if (!csDoc || !csTocList) return;

    let csTocObserver = null;

    csTocList.innerHTML = '';
    csDoc.querySelectorAll('h2, h3').forEach(h => {
      const li = document.createElement('li');
      const a = document.createElement('a');
      a.href = `#${h.id}`;
      a.textContent = h.textContent;
      if (h.tagName === 'H3') a.classList.add('h3');
      a.addEventListener('click', e => {
        e.preventDefault();
        h.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      li.appendChild(a);
      csTocList.appendChild(li);
    });

    // IntersectionObserver per highlight attivo nel TOC cheatsheet
    const csView = document.getElementById('cheatsheet-view');
    if (csTocObserver) csTocObserver.disconnect();
    const headings = [...csDoc.querySelectorAll('h2, h3')];
    if (headings.length && csView) {
      csTocObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          const id = entry.target.id;
          const link = csTocList.querySelector(`a[href="#${CSS.escape(id)}"]`);
          if (link) link.classList.toggle('active', entry.isIntersecting);
        });
      }, { root: csView, rootMargin: '-10% 0px -80% 0px' });
      headings.forEach(h => csTocObserver.observe(h));
    }

    csTocRendered = true;
  }

  // ── Cheatsheet sidebar nav ─────────────────────────────────────────────────
  let csNavRendered  = false;
  let csNavObserver  = null;

  function renderCheatsheetNav() {
    if (csNavRendered) return;
    const csDoc = document.getElementById('cheatsheet-doc');
    const csNav = document.getElementById('cs-nav');
    if (!csDoc || !csNav || !csDoc.innerHTML) return;

    csNav.innerHTML = '';
    const headings = [...csDoc.querySelectorAll('h2')];

    headings.forEach((h, idx) => {
      const el = document.createElement('div');
      el.className = 'cs-item';
      el.dataset.slug = h.id;
      el.innerHTML = `
        <span class="cs-item-num">${String(idx + 1).padStart(2, '0')}</span>
        <span class="cs-item-title">${escHtml(h.textContent)}</span>
      `;
      el.addEventListener('click', () => {
        h.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
      csNav.appendChild(el);
    });

    // IntersectionObserver per highlight sezione attiva nella sidebar
    const csView = document.getElementById('cheatsheet-view');
    if (csNavObserver) csNavObserver.disconnect();
    if (headings.length && csView) {
      csNavObserver = new IntersectionObserver(entries => {
        entries.forEach(entry => {
          const item = csNav.querySelector(`.cs-item[data-slug="${CSS.escape(entry.target.id)}"]`);
          if (item) item.classList.toggle('active-cs', entry.isIntersecting);
        });
      }, { root: csView, rootMargin: '-5% 0px -75% 0px' });
      headings.forEach(h => csNavObserver.observe(h));
    }

    csNavRendered = true;
  }

  // ── Ricerca ────────────────────────────────────────────────────────────────
  function setupSearch() {
    const input = document.getElementById('search-input');
    if (!input) return;

    input.addEventListener('input', e => {
      const q = e.target.value.trim().toLowerCase();

      if (currentView === 'cheatsheet') {
        // Filtra le sezioni della cheatsheet nella sidebar
        document.querySelectorAll('.cs-item').forEach(el => {
          const title = el.querySelector('.cs-item-title')?.textContent.toLowerCase() || '';
          el.style.display = (!q || title.includes(q)) ? '' : 'none';
        });
        return;
      }

      // Filtra l'albero dei moduli (vista appunti)
      document.querySelectorAll('.module').forEach(mEl => {
        const mid = mEl.dataset.module;
        const mod = MODULES.find(m => m.id === mid);
        if (!mod) return;

        if (!q) {
          mEl.style.display = '';
          mEl.querySelectorAll('.section-item').forEach(s => (s.style.display = ''));
          return;
        }

        const modMatch = mod.title.toLowerCase().includes(q);
        let anySec = false;
        mEl.querySelectorAll('.section-item').forEach(sEl => {
          const title = sEl.querySelector('.sec-title')?.textContent.toLowerCase() || '';
          const match = title.includes(q);
          sEl.style.display = match ? '' : 'none';
          if (match) anySec = true;
        });

        mEl.style.display = (modMatch || anySec) ? '' : 'none';
        if (anySec) mEl.classList.add('open');
      });
    });

    // Ctrl/Cmd + K → focus
    document.addEventListener('keydown', e => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        input.focus();
        input.select();
      }
      // Esc → svuota
      if (e.key === 'Escape' && document.activeElement === input) {
        input.value = '';
        input.dispatchEvent(new Event('input'));
        input.blur();
      }
    });
  }

  // ── Tabs ───────────────────────────────────────────────────────────────────
  function setupTabs() {
    document.querySelectorAll('.tab').forEach(t => {
      t.addEventListener('click', () => switchToView(t.dataset.view));
    });
  }

  // ── Utilità ────────────────────────────────────────────────────────────────
  function escHtml(s) {
    return (s || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  // ── Dark mode ──────────────────────────────────────────────────────────────
  function swapHljsTheme(theme) {
    const light = document.getElementById('hljs-light');
    const dark  = document.getElementById('hljs-dark');
    if (!light || !dark) return;
    light.disabled = (theme === 'dark');
    dark.disabled  = (theme === 'light');
  }

  function setThemeIcons(isDark) {
    const moon = document.getElementById('icon-moon');
    const sun  = document.getElementById('icon-sun');
    if (!moon || !sun) return;
    moon.style.display = isDark ? 'none' : '';
    sun.style.display  = isDark ? '' : 'none';
  }

  function initDarkMode() {
    const saved = localStorage.getItem('ecppt-theme');
    if (saved === 'dark') {
      document.documentElement.classList.add('dark');
      setThemeIcons(true);
      swapHljsTheme('dark');
    }
    document.getElementById('theme-toggle')?.addEventListener('click', () => {
      const isDark = document.documentElement.classList.toggle('dark');
      localStorage.setItem('ecppt-theme', isDark ? 'dark' : 'light');
      setThemeIcons(isDark);
      swapHljsTheme(isDark ? 'dark' : 'light');
    });
  }

  // ── Init ───────────────────────────────────────────────────────────────────
  window.initNotesApp = function () {
    if (window.marked) window.marked.setOptions({ breaks: false, gfm: true });
    initDarkMode();
    updateProgress();
    renderSidebar();
    loadModule(MODULES[0].id);
    setupSearch();
    setupTabs();
    document.getElementById('cs-back-btn')?.addEventListener('click', () => switchToView('notes'));
  };
})();
