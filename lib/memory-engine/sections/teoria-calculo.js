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
      salubridad y confort en espacios cerrados. El caudal de aire requerido se determina 
      en función del tipo de local y su ocupación.
    </p>
  </div>

  <div class="teoria-section">
    <h2>Métodos de Cálculo</h2>
    
    <div class="teoria-subsection">
      <h3>Método por Renovaciones por Hora (RH)</h3>
      <p>
        Este método calcula el caudal requerido multiplicando el volumen del local por 
        el número de renovaciones de aire por hora, según el tipo de espacio.
      </p>
      
      <div class="teoria-formula-block">
        <div class="teoria-equation">
          <strong>Q<sub>RH</sub> = V × RH</strong>
        </div>
        <div style="font-size: 8pt; margin-top: 0.08in; color: #555;">
          Donde:<br>
          Q<sub>RH</sub> = Caudal requerido (m³/h)<br>
          V = Volumen del local (m³)<br>
          RH = Renovaciones por hora (1/h)
        </div>
      </div>
      
      <p>
        El valor de RH se obtiene de tablas normativas según el tipo de local 
        (baños, cocinas, áreas residenciales, comerciales, etc.).
      </p>
    </div>

    <div class="teoria-subsection">
      <h3>Método por Personas</h3>
      <p>
        Este método calcula el caudal en función del número de ocupantes y el caudal 
        de aire exterior requerido por persona, según normas de ventilación.
      </p>
      
      <div class="teoria-formula-block">
        <div class="teoria-equation">
          <strong>Q<sub>personas</sub> = N × c</strong>
        </div>
        <div style="font-size: 8pt; margin-top: 0.08in; color: #555;">
          Donde:<br>
          Q<sub>personas</sub> = Caudal requerido (m³/h)<br>
          N = Número de personas<br>
          c = Caudal por persona (m³/h·persona)
        </div>
      </div>
      
      <p>
        El caudal por persona varía según el tipo de actividad y nivel de ocupación 
        del espacio (residencial, oficinas, áreas públicas, etc.).
      </p>
    </div>
  </div>

  <div class="teoria-section">
    <h2>Políticas de Cálculo Aplicadas</h2>
    
    ${renderPolicy('Política de Rangos', range_policy, {
      'midpoint': 'Se utiliza el valor medio del rango normativo (RH_min, RH_max)',
      'min': 'Se utiliza el valor mínimo del rango normativo',
      'max': 'Se utiliza el valor máximo del rango normativo'
    })}
    
    ${renderPolicy('Política de Método Gobernante', governing_policy, {
      'max-of-both': 'Se selecciona el mayor caudal entre RH y personas',
      'rh-only': 'Se utiliza únicamente el método RH',
      'people-only': 'Se utiliza únicamente el método por personas'
    })}
    
    ${renderPolicy('Política de Redondeo', rounding_policy, {
      'round-2-decimals': 'Resultados redondeados a 2 decimales',
      'round-1-decimal': 'Resultados redondeados a 1 decimal',
      'no-rounding': 'Sin redondeo de resultados'
    })}
  </div>

  <div class="footer">Memoria de Cálculo - Renovación de Aire</div>
</div>
`;
}

function renderPolicy(title, value, descriptions) {
  if (!value) return '';
  
  const description = descriptions[value] || value;
  
  return `
    <div class="teoria-policy">
      <div class="teoria-policy-title">${title}</div>
      <div><strong>Aplicada:</strong> <code>${value}</code></div>
      <div>${description}</div>
    </div>
  `;
}

module.exports = { renderTeoriaCalculo };
