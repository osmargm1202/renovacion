/**
 * Resumen de Necesidad por Área Section Renderer
 */

const { numberOrNull, formatNumber } = require("../number-format");

function m3hToCfm(value) {
	if (value === null || value === undefined || Number.isNaN(Number(value)))
		return null;
	return Number((Number(value) * 0.5885777702).toFixed(2));
}

function formatM3h(value) {
	const numeric = numberOrNull(value);
	if (numeric === null) return "N/A";
	return `${formatNumber(numeric)} m3/h`;
}

function formatCfm(m3h, cfm) {
	const explicit = numberOrNull(cfm);
	const converted = explicit === null ? m3hToCfm(m3h) : explicit;
	if (converted === null) return "N/A";
	return `${formatNumber(converted)} CFM`;
}

function renderRows(areaResults) {
	if (!areaResults || areaResults.length === 0) {
		return `
      <tr>
        <td colspan="5" class="text-center">No hay áreas calculadas.</td>
      </tr>
    `;
	}

	return areaResults
		.map((area) => {
			const requiredM3h = area.required_m3_h_final;
			const requiredCfm = area.required_cfm_final;
			const governing =
				{
					rh: "Renovaciones por hora (RH)",
					people: "Personas",
					tie: "Empate",
				}[area.governing_method] || "N/A";

			return `
      <tr>
        <td class="text-left">${area.area_id || "N/A"}</td>
        <td class="text-left">${area.area_alias || "N/A"}</td>
        <td class="text-left">${governing}</td>
        <td class="text-right"><strong>${formatM3h(requiredM3h)}</strong></td>
        <td class="text-right"><strong>${formatCfm(requiredM3h, requiredCfm)}</strong></td>
      </tr>
    `;
		})
		.join("");
}

function renderResumenNecesidadArea(resultadosData) {
	const areaResults = resultadosData.area_results || [];

	return `
<div id="resumen-necesidad-area" class="page">
  <h1>Resumen de Necesidad por Área</h1>
  <p>
    Esta sección consolida la demanda de renovación de aire requerida por área.
    Los valores provienen exclusivamente de <code>resultados.json</code> y expresan
    el caudal final requerido en m3/h y CFM.
  </p>

  <table class="equipment-alternatives-table">
    <thead>
      <tr>
        <th class="text-left">Área</th>
        <th class="text-left">Nombre</th>
        <th class="text-left">Método gobernante</th>
        <th class="text-right">Requerido (m3/h)</th>
        <th class="text-right">Requerido (CFM)</th>
      </tr>
    </thead>
    <tbody>
      ${renderRows(areaResults)}
    </tbody>
  </table>

  <div class="footer">Memoria de Cálculo - Renovación de Aire</div>
</div>
`;
}

module.exports = { renderResumenNecesidadArea, formatM3h, formatCfm };
