/**
 * Teoría de Cálculo (Calculation Theory) Section Renderer
 */

function renderTeoriaCalculo(calculationTrace) {
  const { rounding_policy, range_policy, governing_policy } = calculationTrace || {};

  return `
<div id="teoria-calculo" class="page">
  <h1>Teoría de Cálculo</h1>
  
  <div class="teoria-section">
    <h2>Renovación de Aire</h2>
    <p>
      La renovación de aire es un requisito fundamental para garantizar condiciones de
      salubridad y confort en espacios cerrados. El caudal requerido se determina en
      función del tipo de local, su volumen y, cuando aplica, la ocupación del espacio.
    </p>
  </div>

  <div class="teoria-section">
    <h2>Métodos de Cálculo</h2>
    
    <div class="teoria-subsection avoid-break">
      <h3>Método por Renovaciones por Hora (RH)</h3>
      <p>
        Este método calcula el caudal requerido multiplicando el volumen del local por
        el número de renovaciones de aire por hora correspondiente al tipo de espacio.
      </p>
      
      <div class="teoria-formula-block">
        <div class="teoria-equation"><strong>Q<sub>RH</sub> = V × RH</strong></div>
        <div class="teoria-definiciones">
          Donde:<br>
          Q<sub>RH</sub> = Caudal requerido (m³/h)<br>
          V = Volumen del local (m³)<br>
          RH = Renovaciones por hora (1/h)
        </div>
      </div>
    </div>

    <div class="teoria-subsection avoid-break">
      <h3>Método por Personas</h3>
      <p>
        Este método calcula el caudal en función del número de ocupantes y el caudal
        de aire exterior requerido por persona para el tipo de actividad del espacio.
      </p>
      
      <div class="teoria-formula-block">
        <div class="teoria-equation"><strong>Q<sub>personas</sub> = N × c</strong></div>
        <div class="teoria-definiciones">
          Donde:<br>
          Q<sub>personas</sub> = Caudal requerido (m³/h)<br>
          N = Número de personas<br>
          c = Caudal por persona (m³/h·persona)
        </div>
      </div>
    </div>

    <div class="teoria-subsection avoid-break">
      <h3>Conversión de Unidades</h3>
      <p>
        Para facilitar revisión y selección de equipos, los resultados se presentan en
        metros cúbicos por hora (m³/h) y en pies cúbicos por minuto (CFM).
      </p>
      <div class="teoria-formula-block">
        <div class="teoria-equation">$$Q_{CFM} = Q_{m^3/h} \\times 0.58858$$</div>
        <div class="teoria-equation">$$Q_{m^3/h} = Q_{CFM} \\times 1.69901$$</div>
      </div>
    </div>
  </div>

  <div class="footer">Memoria de Cálculo - Renovación de Aire</div>
</div>

<div class="page page-break-before">
  <h1>Políticas de Cálculo Aplicadas</h1>
  <div class="teoria-policy-page avoid-break">
    ${renderPolicy('Criterio para Rangos', range_policy, {
      'midpoint': 'Valor medio del rango normativo.',
      'min': 'Valor mínimo del rango normativo.',
      'max': 'Valor máximo del rango normativo.'
    })}
    ${renderPolicy('Criterio de Selección del Caudal', governing_policy, {
      'max-of-both': 'Mayor caudal calculado entre el método por renovaciones y el método por personas.',
      'rh-only': 'Solo método por renovaciones por hora.',
      'people-only': 'Solo método por personas.'
    })}
    ${renderPolicy('Criterio de Redondeo', rounding_policy, {
      'round-2-decimals': 'Redondeo a 2 decimales.',
      'round-1-decimal': 'Redondeo a 1 decimal.',
      'no-rounding': 'Sin redondeo de resultados.'
    })}
  </div>
  <div class="footer">Memoria de Cálculo - Renovación de Aire</div>
</div>
`;
}

function renderPolicy(title, value, descriptions) {
  if (!value) return '';
  const description = descriptions[value] || 'Criterio aplicado según configuración del proyecto.';
  return `
    <div class="teoria-policy">
      <div class="teoria-policy-title">${title}</div>
      <div>${description}</div>
    </div>
  `;
}

module.exports = { renderTeoriaCalculo };
