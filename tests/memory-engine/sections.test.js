/**
 * Tests for Section Renderers
 */

const { renderPortada } = require('../../lib/memory-engine/sections/portada');
const { renderIndice } = require('../../lib/memory-engine/sections/indice');
const { renderTeoriaCalculo } = require('../../lib/memory-engine/sections/teoria-calculo');
const { renderFin } = require('../../lib/memory-engine/sections/fin');

describe('Section Renderers', () => {
  describe('renderPortada', () => {
    test('should render cover page with all project data', () => {
      const project = {
        name: 'Test Project',
        cliente: 'Test Client',
        ubicacion: 'Test Location',
        ingeniero: 'Test Engineer',
        codia: '12345',
        empresa_calculo: 'Test Company'
      };

      const assets = {
        logo_empresa: 'assets/logos/empresa.png',
        logo_cliente: 'assets/logos/cliente.png'
      };

      const html = renderPortada(project, assets);

      expect(html).toContain('id="portada"');
      expect(html).toContain('Test Project');
      expect(html).toContain('Test Client');
      expect(html).toContain('Test Location');
      expect(html).toContain('Test Engineer');
      expect(html).toContain('12345');
      expect(html).toContain('Test Company');
      expect(html).toContain('assets/logos/empresa.png');
      expect(html).toContain('assets/logos/cliente.png');
    });

    test('should use placeholders for missing logos', () => {
      const project = {
        name: 'Test Project',
        ingeniero: 'Test Engineer'
      };

      const assets = {};

      const html = renderPortada(project, assets);

      expect(html).toContain('placeholder-logo.svg');
    });
  });

  describe('renderIndice', () => {
    test('should render table of contents with all sections', () => {
      const html = renderIndice();

      expect(html).toContain('id="indice"');
      expect(html).toContain('href="#portada"');
      expect(html).toContain('href="#teoria-calculo"');
      expect(html).toContain('href="#resultados-calculo"');
      expect(html).toContain('href="#seleccion-equipos"');
      expect(html).toContain('href="#fin"');
    });

    test('should include section numbers', () => {
      const html = renderIndice();

      expect(html).toContain('1.');
      expect(html).toContain('2.');
      expect(html).toContain('3.');
      expect(html).toContain('4.');
      expect(html).toContain('5.');
      expect(html).toContain('6.');
    });
  });

  describe('renderTeoriaCalculo', () => {
    test('should render theory section with policies', () => {
      const trace = {
        rounding_policy: 'round-2-decimals',
        range_policy: 'midpoint',
        governing_policy: 'max-of-both'
      };

      const html = renderTeoriaCalculo(trace);

      expect(html).toContain('id="teoria-calculo"');
      expect(html).toContain('Renovación de Aire');
      expect(html).toContain('Método por Renovaciones por Hora');
      expect(html).toContain('Método por Personas');
      expect(html).toContain('round-2-decimals');
      expect(html).toContain('midpoint');
      expect(html).toContain('max-of-both');
    });

    test('should handle missing trace', () => {
      const html = renderTeoriaCalculo(null);

      expect(html).toContain('id="teoria-calculo"');
      expect(html).toContain('Renovación de Aire');
    });
  });

  describe('renderFin', () => {
    test('should render closing section', () => {
      const project = {
        name: 'Test Project',
        ingeniero: 'Test Engineer',
        codia: '12345'
      };

      const html = renderFin(project);

      expect(html).toContain('id="fin"');
      expect(html).toContain('Fin del Documento');
      expect(html).toContain('Test Project');
      expect(html).toContain('Test Engineer');
      expect(html).toContain('12345');
    });
  });
});
