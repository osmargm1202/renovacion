#!/usr/bin/env node
/**
 * Memory Engine Runner
 * CLI tool to generate memoria.html for projects
 */

const { generateMemoria } = require('./index');
const path = require('path');

async function main() {
  const args = process.argv.slice(2);
  
  if (args.length === 0) {
    console.log('Usage: node runner.js <project-id> [project-path]');
    console.log('');
    console.log('Examples:');
    console.log('  node runner.js 1');
    console.log('  node runner.js 1 /custom/path/to/proyectos/1');
    process.exit(1);
  }

  const projectId = args[0];
  const projectPath = args[1] || path.join(process.cwd(), `proyectos/${projectId}`);

  console.log('Memory Engine Runner');
  console.log('====================');
  console.log(`Project ID: ${projectId}`);
  console.log(`Project Path: ${projectPath}`);
  console.log('');

  console.log('Generating memoria.html...');
  const startTime = Date.now();

  const result = await generateMemoria(projectId, projectPath);

  const elapsed = ((Date.now() - startTime) / 1000).toFixed(2);

  if (result.status === 'completed') {
    console.log(`✅ Success! (${elapsed}s)`);
    console.log(`Output: ${result.output_path}`);
    
    if (result.warnings && result.warnings.length > 0) {
      console.log('');
      console.log('⚠️  Warnings:');
      result.warnings.forEach(w => console.log(`  - ${w}`));
    }
  } else {
    console.log(`❌ Failed! (${elapsed}s)`);
    console.log(`Error: ${result.error}`);
    if (result.stack) {
      console.log('');
      console.log('Stack trace:');
      console.log(result.stack);
    }
    process.exit(1);
  }
}

main().catch(err => {
  console.error('Fatal error:', err);
  process.exit(1);
});
