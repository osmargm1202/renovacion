/**
 * Selección de Equipos (Equipment Selection) Section Renderer
 */

function renderSeleccionEquipos(specData, stagedAssets) {
  const { equipment_specs } = specData;

  if (!equipment_specs || equipment_specs.length === 0) {
    return `
<div id="seleccion-equipos" class="page">
  <h1>Selección de Equipos</h1>
  <div class="infobox warning">
    <div class="infobox-title">Sin Equipos</div>
    <div>No hay equipos especificados en este proyecto.</div>
  </div>
  <div class="footer">Memoria de Cálculo - Renovación de Aire</div>
</div>
`;
  }

  return `
<div id="seleccion-equipos" class="page">
  <h1>Selección de Equipos</h1>
  
  ${equipment_specs.map((spec, idx) => renderEquipment(spec, stagedAssets, idx)).join('\n')}
  
  <div class="footer">Memoria de Cálculo - Renovación de Aire</div>
</div>
`;
}

function renderEquipment(spec, stagedAssets, index) {
  const {
    equipment_id,
    equipment_alias,
    kind,
    required_m3_h,
    selection_status,
    selection_reason,
    selected_model,
    alternatives
  } = spec;

  // Find staged assets for this equipment
  const equipAssets = stagedAssets.equipment?.find(e => e.equipment_id === equipment_id);
  const selectedImagePath = equipAssets?.selected || 'assets/placeholders/placeholder-equipment.svg';

  if (selection_status === 'failed' || !selected_model) {
    return renderFailedSelection(spec);
  }

  return `
  <div class="equipment-card ${index > 0 ? 'page-break-before' : ''}">
    <div class="equipment-header">
      <div class="equipment-title">${equipment_id}: ${equipment_alias}</div>
      <div class="equipment-subtitle">Tipo: ${kind} | Caudal Requerido: ${required_m3_h?.toFixed(2) || 'N/A'} m³/h</div>
    </div>
    
    <div class="equipment-body">
      <div class="equipment-image-container">
        <img src="${selectedImagePath}" alt="${selected_model.model}" class="equipment-image ${selectedImagePath.includes('placeholder') ? 'placeholder' : ''}">
        <div class="equipment-selected-badge">SELECCIONADO</div>
      </div>
      
      <div class="equipment-specs">
        <h3 style="margin-top: 0;">Modelo Seleccionado</h3>
        
        <div class="equipment-spec-row">
          <div class="equipment-spec-label">Marca:</div>
          <div class="equipment-spec-value">${selected_model.brand || 'N/A'}</div>
        </div>
        
        <div class="equipment-spec-row">
          <div class="equipment-spec-label">Modelo:</div>
          <div class="equipment-spec-value"><strong>${selected_model.model || 'N/A'}</strong></div>
        </div>
        
        <div class="equipment-spec-row">
          <div class="equipment-spec-label">Caudal:</div>
          <div class="equipment-spec-value"><strong>${selected_model.airflow_m3_h?.toFixed(2) || 'N/A'} m³/h</strong></div>
        </div>
        
        <div class="equipment-spec-row">
          <div class="equipment-spec-label">Voltaje:</div>
          <div class="equipment-spec-value">${selected_model.voltage || 'N/A'} V</div>
        </div>
        
        <div class="equipment-spec-row">
          <div class="equipment-spec-label">Frecuencia:</div>
          <div class="equipment-spec-value">${selected_model.frequency_hz || 'N/A'} Hz</div>
        </div>
        
        <div class="equipment-spec-row">
          <div class="equipment-spec-label">Potencia:</div>
          <div class="equipment-spec-value">${selected_model.power_w || 'N/A'} W (${selected_model.power_kw?.toFixed(3) || 'N/A'} kW)</div>
        </div>
        
        <div class="equipment-spec-row">
          <div class="equipment-spec-label">Instalación:</div>
          <div class="equipment-spec-value">${selected_model.installation_type || 'N/A'}</div>
        </div>
        
        ${selection_reason ? `
        <div style="margin-top: 0.15in; padding: 0.08in; background: #e8f4f8; border: 1px solid #0066cc; font-size: 8.5pt;">
          <strong>Razón de selección:</strong><br>
          ${selection_reason}
        </div>
        ` : ''}
      </div>
    </div>
    
    ${renderAlternatives(alternatives, equipAssets)}
  </div>
  `;
}

function renderAlternatives(alternatives, equipAssets) {
  if (!alternatives || alternatives.length === 0) {
    return `
    <div class="equipment-alternatives">
      <div class="equipment-alternatives-title">Alternativas</div>
      <div style="font-style: italic; color: #999;">No hay alternativas disponibles</div>
    </div>
    `;
  }

  const rows = alternatives.map(alt => `
    <tr>
      <td class="text-left">${alt.brand || 'N/A'}</td>
      <td class="text-left"><strong>${alt.model || 'N/A'}</strong></td>
      <td class="text-right">${alt.airflow_m3_h?.toFixed(2) || 'N/A'}</td>
      <td class="text-center">${alt.voltage || 'N/A'}</td>
      <td class="text-center">${alt.frequency_hz || 'N/A'}</td>
      <td class="text-right">${alt.power_w || 'N/A'}</td>
      <td class="text-center">${alt.installation_type || 'N/A'}</td>
    </tr>
  `).join('');

  return `
  <div class="equipment-alternatives">
    <div class="equipment-alternatives-title">Alternativas Disponibles</div>
    <table class="equipment-alternatives-table">
      <thead>
        <tr>
          <th class="text-left">Marca</th>
          <th class="text-left">Modelo</th>
          <th class="text-right">Caudal (m³/h)</th>
          <th class="text-center">Voltaje (V)</th>
          <th class="text-center">Frecuencia (Hz)</th>
          <th class="text-right">Potencia (W)</th>
          <th class="text-center">Instalación</th>
        </tr>
      </thead>
      <tbody>
        ${rows}
      </tbody>
    </table>
  </div>
  `;
}

function renderFailedSelection(spec) {
  return `
  <div class="equipment-card">
    <div class="equipment-header">
      <div class="equipment-title">${spec.equipment_id}: ${spec.equipment_alias}</div>
      <div class="equipment-subtitle">Tipo: ${spec.kind} | Caudal Requerido: ${spec.required_m3_h?.toFixed(2) || 'N/A'} m³/h</div>
    </div>
    
    <div class="equipment-selection-failed">
      <div class="equipment-selection-failed-title">⚠ Selección Fallida</div>
      <div>
        No se pudo seleccionar un modelo que cumpla con los requisitos para este equipo.
      </div>
      ${spec.selection_reason ? `
      <div style="margin-top: 0.08in;">
        <strong>Razón:</strong> ${spec.selection_reason}
      </div>
      ` : ''}
    </div>
    
    ${spec.alternatives ? renderAlternatives(spec.alternatives, null) : ''}
  </div>
  `;
}

module.exports = { renderSeleccionEquipos };
