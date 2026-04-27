/**
 * Memory Engine - Main Renderer
 * Orchestrates demanda-only memoria.html generation
 */

const fs = require("fs").promises;
const path = require("path");
const { AssetManager } = require("./assets");
const { getKaTeXIncludes } = require("./formula");
const { renderPortada } = require("./sections/portada");
const { renderIndice } = require("./sections/indice");
const { renderTeoriaCalculo } = require("./sections/teoria-calculo");
const { renderResultadosCalculo } = require("./sections/resultados-calculo");
const {
	renderResumenNecesidadArea,
} = require("./sections/resumen-necesidad-area");
const { renderFin } = require("./sections/fin");

class MemoryEngine {
	constructor(projectId, projectPath) {
		this.projectId = projectId;
		this.projectPath = projectPath;
		this.assetManager = new AssetManager(projectId, projectPath);
	}

	async loadJSON(filePath) {
		const content = await fs.readFile(filePath, "utf-8");
		return JSON.parse(content);
	}

	async loadCSS() {
		const cssPath = path.join(__dirname, "../../assets/css");
		const memoriaCSS = await fs.readFile(
			path.join(cssPath, "memoria.css"),
			"utf-8",
		);
		const sectionsCSS = await fs.readFile(
			path.join(cssPath, "memoria-sections.css"),
			"utf-8",
		);
		return `${memoriaCSS}\n\n${sectionsCSS}`;
	}

	async generate() {
		try {
			const inputPath = path.join(this.projectPath, "input.json");
			const resultadosPath = path.join(this.projectPath, "resultados.json");

			const inputData = await this.loadJSON(inputPath);
			const resultadosData = await this.loadJSON(resultadosPath);

			const stagedAssets = await this.assetManager.stageAll(inputData);
			const css = await this.loadCSS();

			const portada = renderPortada(inputData.project, stagedAssets);
			const indice = renderIndice();
			const teoriaCalculo = renderTeoriaCalculo(
				resultadosData.calculation_trace,
			);
			const resultadosCalculo = renderResultadosCalculo(resultadosData);
			const resumenNecesidadArea = renderResumenNecesidadArea(resultadosData);
			const fin = renderFin(inputData.project);

			const html = this.assembleHTML({
				project: inputData.project,
				css,
				sections: {
					portada,
					indice,
					teoriaCalculo,
					resultadosCalculo,
					resumenNecesidadArea,
					fin,
				},
			});

			const outputPath = path.join(this.projectPath, "memoria.html");
			await fs.writeFile(outputPath, html, "utf-8");

			return {
				status: "completed",
				output_path: outputPath,
				warnings: this.assetManager.getWarnings(),
			};
		} catch (err) {
			return {
				status: "failed",
				error: err.message,
				stack: err.stack,
			};
		}
	}

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
  
  <!-- RESUMEN DE NECESIDAD POR ÁREA -->
  ${sections.resumenNecesidadArea}
  
  <!-- FIN -->
  ${sections.fin}
</body>
</html>
`;
	}
}

async function generateMemoria(projectId, projectPath) {
	const engine = new MemoryEngine(projectId, projectPath);
	return await engine.generate();
}

module.exports = {
	MemoryEngine,
	generateMemoria,
};
