/**
 * Tests for MemoryEngine Main Renderer
 */

const { MemoryEngine } = require('../../lib/memory-engine');
const fs = require('fs').promises;
const path = require('path');

describe('MemoryEngine', () => {
  const testProjectPath = path.join(__dirname, '../fixtures/test-project');
  let engine;

  beforeEach(() => {
    engine = new MemoryEngine(999, testProjectPath);
  });

  describe('loadJSON', () => {
    test('should load and parse JSON file', async () => {
      const testFile = path.join(testProjectPath, 'test.json');
      await fs.mkdir(testProjectPath, { recursive: true });
      await fs.writeFile(testFile, JSON.stringify({ test: 'data' }));

      const data = await engine.loadJSON(testFile);

      expect(data).toEqual({ test: 'data' });

      await fs.rm(testProjectPath, { recursive: true, force: true });
    });
  });

  describe('loadCSS', () => {
    test('should load and concatenate CSS files', async () => {
      const css = await engine.loadCSS();

      expect(css).toContain('font-family: Arial');
      expect(css).toContain('.portada');
      expect(css).toContain('.equipment-card');
      expect(css.length).toBeGreaterThan(1000);
    });
  });

  describe('assembleHTML', () => {
    test('should assemble complete HTML document', () => {
      const params = {
        project: {
          name: 'Test Project'
        },
        css: '.test { color: red; }',
        sections: {
          portada: '<div id="portada">Portada</div>',
          indice: '<div id="indice">Indice</div>',
          teoriaCalculo: '<div id="teoria-calculo">Teoria</div>',
          resultadosCalculo: '<div id="resultados-calculo">Resultados</div>',
          seleccionEquipos: '<div id="seleccion-equipos">Equipos</div>',
          fin: '<div id="fin">Fin</div>'
        }
      };

      const html = engine.assembleHTML(params);

      expect(html).toContain('<!DOCTYPE html>');
      expect(html).toContain('<html lang="es">');
      expect(html).toContain('<title>Memoria de Cálculo - Test Project</title>');
      expect(html).toContain('.test { color: red; }');
      expect(html).toContain('<div id="portada">');
      expect(html).toContain('<div id="indice">');
      expect(html).toContain('<div id="teoria-calculo">');
      expect(html).toContain('<div id="resultados-calculo">');
      expect(html).toContain('<div id="seleccion-equipos">');
      expect(html).toContain('<div id="fin">');
      expect(html).toContain('katex');
    });
  });
});
