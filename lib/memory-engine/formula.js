/**
 * Memory Engine - Formula Rendering
 * Converts structured calculation traces to KaTeX/LaTeX formulas
 */

/**
 * Render formula from structured trace
 */
function renderFormulaKaTeX(trace) {
  if (!trace || !trace.formula) {
    return null;
  }

  try {
    const formula = convertTraceToLatex(trace);
    if (!formula) return null;

    return {
      type: 'katex',
      latex: formula,
      html: `<div class="formula-katex">
  <div class="katex-display">$$${formula}$$</div>
</div>`
    };
  } catch (err) {
    console.warn('Failed to convert trace to LaTeX:', err);
    return null;
  }
}

/**
 * Convert structured trace to LaTeX formula
 */
function convertTraceToLatex(trace) {
  const { formula, inputs, output, unit } = trace;

  // Handle RH method: Q = V × RH
  if (formula === 'required_m3_h = volume_m3 * rh_target') {
    const V = inputs.volume_m3 || 0;
    const RH = inputs.rh_target || 0;
    const Q = output || 0;
    
    return `Q_{RH} = V \\times RH = ${V.toFixed(2)} \\times ${RH.toFixed(2)} = ${Q.toFixed(2)}\\text{ m}^3\\text{/h}`;
  }

  // Handle People method: Q = N × caudal_persona
  if (formula === 'required_m3_h = people * caudal_persona_target') {
    const N = inputs.people || 0;
    const caudal = inputs.caudal_persona_target || 0;
    const Q = output || 0;
    
    return `Q_{people} = N \\times c = ${N} \\times ${caudal.toFixed(2)} = ${Q.toFixed(2)}\\text{ m}^3\\text{/h}`;
  }

  // Generic formula conversion
  if (trace.operation === 'multiply' && Object.keys(inputs).length === 2) {
    const values = Object.values(inputs);
    const keys = Object.keys(inputs);
    return `${keys[0]} \\times ${keys[1]} = ${values[0]} \\times ${values[1]} = ${output}`;
  }

  return null;
}

/**
 * Render formula from human trace (fallback)
 */
function renderFormulaHuman(traceHuman) {
  if (!traceHuman) {
    return {
      type: 'human',
      text: 'No trace available',
      html: '<div class="formula"><em>No calculation trace available</em></div>'
    };
  }

  return {
    type: 'human',
    text: traceHuman,
    html: `<div class="formula">${escapeHtml(traceHuman)}</div>`
  };
}

/**
 * Render formula (hybrid mode)
 * Try structured → KaTeX first, fall back to human trace
 */
function renderFormula(traceStructured, traceHuman) {
  // Try KaTeX rendering
  const katex = renderFormulaKaTeX(traceStructured);
  if (katex) {
    return katex;
  }

  // Fall back to human trace
  return renderFormulaHuman(traceHuman);
}

/**
 * Escape HTML entities
 */
function escapeHtml(text) {
  const map = {
    '&': '&amp;',
    '<': '&lt;',
    '>': '&gt;',
    '"': '&quot;',
    "'": '&#39;'
  };
  return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Get KaTeX local include tags (vendored assets)
 */
function getKaTeXIncludes() {
  return `
<!-- KaTeX CSS (vendored) -->
<link rel="stylesheet" href="../../assets/vendor/katex/katex.min.css">
<!-- KaTeX JS (vendored) -->
<script defer src="../../assets/vendor/katex/katex.min.js"></script>
<script defer src="../../assets/vendor/katex/auto-render.min.js" onload="renderMathInElement(document.body, {
  delimiters: [
    {left: '$$', right: '$$', display: true},
    {left: '$', right: '$', display: false}
  ]
});"></script>
`;
}

module.exports = {
  renderFormula,
  renderFormulaKaTeX,
  renderFormulaHuman,
  getKaTeXIncludes
};
