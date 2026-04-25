/**
 * Portada (Cover Page) Section Renderer
 */

function renderPortada(projectData, stagedAssets) {
  const {
    name,
    cliente,
    ubicacion,
    ingeniero,
    codia,
    empresa_calculo
  } = projectData;

  const logoEmpresa = stagedAssets.logo_empresa || null;
  const logoCliente = stagedAssets.logo_cliente || null;
  
  const fecha = new Date().toLocaleDateString('es-DO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  return `
<div id="portada" class="page no-page-number">
  <div class="portada">
    <div class="portada-logos">
      <div class="portada-logo-slot ${logoCliente ? '' : 'empty'}">
        ${logoCliente ? `<img src="${logoCliente}" alt="Logo ${cliente || 'Cliente'}" class="portada-logo">` : ''}
      </div>
      <div class="portada-logo-slot ${logoEmpresa ? '' : 'empty'}">
        ${logoEmpresa ? `<img src="${logoEmpresa}" alt="Logo ${empresa_calculo || 'Empresa'}" class="portada-logo">` : ''}
      </div>
    </div>
    
    <div class="portada-titulo">
      Memoria de Cálculo<br>
      Renovación de Aire
    </div>
    
    <div class="portada-proyecto">
      ${name}
    </div>
    
    <div class="portada-info">
      <div><strong>Cliente:</strong> ${cliente || 'N/A'}</div>
      <div><strong>Ubicación:</strong> ${ubicacion || 'N/A'}</div>
      <div><strong>Ingeniero Responsable:</strong> ${ingeniero || 'N/A'}</div>
      <div><strong>CODIA:</strong> ${codia || 'N/A'}</div>
      ${empresa_calculo ? `<div><strong>Empresa de Cálculo:</strong> ${empresa_calculo}</div>` : ''}
      <div><strong>Fecha:</strong> ${fecha}</div>
    </div>
    
    <div class="portada-firma">
      <div class="portada-firma-line">
        ${ingeniero || 'Ingeniero Responsable'}<br>
        ${codia ? `CODIA ${codia}` : ''}
      </div>
    </div>
  </div>
</div>
`;
}

module.exports = { renderPortada };
