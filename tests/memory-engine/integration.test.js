/**
 * Integration Test - Full memoria.html generation
 */

const { generateMemoria } = require('../../lib/memory-engine');
const fs = require('fs').promises;
const path = require('path');

describe('MemoryEngine Integration', () => {
  const projectPath = path.join(__dirname, '../../proyectos/1');
  const outputPath = path.join(projectPath, 'memoria.html');

  afterEach(async () => {
    // Optional: cleanup generated file
    // await fs.unlink(outputPath).catch(() => {});
  });

  test('should generate complete memoria.html for project 1', async () => {
    const result = await generateMemoria(1, projectPath);

    expect(result.status).toBe('completed');
    expect(result.output_path).toBe(outputPath);

    // Verify file was created
    const fileExists = await fs.access(outputPath)
      .then(() => true)
      .catch(() => false);
    
    expect(fileExists).toBe(true);
  });

  test('generated HTML should contain all sections', async () => {
    await generateMemoria(1, projectPath);
    
    const html = await fs.readFile(outputPath, 'utf-8');

    // Check section IDs
    expect(html).toContain('id="portada"');
    expect(html).toContain('id="indice"');
    expect(html).toContain('id="teoria-calculo"');
    expect(html).toContain('id="resultados-calculo"');
    expect(html).toContain('id="seleccion-equipos"');
    expect(html).toContain('id="fin"');
  });

  test('generated HTML should contain project data', async () => {
    await generateMemoria(1, projectPath);
    
    const html = await fs.readFile(outputPath, 'utf-8');

    expect(html).toContain('AURORA GMR');
    expect(html).toContain('BOHC SRL');
    expect(html).toContain('Osmar Garcia');
    expect(html).toContain('36467');
    expect(html).toContain('Baño principal');
  });

  test('generated HTML should contain calculation results', async () => {
    await generateMemoria(1, projectPath);
    
    const html = await fs.readFile(outputPath, 'utf-8');

    expect(html).toContain('129.6'); // Required airflow
    expect(html).toContain('21.6'); // Volume
    expect(html).toContain('6.0'); // RH target (might be 6.00)
  });

  test('generated HTML should contain equipment selection', async () => {
    await generateMemoria(1, projectPath);
    
    const html = await fs.readFile(outputPath, 'utf-8');

    expect(html).toContain('EX-150'); // Selected model
    expect(html).toContain('140'); // Airflow of selected model
    expect(html).toContain('EX-160'); // Alternative 1
    expect(html).toContain('EX-200'); // Alternative 2
    expect(html).toContain('EX-250'); // Alternative 3
  });

  test('generated HTML should have embedded CSS', async () => {
    await generateMemoria(1, projectPath);
    
    const html = await fs.readFile(outputPath, 'utf-8');

    expect(html).toContain('<style>');
    expect(html).toContain('font-family: Arial');
    expect(html).toContain('.portada');
    expect(html).toContain('.equipment-card');
  });

  test('generated HTML should include KaTeX', async () => {
    await generateMemoria(1, projectPath);
    
    const html = await fs.readFile(outputPath, 'utf-8');

    expect(html).toContain('katex');
    expect(html).toContain('cdn.jsdelivr.net');
  });

  test('should handle missing optional data gracefully', async () => {
    const result = await generateMemoria(1, projectPath);

    expect(result.status).toBe('completed');
    expect(result.warnings).toBeDefined();
    // Should complete even with warnings
  });

  test('should fail gracefully for missing input files', async () => {
    const badPath = path.join(__dirname, '../fixtures/nonexistent');
    
    const result = await generateMemoria(999, badPath);

    expect(result.status).toBe('failed');
    expect(result.error).toBeDefined();
  });
});
