#!/usr/bin/env node
/**
 * Regression tests for print/memory polish changes.
 * Run with: node tests/memory-engine/regression-hardening.test.js
 */
const assert = require('assert');
const fs = require('fs');
const path = require('path');

const { AssetManager } = require('../../lib/memory-engine/assets');
const { renderPortada } = require('../../lib/memory-engine/sections/portada');
const { renderTeoriaCalculo } = require('../../lib/memory-engine/sections/teoria-calculo');
const { renderResultadosCalculo } = require('../../lib/memory-engine/sections/resultados-calculo');

async function test(name, fn) {
  try {
    await fn();
    console.log(`✓ ${name}`);
  } catch (err) {
    console.error(`✗ ${name}`);
    console.error(err.message);
    process.exitCode = 1;
  }
}

const project = {
  name: 'AURORA GMR',
  cliente: 'BOHC SRL',
  ubicacion: 'Distrito Nacional',
  ingeniero: 'Osmar Garcia',
  codia: '36467',
  empresa_calculo: 'ORGM',
};

const resultados = {
  summary: {
    total_required_m3_h: 129.6,
    total_required_cfm: 76.28,
    areas_count: 1,
    equipment_count: 1,
    governing_method_counts: { rh: 1, people: 0, tie: 0 },
  },
  area_results: [
    {
      area_id: 'A1',
      area_alias: 'Baño principal',
      catalog_type: 'Cuartos de baño',
      catalog_sector: 'residencial_domestico',
      inputs: {
        dimensions: { length_m: 2, width_m: 4, height_m: 2.7 },
        volume_m3: 21.6,
        people: null,
      },
      methods: {
        rh: {
          applicable: true,
          source: 'rules/renovacion.json.tablas_renovaciones_aire',
          rh_target: 6,
          rh_min: 5,
          rh_max: 7,
          result_m3_h: 129.6,
          result_cfm: 76.28,
          trace_structured: {
            formula: 'required_m3_h = volume_m3 * rh_target',
            inputs: { volume_m3: 21.6, rh_target: 6 },
            output: 129.6,
            unit: 'm3/h',
          },
          trace_human: 'Q_rh = V * RH = 21.60 * 6.00 = 129.60 m3/h',
        },
        people: {
          applicable: false,
          source: 'rules/renovacion.json.tabla_caudal_por_persona',
          result_m3_h: null,
          result_cfm: null,
          trace_human: 'Not applicable: people is null',
          trace_structured: { formula: null, inputs: {}, output: null, unit: 'm3/h' },
        },
      },
      governing_method: 'rh',
      required_m3_h_final: 129.6,
      required_cfm_final: 76.28,
      linked_equipment_ids: ['E1'],
    },
  ],
};

test('asset manager returns null for missing cover logos so portada prints empty slot', async () => {
  const manager = new AssetManager(999, path.join(__dirname, '../fixtures/no-logo-project'));
  await manager.init();
  const logo = await manager.resolveLogo(null, 'empresa');
  assert.strictEqual(logo, null);
  await fs.promises.rm(path.join(__dirname, '../fixtures/no-logo-project'), { recursive: true, force: true });
});

test('cover preserves logo slots without printing placeholders when logos are missing', () => {
  const html = renderPortada(project, {});
  assert(!html.includes('placeholder-logo.svg'), 'missing logos must not render placeholder image');
  assert(html.includes('portada-logo-slot empty'), 'empty logo slot should preserve layout space');
});

test('cover renders client logo before company logo when both exist', () => {
  const html = renderPortada(project, {
    logo_empresa: 'assets/logos/empresa.png',
    logo_cliente: 'assets/logos/cliente.png',
  });
  assert(html.indexOf('assets/logos/cliente.png') < html.indexOf('assets/logos/empresa.png'));
});

test('theory renders Spanish policy labels without raw English policy keys', () => {
  const html = renderTeoriaCalculo({
    rounding_policy: 'round-2-decimals',
    range_policy: 'midpoint',
    governing_policy: 'max-of-both',
  });
  assert(html.includes('Valor medio del rango'));
  assert(html.includes('Mayor caudal calculado'));
  assert(html.includes('Redondeo a 2 decimales'));
  assert(!html.includes('midpoint'));
  assert(!html.includes('max-of-both'));
  assert(!html.includes('round-2-decimals'));
  assert(html.includes('page-break-before'), 'policy block should start on a new printed page');
});

test('theory documents CFM conversion formulas', () => {
  const html = renderTeoriaCalculo({});
  assert(html.includes('Q_{CFM}'));
  assert(html.includes('\\times 0.58858'), 'CFM formula should preserve LaTeX \\times, not a tab escape');
  assert(html.includes('\\times 1.69901'), 'm3/h formula should preserve LaTeX \\times, not a tab escape');
});

test('results use Spanish heading, hide source file paths, and show m3/h plus CFM', () => {
  const html = renderResultadosCalculo(resultados);
  assert(html.includes('Análisis por Área'));
  assert(!html.includes('Breakdown por Área'));
  assert(!html.includes('Fuente:'));
  assert(!html.includes('rules/renovacion.json'));
  assert(html.includes('129.60 m³/h'));
  assert(html.includes('76.28 CFM'));
});

test('print footer is not absolutely positioned', () => {
  const css = fs.readFileSync(path.join(__dirname, '../../assets/css/memoria.css'), 'utf-8');
  const footerBlock = css.match(/\.footer\s*\{[\s\S]*?\}/)[0];
  assert(!footerBlock.includes('position: absolute'), 'footer must not be absolute for print');
  assert(footerBlock.includes('margin-top: auto'), 'footer should sit at bottom in flex page layout');
});

if (process.exitCode) process.exit(process.exitCode);
