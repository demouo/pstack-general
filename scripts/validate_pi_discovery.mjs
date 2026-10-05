#!/usr/bin/env node
// Exercise an installed pi's native resource loader without explicit skill paths.
import fs from 'node:fs/promises';
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const [piDist, projectArg] = process.argv.slice(2);
if (!piDist || !projectArg) {
  console.error('Usage: node validate_pi_discovery.mjs <installed-pi-dist> <project>');
  process.exit(2);
}
const project = path.resolve(projectArg);
const skillsRoot = path.join(project, '.agents', 'skills');
const expected = [];
for (const entry of await fs.readdir(skillsRoot, { withFileTypes: true })) {
  if (!entry.isDirectory()) continue;
  try {
    await fs.access(path.join(skillsRoot, entry.name, 'SKILL.md'));
    expected.push(entry.name);
  } catch (error) {
    if (error.code !== 'ENOENT') throw error;
  }
}
if (!expected.length) throw new Error('No installed skills to verify');
const agentDir = await fs.mkdtemp(path.join(os.tmpdir(), 'pstack-pi-discovery-'));
try {
  const { DefaultResourceLoader } = await import(pathToFileURL(path.resolve(piDist, 'core/resource-loader.js')).href);
  const { SettingsManager } = await import(pathToFileURL(path.resolve(piDist, 'core/settings-manager.js')).href);
  const settingsManager = SettingsManager.inMemory();
  // This is a known test fixture. Trust stays in memory, never in user settings.
  settingsManager.setProjectTrusted(true);
  const loader = new DefaultResourceLoader({
    cwd: project, agentDir, settingsManager,
    noExtensions: true, noPromptTemplates: true, noThemes: true,
  });
  await loader.reload();
  const { skills, diagnostics } = loader.getSkills();
  const found = skills.filter(skill => path.resolve(skill.filePath).startsWith(skillsRoot + path.sep));
  const missing = expected.filter(name => !found.some(skill => skill.name === name));
  const localDiagnostics = diagnostics.filter(d => d.path && path.resolve(d.path).startsWith(skillsRoot + path.sep));
  console.log(JSON.stringify({ expected: expected.length, discovered: found.length, missing, diagnostics: localDiagnostics }, null, 2));
  if (missing.length || localDiagnostics.length) process.exitCode = 1;
} finally {
  await fs.rm(agentDir, { recursive: true, force: true });
}
