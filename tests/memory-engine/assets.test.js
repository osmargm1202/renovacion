/**
 * Tests for Asset Management
 */

const { AssetManager } = require('../../lib/memory-engine/assets');
const fs = require('fs').promises;
const path = require('path');

describe('AssetManager', () => {
  const testProjectPath = path.join(__dirname, '../fixtures/test-project');
  let assetManager;

  beforeEach(() => {
    assetManager = new AssetManager(999, testProjectPath);
  });

  afterEach(async () => {
    // Cleanup test assets
    try {
      await fs.rm(path.join(testProjectPath, 'assets'), { recursive: true, force: true });
    } catch (err) {
      // Ignore
    }
  });

  test('should initialize asset directories', async () => {
    await assetManager.init();
    
    const logosDir = await fs.stat(assetManager.logosDir);
    const equiposDir = await fs.stat(assetManager.equiposDir);
    const placeholdersDir = await fs.stat(assetManager.placeholdersDir);
    
    expect(logosDir.isDirectory()).toBe(true);
    expect(equiposDir.isDirectory()).toBe(true);
    expect(placeholdersDir.isDirectory()).toBe(true);
  });

  test('should create placeholder images', async () => {
    await assetManager.init();
    
    const logoPlaceholder = await fs.readFile(
      path.join(assetManager.placeholdersDir, 'placeholder-logo.svg'),
      'utf-8'
    );
    const equipmentPlaceholder = await fs.readFile(
      path.join(assetManager.placeholdersDir, 'placeholder-equipment.svg'),
      'utf-8'
    );
    
    expect(logoPlaceholder).toContain('<svg');
    expect(logoPlaceholder).toContain('Logo');
    expect(equipmentPlaceholder).toContain('<svg');
    expect(equipmentPlaceholder).toContain('not available');
  });

  test('should return placeholder for missing logo', async () => {
    await assetManager.init();
    
    const result = await assetManager.resolveLogo(null, 'empresa');
    
    expect(result).toBe('assets/placeholders/placeholder-logo.svg');
    expect(assetManager.warnings.length).toBeGreaterThan(0);
  });

  test('should return placeholder for missing equipment image', async () => {
    await assetManager.init();
    
    const result = await assetManager.resolveEquipmentImage(null);
    
    expect(result).toBe('assets/placeholders/placeholder-equipment.svg');
    expect(assetManager.warnings.length).toBeGreaterThan(0);
  });

  test('should handle invalid URL gracefully', async () => {
    await assetManager.init();
    
    const result = await assetManager.resolveLogo('https://invalid.url.that.does.not.exist/logo.png', 'test');
    
    expect(result).toBe('assets/placeholders/placeholder-logo.svg');
    expect(assetManager.warnings.some(w => w.includes('Failed to download'))).toBe(true);
  });

  test('should collect warnings', async () => {
    await assetManager.init();
    
    await assetManager.resolveLogo(null, 'empresa');
    await assetManager.resolveEquipmentImage(null);
    
    const warnings = assetManager.getWarnings();
    
    expect(warnings.length).toBeGreaterThanOrEqual(2);
    expect(warnings.some(w => w.includes('logo'))).toBe(true);
    expect(warnings.some(w => w.includes('equipment'))).toBe(true);
  });
});
