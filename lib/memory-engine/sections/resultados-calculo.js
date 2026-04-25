/**
 * Resultados de Cálculo (Calculation Results) Section Renderer
 */

const { renderFormula } = require('../formula');

function renderResultadosCalculo(resultadosData) {
  const { summary, area_results } = resultadosData;

  return `
<div id="resultados-calculo" class="page">
  <h1>Resultados de Cálculo</h1>
  
  ${renderSummary(summary)}
  
  <h2>Breakdown por Área</h2>
  ${area_results.map(renderArea).join('\n')}
  
  <div class="footer">Memoria de Cálculo - Renovación de Aire</div>
</div>
`;
}

function renderSummary(summary) {
  if (!summary) return '';

  return `
  <div class="resultados-summary">
    <div class="resultados-summary-title">Resumen Global del Proyecto</div>
    <div class="resultados-summary-grid">
      <div class="resultados-summary-item">
        <div class="resultados-summary-label">Caudal Total Requerido:</div>
        <div>${summary.total_required_m3_h?.toFixed(2) || 'N/A'} m³/h</div>
      </div>
      <div class="resultados-summary-item">
        <div class="resultados-summary-label">Áreas Calculadas:</div>
        <div>${summary.areas_count || 0}</div>
      </div>
      <div class="resultados-summary-item">
        <div class="resultados-summary-label">Equipos Requeridos:</div>
        <div>${summary.equipment_count || 0}</div>
      </div>
      <div class="resultados-summary-item">
        <div class="resultados-summary-label">Método RH (áreas):</div>
        <div>${summary.governing_method_counts?.rh || 0}</div>
      </div>
      <div class="resultados-summary-item">
        <div class="resultados-summary-label">Método Personas (áreas):</div>
        <div>${summary.governing_method_counts?.people || 0}</div>
      </div>
      <div class="resultados-summary-item">
        <div class="resultados-summary-label">Empate (áreas):</div>
        <div>${summary.governing_method_counts?.tie || 0}</div>
      </div>
    </div>
  </div>
  `;
}

function renderArea(area) {
  const {
    area_id,
    area_alias,
    catalog_type,
    catalog_sector,
    inputs,
    methods,
    governing_method,
    required_m3_h_final
  } = area;

  return `
  <div class="resultados-area avoid-break">
    <div class="resultados-area-header">
      <div class="resultados-area-title">
        ${area_id}: ${area_alias}
      </div>
      <div style="font-size: 8.5pt; margin-top: 0.03in; color: #555;">
        Tipo: ${catalog_type} | Sector: ${catalog_sector}
      </div>
    </div>
    
    <div style="margin-bottom: 0.15in;">
      <strong>Dimensiones:</strong>
      ${inputs.dimensions?.length_m?.toFixed(2) || 'N/A'} m × 
      ${inputs.dimensions?.width_m?.toFixed(2) || 'N/A'} m × 
      ${inputs.dimensions?.height_m?.toFixed(2) || 'N/A'} m
      (Volumen: ${inputs.volume_m3?.toFixed(2) || 'N/A'} m³)
    </div>
    
    ${renderMethod('Método RH', methods.rh)}
    ${renderMethod('Método por Personas', methods.people)}
    
    <div class="resultados-governing">
      <strong>Método Gobernante:</strong> ${governing_method?.toUpperCase() || 'N/A'}<br>
      <strong>Caudal Requerido Final:</strong> ${required_m3_h_final?.toFixed(2) || 'N/A'} m³/h
    </div>
  </div>
  `;
}

function renderMethod(title, method) {
  if (!method) {
    return `
    <div class="resultados-method">
      <div class="resultados-method-title">${title}</div>
      <div class="resultados-method-na">No disponible</div>
    </div>
    `;
  }

  if (!method.applicable) {
    return `
    <div class="resultados-method">
      <div class="resultados-method-title">${title}</div>
      <div class="resultados-method-na">No aplicable: ${method.trace_human || 'N/A'}</div>
    </div>
    `;
  }

  const formula = renderFormula(method.trace_structured, method.trace_human);

  return `
  <div class="resultados-method">
    <div class="resultados-method-title">${title}</div>
    <div>
      <strong>Fuente:</strong> <code style="font-size: 7.5pt;">${method.source || 'N/A'}</code>
    </div>
    ${title.includes('RH') ? `
    <div style="margin-top: 0.05in; font-size: 8.5pt;">
      RH objetivo: ${method.rh_target || 'N/A'} renovaciones/hora 
      (Rango: ${method.rh_min || 'N/A'} - ${method.rh_max || 'N/A'})
    </div>
    ` : ''}
    ${title.includes('Personas') ? `
    <div style="margin-top: 0.05in; font-size: 8.5pt;">
      Caudal por persona: ${method.caudal_persona_target || 'N/A'} m³/h·persona
    </div>
    ` : ''}
    <div style="margin-top: 0.08in;">
      ${formula.html}
    </div>
    <div style="margin-top: 0.05in;">
      <strong>Resultado:</strong> ${method.result_m3_h?.toFixed(2) || 'N/A'} m³/h
    </div>
  </div>
  `;
}

module.exports = { renderResultadosCalculo };
