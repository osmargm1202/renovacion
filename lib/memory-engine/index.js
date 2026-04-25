/**
 * Memory Engine - Main Renderer
 * Orchestrates memoria.html generation
 */

const fs = require('fs').promises;
const path = require('path');
const { AssetManager } = require('./assets');
const { getKaTeXIncludes } = require('./formula');
const { renderPortada } = require('./sections/portada');
const { renderIndice } = require('./sections/indice');
const { renderTeoriaCalculo } = require('./sections/teoria-calculo');
const { renderResultadosCalculo } = require('./sections/resultados-calculo');
const { renderSeleccionEquipos } = require('./sections/seleccion-equipos');
const { renderFin } = require('./sections/fin');

class MemoryEngine {
  constructor(projectId, projectPath) {
    this.projectId = projectId;
    this.projectPath = projectPath;
    this.assetManager = new AssetManager(projectId, projectPath);
  }

  /**
   * Load JSON file
   */
  async loadJSON(filePath) {
    const content = await fs.readFile(filePath, 'utf-8');
    return JSON.parse(content);
  }

  /**
   * Load CSS files
   */
  async loadCSS() {
    const cssPath = path.join(__dirname, '../../assets/css');
    const memoriaCSS = await fs.readFile(path.join(cssPath, 'memoria.css'), 'utf-8');
    const sectionsCSS = await fs.readFile(path.join(cssPath, 'memoria-sections.css'), 'utf-8');
    return `${memoriaCSS}\n\n${sectionsCSS}`;
  }

  /**
   * Generate memoria.html
   */
  async generate() {
    try {
      // Load input files
      const inputPath = path.join(this.projectPath, 'input.json');
      const resultadosPath = path.join(this.projectPath, 'resultados.json');
      const specPath = path.join(this.projectPath, 'spec.json');

      const inputData = await this.loadJSON(inputPath);
      const resultadosData = await this.loadJSON(resultadosPath);
      const specData = await this.loadJSON(specPath);

      // Stage assets
      const stagedAssets = await this.assetManager.stageAll(inputData, specData);

      // Load CSS
      const css = await this.loadCSS();

      // Render sections
      const portada = renderPortada(inputData.project, stagedAssets);
      const indice = renderIndice();
      const teoriaCalculo = renderTeoriaCalculo(resultadosData.calculation_trace);
      const resultadosCalculo = renderResultadosCalculo(resultadosData);
      const seleccionEquipos = renderSeleccionEquipos(specData, stagedAssets);
      const fin = renderFin(inputData.project);

      // Assemble HTML
      const html = this.assembleHTML({
        project: inputData.project,
        css,
        sections: {
          portada,
          indice,
          teoriaCalculo,
          resultadosCalculo,
          seleccionEquipos,
          fin
        }
      });

      // Write output
      const outputPath = path.join(this.projectPath, 'memoria.html');
      await fs.writeFile(outputPath, html, 'utf-8');

      // Return result
      return {
        status: 'completed',
        output_path: outputPath,
        warnings: this.assetManager.getWarnings()
      };

    } catch (err) {
      return {
        status: 'failed',
        error: err.message,
        stack: err.stack
      };
    }
  }

  /**
   * Assemble final HTML document
   */
  assembleHTML({ project, css, sections }) {
    return `<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Memoria de Cálculo - ${project.name}</title>
  
  <!-- KaTeX -->
  ${getKaTeXIncludes()}
  
  <!-- Embedded CSS -->
  <style>
${css}
  </style>
</head>
<body>
  <!-- PORTADA -->
  ${sections.portada}
  
  <!-- ÍNDICE -->
  ${sections.indice}
  
  <!-- TEORÍA DE CÁLCULO -->
  ${sections.teoriaCalculo}
  
  <!-- RESULTADOS DE CÁLCULO -->
  ${sections.resultadosCalculo}
  
  <!-- SELECCIÓN DE EQUIPOS -->
  ${sections.seleccionEquipos}
  
  <!-- FIN -->
  ${sections.fin}
</body>
</html>
`;
  }
}

/**
 * Generate memoria for a project
 */
async function generateMemoria(projectId, projectPath) {
  const engine = new MemoryEngine(projectId, projectPath);
  return await engine.generate();
}

module.exports = {
  MemoryEngine,
  generateMemoria
};
