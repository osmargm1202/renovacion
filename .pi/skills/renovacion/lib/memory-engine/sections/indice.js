/**
 * Índice (Table of Contents) Section Renderer
 */

function renderIndice() {
	const sections = [
		{ number: "1", title: "Portada", anchor: "portada" },
		{ number: "2", title: "Índice", anchor: "indice" },
		{ number: "3", title: "Teoría de Cálculo", anchor: "teoria-calculo" },
		{
			number: "4",
			title: "Resultados de Cálculo",
			anchor: "resultados-calculo",
		},
		{
			number: "5",
			title: "Resumen de Necesidad por Área",
			anchor: "resumen-necesidad-area",
		},
		{ number: "6", title: "Fin del Documento", anchor: "fin" },
	];

	const items = sections
		.map(
			(s) => `
    <li class="indice-item">
      <span class="section-number">${s.number}.</span>
      <a href="#${s.anchor}">${s.title}</a>
    </li>
  `,
		)
		.join("");

	return `
<div id="indice" class="page">
  <div class="indice">
    <h1 class="indice-titulo">Índice</h1>
    <ul class="indice-list">
      ${items}
    </ul>
  </div>
  <div class="footer">Memoria de Cálculo - Renovación de Aire</div>
</div>
`;
}

module.exports = { renderIndice };
