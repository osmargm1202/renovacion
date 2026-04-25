/**
 * Memory Engine - Asset Staging and Resolution
 * Handles downloading, copying, and resolving assets for memoria generation
 */

const fs = require('fs').promises;
const path = require('path');
const https = require('https');
const http = require('http');

class AssetManager {
  constructor(projectId, projectPath) {
    this.projectId = projectId;
    this.projectPath = projectPath;
    this.assetsDir = path.join(projectPath, 'assets');
    this.logosDir = path.join(this.assetsDir, 'logos');
    this.equiposDir = path.join(this.assetsDir, 'equipos');
    this.placeholdersDir = path.join(this.assetsDir, 'placeholders');
    this.warnings = [];
  }

  /**
   * Initialize asset directories
   */
  async init() {
    await fs.mkdir(this.assetsDir, { recursive: true });
    await fs.mkdir(this.logosDir, { recursive: true });
    await fs.mkdir(this.equiposDir, { recursive: true });
    await fs.mkdir(this.placeholdersDir, { recursive: true });
    
    // Create placeholder images
    await this.createPlaceholders();
  }

  /**
   * Create placeholder SVG images
   */
  async createPlaceholders() {
    // Logo placeholder
    const logoPlaceholder = `<svg width="200" height="100" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="100" fill="#f0f0f0"/>
  <text x="100" y="50" font-family="Arial" font-size="16" fill="#999" text-anchor="middle" dominant-baseline="middle">Logo</text>
</svg>`;
    
    // Equipment placeholder
    const equipmentPlaceholder = `<svg width="400" height="300" xmlns="http://www.w3.org/2000/svg">
  <rect width="400" height="300" fill="#f5f5f5"/>
  <text x="200" y="140" font-family="Arial" font-size="16" fill="#999" text-anchor="middle">Image not available</text>
  <text x="200" y="160" font-family="Arial" font-size="12" fill="#aaa" text-anchor="middle">Imagen no disponible</text>
</svg>`;
    
    await fs.writeFile(path.join(this.placeholdersDir, 'placeholder-logo.svg'), logoPlaceholder);
    await fs.writeFile(path.join(this.placeholdersDir, 'placeholder-equipment.svg'), equipmentPlaceholder);
  }

  /**
   * Download file from URL
   */
  async downloadFile(url, destPath) {
    return new Promise((resolve, reject) => {
      const protocol = url.startsWith('https') ? https : http;
      const timeout = 10000; // 10 seconds

      const req = protocol.get(url, { timeout }, (res) => {
        if (res.statusCode === 301 || res.statusCode === 302) {
          // Follow redirect
          return this.downloadFile(res.headers.location, destPath)
            .then(resolve)
            .catch(reject);
        }

        if (res.statusCode !== 200) {
          reject(new Error(`HTTP ${res.statusCode}`));
          return;
        }

        const fileStream = require('fs').createWriteStream(destPath);
        res.pipe(fileStream);

        fileStream.on('finish', () => {
          fileStream.close();
          resolve(destPath);
        });

        fileStream.on('error', (err) => {
          fs.unlink(destPath).catch(() => {});
          reject(err);
        });
      });

      req.on('timeout', () => {
        req.destroy();
        reject(new Error('Download timeout'));
      });

      req.on('error', reject);
    });
  }

  /**
   * Resolve and stage logo
   */
  async resolveLogo(logoRef, type = 'empresa') {
    if (!logoRef) {
      this.warnings.push(`Missing ${type} logo`);
      return null;
    }

    // Check if URL
    if (logoRef.startsWith('http://') || logoRef.startsWith('https://')) {
      try {
        const filename = `${type}-${path.basename(new URL(logoRef).pathname)}`;
        const destPath = path.join(this.logosDir, filename);
        
        // Check if already downloaded
        try {
          await fs.access(destPath);
          return `assets/logos/${filename}`;
        } catch {
          // Download
          await this.downloadFile(logoRef, destPath);
          return `assets/logos/${filename}`;
        }
      } catch (err) {
        this.warnings.push(`Failed to download ${type} logo from ${logoRef}: ${err.message}`);
        return null;
      }
    }

    // Local file reference
    try {
      const sourcePath = path.resolve(logoRef);
      const filename = `${type}-${path.basename(sourcePath)}`;
      const destPath = path.join(this.logosDir, filename);
      
      await fs.copyFile(sourcePath, destPath);
      return `assets/logos/${filename}`;
    } catch (err) {
      this.warnings.push(`Failed to copy ${type} logo from ${logoRef}: ${err.message}`);
      return null;
    }
  }

  /**
   * Resolve and stage equipment image
   */
  async resolveEquipmentImage(imageRef) {
    if (!imageRef) {
      this.warnings.push('Missing equipment image reference');
      return 'assets/placeholders/placeholder-equipment.svg';
    }

    const filename = path.basename(imageRef);
    const destPath = path.join(this.equiposDir, filename);

    // Check if already in project assets
    try {
      await fs.access(destPath);
      return `assets/equipos/${filename}`;
    } catch {
      // Try to copy from catalog
      try {
        const catalogPath = path.resolve(imageRef);
        await fs.copyFile(catalogPath, destPath);
        return `assets/equipos/${filename}`;
      } catch (err) {
        this.warnings.push(`Failed to resolve equipment image ${imageRef}: ${err.message}`);
        return 'assets/placeholders/placeholder-equipment.svg';
      }
    }
  }

  /**
   * Stage all assets for a project
   */
  async stageAll(inputData, specData) {
    await this.init();

    const stagedAssets = {
      logo_empresa: null,
      logo_cliente: null,
      equipment: []
    };

    // Stage logos
    if (inputData.project) {
      stagedAssets.logo_empresa = await this.resolveLogo(
        inputData.project.logo_empresa,
        'empresa'
      );
      stagedAssets.logo_cliente = await this.resolveLogo(
        inputData.project.logo_cliente,
        'cliente'
      );
    }

    // Stage equipment images
    if (specData.equipment_specs) {
      for (const spec of specData.equipment_specs) {
        const equipmentAssets = {
          equipment_id: spec.equipment_id,
          selected: null,
          alternatives: []
        };

        // Selected model image
        if (spec.selected_model?.image_asset) {
          equipmentAssets.selected = await this.resolveEquipmentImage(
            spec.selected_model.image_asset
          );
        }

        // Alternative images
        if (spec.alternatives) {
          for (const alt of spec.alternatives) {
            if (alt.image_asset) {
              const altPath = await this.resolveEquipmentImage(alt.image_asset);
              equipmentAssets.alternatives.push({
                model: alt.model,
                path: altPath
              });
            }
          }
        }

        stagedAssets.equipment.push(equipmentAssets);
      }
    }

    return stagedAssets;
  }

  /**
   * Get warnings generated during staging
   */
  getWarnings() {
    return this.warnings;
  }
}

module.exports = { AssetManager };
