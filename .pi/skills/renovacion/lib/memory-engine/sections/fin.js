/**
 * Fin (Closing) Section Renderer
 */

function renderFin(projectData) {
  const { name, ingeniero, codia } = projectData;
  
  const fecha = new Date().toLocaleDateString('es-DO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  return `
<div id="fin" class="page no-page-number">
  <div class="fin">
    <div class="fin-titulo">
      Fin del Documento
    </div>
    
    <div class="fin-nota">
      Este documento constituye la memoria de cálculo para el sistema de renovación 
      de aire del proyecto <strong>${name}</strong>, y ha sido elaborado conforme a 
      las normas y mejores prácticas de ingeniería aplicables.
    </div>
    
    <div class="fin-nota">
      Los cálculos, selección de equipos y especificaciones técnicas contenidos en 
      esta memoria son responsabilidad del ingeniero firmante y están sujetos a 
      revisión y aprobación por las autoridades competentes.
    </div>
    
    <div class="fin-firma">
      <div style="margin-top: 1in; border-top: 1px solid #333; width: 3in; margin-left: auto; margin-right: auto; padding-top: 0.1in;">
        ${ingeniero || 'Ingeniero Responsable'}<br>
        ${codia ? `CODIA ${codia}` : ''}<br>
        ${fecha}
      </div>
    </div>
  </div>
</div>
`;
}

module.exports = { renderFin };
