// eCPPT - Rimuove gli Zero-Width Space (U+200B) iniettati dal builder
// per evadere i signature-based AV nei file HTML del sito.
// Quando l'utente copia un comando (sia con il copy-button di Material
// sia con Ctrl+C), il testo che arriva in clipboard NON contiene ZWSP
// -> incollato in PowerShell/Bash e' identico all'originale.
(function() {
  // Rimuove sia ZERO-WIDTH SPACE (U+200B) sia WORD JOINER (U+2060):
  // entrambi usati per AV evasion, entrambi invisibili, entrambi da rimuovere
  // prima della copia per evitare di incollare caratteri estranei.
  const ZWSP_RE = /[\u200B\u2060]/g;

  // 1) Intercetta il copy-button (Material usa navigator.clipboard.writeText)
  if (navigator.clipboard && navigator.clipboard.writeText) {
    const original = navigator.clipboard.writeText.bind(navigator.clipboard);
    navigator.clipboard.writeText = function(text) {
      if (typeof text === "string") text = text.replace(ZWSP_RE, "");
      return original(text);
    };
  }

  // 2) Intercetta il Ctrl+C / selezione manuale
  document.addEventListener("copy", function(e) {
    const sel = (window.getSelection() || "").toString();
    if (!sel || !ZWSP_RE.test(sel)) return;
    ZWSP_RE.lastIndex = 0;
    e.preventDefault();
    const cleaned = sel.replace(ZWSP_RE, "");
    if (e.clipboardData) {
      e.clipboardData.setData("text/plain", cleaned);
    } else if (window.clipboardData) {  // IE legacy
      window.clipboardData.setData("Text", cleaned);
    }
  });
})();
