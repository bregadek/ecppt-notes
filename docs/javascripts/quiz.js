// eCPPT - quiz INLINE a risposta multipla.
// Cerca <div class="ecppt-quiz" data-module="<slug>" data-block="<idx>"></div>
// e renderizza le 5 domande del blocco <idx> caricato da /quiz/<slug>.json.
//
// JSON atteso:
//   { "module": "Active Directory",
//     "blocks": [
//       { "after_h2": "PARTE 1 — AD PRIMER",
//         "title": "AD Primer",
//         "questions": [
//           { "q": "Testo", "choices": ["A","B","C","D"], "correct": 2, "explanation": "..." } ] } ] }
(function() {
  const STORAGE_KEY = "ecppt-quiz";
  const cache = {};   // module -> data

  function loadAnswers() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{}"); }
    catch (e) { return {}; }
  }
  function saveAnswers(o) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(o));
  }

  async function loadQuiz(module) {
    if (cache[module]) return cache[module];
    const baseHref = document.querySelector('base')?.href || (location.origin + '/');
    const resp = await fetch(`${baseHref}quiz/${module}.json`, { cache: "no-store" });
    if (!resp.ok) throw new Error(`Quiz HTTP ${resp.status}`);
    const data = await resp.json();
    cache[module] = data;
    return data;
  }

  function evaluate(block, q) {
    const chosen = block.querySelector("input:checked");
    if (!chosen) return;
    const correct = parseInt(chosen.value, 10) === q.correct;
    block.classList.remove("ecppt-correct", "ecppt-wrong");
    block.classList.add(correct ? "ecppt-correct" : "ecppt-wrong");
    const fb = block.querySelector(".ecppt-quiz-feedback");
    if (correct) {
      fb.innerHTML = `<strong>✓ Corretto.</strong> ${q.explanation || ""}`;
    } else {
      const right = q.choices[q.correct];
      fb.innerHTML = `<strong>✗ Sbagliato.</strong> Risposta corretta: <em>${right}</em>. ${q.explanation || ""}`;
    }
  }

  function updateBlockStats(blockData, module, blockIdx, statsEl) {
    const answers = (loadAnswers()[module] || {})[blockIdx] || {};
    let correct = 0, answered = 0;
    blockData.questions.forEach((q, i) => {
      if (answers[i] !== undefined) {
        answered++;
        if (answers[i] === q.correct) correct++;
      }
    });
    const total = blockData.questions.length;
    const pct = answered ? Math.round((correct / answered) * 100) : 0;
    statsEl.innerHTML = `
      <div class="ecppt-quiz-stats-text">
        Risposte: <strong>${answered}/${total}</strong> ·
        Corrette: <strong>${correct}/${answered || 0}</strong>
        (${pct}%)
      </div>`;
  }

  function renderBlock(container, data, module, blockIdx) {
    const blockData = data.blocks[blockIdx];
    if (!blockData) {
      container.innerHTML = `<em>Blocco quiz ${blockIdx} non trovato.</em>`;
      return;
    }
    container.innerHTML = "";
    const moduleAnswers = (loadAnswers()[module] || {})[blockIdx] || {};

    const stats = document.createElement("div");
    stats.className = "ecppt-quiz-stats";
    container.appendChild(stats);

    blockData.questions.forEach((q, i) => {
      const qBlock = document.createElement("div");
      qBlock.className = "ecppt-quiz-q";
      qBlock.dataset.idx = i;

      const qText = document.createElement("p");
      qText.className = "ecppt-quiz-q-text";
      qText.innerHTML = `<strong>${i + 1}.</strong> ${q.q}`;
      qBlock.appendChild(qText);

      const list = document.createElement("ul");
      list.className = "ecppt-quiz-choices";
      q.choices.forEach((choice, ci) => {
        const li = document.createElement("li");
        const lbl = document.createElement("label");
        const input = document.createElement("input");
        input.type = "radio";
        input.name = `q-${module}-${blockIdx}-${i}`;
        input.value = ci;
        if (moduleAnswers[i] === ci) input.checked = true;
        input.addEventListener("change", () => {
          const all = loadAnswers();
          all[module] = all[module] || {};
          all[module][blockIdx] = all[module][blockIdx] || {};
          all[module][blockIdx][i] = ci;
          saveAnswers(all);
          evaluate(qBlock, q);
          updateBlockStats(blockData, module, blockIdx, stats);
        });
        lbl.appendChild(input);
        lbl.appendChild(document.createTextNode(" " + choice));
        li.appendChild(lbl);
        list.appendChild(li);
      });
      qBlock.appendChild(list);

      const feedback = document.createElement("div");
      feedback.className = "ecppt-quiz-feedback";
      qBlock.appendChild(feedback);

      container.appendChild(qBlock);

      if (moduleAnswers[i] !== undefined) {
        evaluate(qBlock, q);
      }
    });

    const reset = document.createElement("button");
    reset.className = "md-button md-button--secondary";
    reset.textContent = "Resetta questo quiz";
    reset.style.marginTop = "1rem";
    reset.onclick = () => {
      if (!confirm("Cancello le tue risposte di questo blocco?")) return;
      const all = loadAnswers();
      if (all[module]) delete all[module][blockIdx];
      saveAnswers(all);
      renderBlock(container, data, module, blockIdx);
    };
    container.appendChild(reset);

    updateBlockStats(blockData, module, blockIdx, stats);
  }

  async function init() {
    const containers = document.querySelectorAll(".ecppt-quiz[data-module]");
    for (const c of containers) {
      if (c.dataset.ecpptInit) continue;
      c.dataset.ecpptInit = "1";
      const module = c.dataset.module;
      const blockIdx = parseInt(c.dataset.block || "0", 10);
      try {
        const data = await loadQuiz(module);
        renderBlock(c, data, module, blockIdx);
      } catch (e) {
        c.innerHTML = `<em>Quiz per "${module}" non ancora disponibile.</em>`;
      }
    }
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
