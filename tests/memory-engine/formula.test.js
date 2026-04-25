/**
 * Tests for Formula Rendering
 */

const {
  renderFormula,
  renderFormulaKaTeX,
  renderFormulaHuman,
  getKaTeXIncludes
} = require('../../lib/memory-engine/formula');

describe('Formula Rendering', () => {
  describe('renderFormulaKaTeX', () => {
    test('should render RH method formula', () => {
      const trace = {
        formula: 'required_m3_h = volume_m3 * rh_target',
        inputs: {
          volume_m3: 21.6,
          rh_target: 6.0
        },
        operation: 'multiply',
        output: 129.6,
        unit: 'm3/h'
      };

      const result = renderFormulaKaTeX(trace);

      expect(result).toBeTruthy();
      expect(result.type).toBe('katex');
      expect(result.latex).toContain('Q_{RH}');
      expect(result.latex).toContain('21.60');
      expect(result.latex).toContain('6.00');
      expect(result.latex).toContain('129.60');
      expect(result.html).toContain('$$');
    });

    test('should render People method formula', () => {
      const trace = {
        formula: 'required_m3_h = people * caudal_persona_target',
        inputs: {
          people: 5,
          caudal_persona_target: 30.0
        },
        operation: 'multiply',
        output: 150.0,
        unit: 'm3/h'
      };

      const result = renderFormulaKaTeX(trace);

      expect(result).toBeTruthy();
      expect(result.type).toBe('katex');
      expect(result.latex).toContain('Q_{people}');
      expect(result.latex).toContain('5');
      expect(result.latex).toContain('30.00');
    });

    test('should return null for invalid trace', () => {
      const result = renderFormulaKaTeX(null);
      expect(result).toBeNull();
    });

    test('should return null for unknown formula', () => {
      const trace = {
        formula: 'unknown_formula',
        inputs: {},
        operation: null,
        output: null
      };

      const result = renderFormulaKaTeX(trace);
      expect(result).toBeNull();
    });
  });

  describe('renderFormulaHuman', () => {
    test('should render human trace', () => {
      const trace = 'Q_rh = V * RH = 21.60 * 6.00 = 129.60 m3/h';
      const result = renderFormulaHuman(trace);

      expect(result.type).toBe('human');
      expect(result.text).toBe(trace);
      expect(result.html).toContain(trace);
      expect(result.html).toContain('class="formula"');
    });

    test('should escape HTML entities', () => {
      const trace = 'Q = <script>alert("xss")</script>';
      const result = renderFormulaHuman(trace);

      expect(result.html).not.toContain('<script>');
      expect(result.html).toContain('&lt;script&gt;');
    });

    test('should handle null trace', () => {
      const result = renderFormulaHuman(null);

      expect(result.type).toBe('human');
      expect(result.html).toContain('No trace available');
    });
  });

  describe('renderFormula (hybrid)', () => {
    test('should prefer KaTeX over human trace', () => {
      const structured = {
        formula: 'required_m3_h = volume_m3 * rh_target',
        inputs: { volume_m3: 21.6, rh_target: 6.0 },
        operation: 'multiply',
        output: 129.6,
        unit: 'm3/h'
      };
      const human = 'Q_rh = V * RH = 21.60 * 6.00 = 129.60 m3/h';

      const result = renderFormula(structured, human);

      expect(result.type).toBe('katex');
      expect(result.latex).toBeTruthy();
    });

    test('should fallback to human trace when structured fails', () => {
      const structured = {
        formula: 'unknown_formula',
        inputs: {},
        operation: null,
        output: null
      };
      const human = 'Q = some calculation';

      const result = renderFormula(structured, human);

      expect(result.type).toBe('human');
      expect(result.text).toBe(human);
    });

    test('should handle both null inputs', () => {
      const result = renderFormula(null, null);

      expect(result.type).toBe('human');
      expect(result.html).toContain('No trace available');
    });
  });

  describe('getKaTeXIncludes', () => {
    test('should return KaTeX CDN includes', () => {
      const includes = getKaTeXIncludes();

      expect(includes).toContain('katex');
      expect(includes).toContain('cdn.jsdelivr.net');
      expect(includes).toContain('<link');
      expect(includes).toContain('<script');
    });
  });
});
