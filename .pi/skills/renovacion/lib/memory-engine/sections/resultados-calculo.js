/**
 * Resultados de Cálculo (Calculation Results) Section Renderer
 */

const { renderFormula } = require("../formula");

function renderResultadosCalculo(resultadosData) {
	const { summary, area_results } = resultadosData;

	return `
<div id="resultados-calculo" class="page">
  <h1>Resultados de Cálculo</h1>
  
  ${renderSummary(summary)}
  
  <h2>Análisis por Área</h2>
  ${area_results.map(renderArea).join("\n")}
  
  <div class="footer">Memoria de Cálculo - Renovación de Aire</div>
</div>
`;
}

function renderSummary(summary) {
	if (!summary) return "";

	return `
  <div class="resultados-summary">
    <div class="resultados-summary-title">Resumen Global del Proyecto</div>
    <div class="resultados-summary-grid">
      <div class="resultados-summary-item">
        <div class="resultados-summary-label">Caudal Total Requerido:</div>
        <div>${formatAirflow(summary.total_required_m3_h, summary.total_required_cfm)}</div>
      </div>
      <div class="resultados-summary-item">
        <div class="resultados-summary-label">Áreas Calculadas:</div>
        <div>${summary.areas_count || 0}</div>
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
		required_m3_h_final,
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
      ${inputs.dimensions?.length_m?.toFixed(2) || "N/A"} m × 
      ${inputs.dimensions?.width_m?.toFixed(2) || "N/A"} m × 
      ${inputs.dimensions?.height_m?.toFixed(2) || "N/A"} m
      (Volumen: ${inputs.volume_m3?.toFixed(2) || "N/A"} m³)
    </div>
    
    ${renderMethod("Método RH", methods.rh)}
    ${renderMethod("Método por Personas", methods.people)}
    
    <div class="resultados-governing">
      <strong>Método Gobernante:</strong> ${formatGoverningMethod(governing_method)}<br>
      <strong>Caudal Requerido Final:</strong> ${formatAirflow(required_m3_h_final, area.required_cfm_final)}
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
      <div class="resultados-method-na">No aplicable: ${method.trace_human || "N/A"}</div>
    </div>
    `;
	}

	const formula = renderFormula(method.trace_structured, method.trace_human);

	return `
  <div class="resultados-method">
    <div class="resultados-method-title">${title}</div>
    ${
			title.includes("RH")
				? `
    <div style="margin-top: 0.05in; font-size: 8.5pt;">
      RH objetivo: ${method.rh_target || "N/A"} renovaciones/hora 
      (Rango: ${method.rh_min || "N/A"} - ${method.rh_max || "N/A"})
    </div>
    `
				: ""
		}
    ${
			title.includes("Personas")
				? `
    <div style="margin-top: 0.05in; font-size: 8.5pt;">
      Caudal por persona: ${method.caudal_persona_target || "N/A"} m³/h·persona
    </div>
    `
				: ""
		}
    <div style="margin-top: 0.08in;">
      ${formula.html}
    </div>
    <div style="margin-top: 0.05in;">
      <strong>Resultado:</strong> ${formatAirflow(method.result_m3_h, method.result_cfm)}
    </div>
  </div>
  `;
}

function m3hToCfm(value) {
	if (value === null || value === undefined || Number.isNaN(Number(value)))
		return null;
	return Number((Number(value) * 0.5885777702).toFixed(2));
}

function formatAirflow(m3h, cfm) {
	const m3hText =
		m3h !== null && m3h !== undefined
			? `${Number(m3h).toFixed(2)} m³/h`
			: "N/A";
	const cfmValue = cfm !== null && cfm !== undefined ? cfm : m3hToCfm(m3h);
	const cfmText =
		cfmValue !== null ? `${Number(cfmValue).toFixed(2)} CFM` : "N/A";
	return `${m3hText} (${cfmText})`;
}

function formatGoverningMethod(method) {
	const labels = {
		rh: "Renovaciones por hora (RH)",
		people: "Personas",
		tie: "Empate entre métodos",
	};
	return labels[method] || "N/A";
}

module.exports = { renderResultadosCalculo, formatAirflow };
