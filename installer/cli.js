/**
 * Project Intelligence — CLI Controller & Portable Installer
 * Implements: init, doctor, update, uninstall
 * Conformance: Zero external npm dependencies.
 */

const fs = require('fs');
const path = require('path');
const {
  detectProjectRoot,
  detectNode,
  detectPython,
  detectGit,
  detectClientConfigs,
} = require('./detector');
const {
  loadManifest,
  saveManifest,
  revertInstallation,
} = require('./manifest');
const { installAntigravity } = require('./adapters/antigravity');
const { installClaude } = require('./adapters/claude');

const PACKAGE_ROOT = path.resolve(__dirname, '..');
const pkg = require(path.join(PACKAGE_ROOT, 'package.json'));
const { spawnSync } = require('child_process');
const { cliInvocation } = require('./invocation');

function parseArgs(args) {
  const parsed = {
    command: null,
    client: 'all',
    mcp: true,
    force: false,
    dryRun: false,
    yes: false,
    dir: null,
    help: false,
    version: false,
    json: false,
    rest: [],
    task: '',
  };

  for (let i = 0; i < args.length; i++) {
    const arg = args[i];
    if (!parsed.command && ['init', 'doctor', 'update', 'uninstall', 'ask', 'council', 'mcp'].includes(arg)) {
      parsed.command = arg;
    } else if (arg === '--json') {
      parsed.json = true;
    } else if (parsed.command === 'council' || parsed.command === 'mcp') {
      parsed.rest.push(arg); // passed through to the Python tool, flags included
    } else if (parsed.command === 'ask' && (arg === '--council' || arg === '--persona' || arg === '--include')) {
      parsed.rest.push(arg, args[++i] || '');
    } else if (parsed.command === 'ask' && arg === '--full-roster') {
      parsed.rest.push(arg);
    } else if (parsed.command === 'ask' && !arg.startsWith('--')) {
      parsed.task = (parsed.task ? parsed.task + ' ' : '') + arg;
    } else if (arg === '--client') {
      parsed.client = args[++i] || 'all';
    } else if (arg.startsWith('--client=')) {
      parsed.client = arg.split('=')[1] || 'all';
    } else if (arg === '--mcp') {
      const next = args[i + 1];
      if (next === 'true' || next === 'false') {
        parsed.mcp = next === 'true';
        i++;
      } else {
        parsed.mcp = true;
      }
    } else if (arg.startsWith('--mcp=')) {
      parsed.mcp = arg.split('=')[1] !== 'false';
    } else if (arg === '--no-mcp') {
      parsed.mcp = false;
    } else if (arg === '--force' || arg === '-f') {
      parsed.force = true;
    } else if (arg === '--dry-run') {
      parsed.dryRun = true;
    } else if (arg === '--yes' || arg === '-y') {
      parsed.yes = true;
    } else if (arg === '--dir') {
      parsed.dir = args[++i];
    } else if (arg.startsWith('--dir=')) {
      parsed.dir = arg.split('=')[1];
    } else if (arg === '--help' || arg === '-h' || arg === 'help') {
      parsed.help = true;
    } else if (arg === '--version' || arg === '-v') {
      parsed.version = true;
    }
  }

  return parsed;
}

function printHelp() {
  console.log(`
Project Intelligence — Portable Installer & Platform Adapter CLI

Usage:
  node <path-to-project-intelligence>/bin/cli.js <command> [options]

  Not published to npm: the npm package named "project-intelligence" belongs to
  an unrelated project, so do not run it through npx.

Commands:
  init          Initialize Project Intelligence in the current or target directory
  doctor        Verify runtime environment, dependencies, and manifest integrity
  update        Update framework skills and rules while preserving user contracts
  uninstall     Cleanly remove created files and revert merged standing rules
  ask "<task>"  Plan a request: which tier, skills, agents or councils handle it (add --json for JSON)
  council <plan|prompt|record|list|check> ...
                Run the council referee (see core/council/referee.py)
  mcp           Start the MCP server on stdio (for Copilot CLI and other MCP clients)

Options:
  --client <antigravity|claude|all>   Target AI coding assistant platform (default: all)
  --mcp <true|false>                  Enable/disable Model Context Protocol adapter (default: true)
  --dir <path>                        Specify target project directory (default: CWD/Git Root)
  --force                             Force re-initialization
  --dry-run                           Simulate execution without modifying files
  --yes, -y                           Skip confirmation prompts
  --help, -h                          Show this help message
  --version, -v                       Show version
`);
}

async function handleInit(options, targetDir) {
  const { client, mcp, force, dryRun } = options;
  console.log('========================================================================');
  console.log('PROJECT INTELLIGENCE — INITIALIZING PLATFORM ADAPTERS');
  console.log(`Target Directory : ${targetDir}`);
  console.log(`Target Platform  : ${client}`);
  console.log(`MCP Adapter      : ${mcp ? 'ENABLED' : 'DISABLED'}`);
  console.log(`Execution Mode   : ${dryRun ? 'DRY RUN (preview only)' : 'STANDARD'}`);
  console.log('========================================================================');

  const existingManifest = loadManifest(targetDir);
  if (existingManifest && !force) {
    console.log('[NOTE] Existing installation manifest detected. Performing idempotent synchronization.');
  }

  const allCreatedFiles = new Set(existingManifest ? existingManifest.createdFiles : []);
  const allCreatedDirs = new Set(existingManifest ? existingManifest.createdDirectories : []);
  const modifiedMap = new Map();

  if (existingManifest && Array.isArray(existingManifest.modifiedFiles)) {
    for (const mod of existingManifest.modifiedFiles) {
      modifiedMap.set(mod.path, mod);
    }
  }

  const context = { packageRoot: PACKAGE_ROOT };

  // 1. Antigravity Adapter
  if (client === 'antigravity' || client === 'all') {
    console.log('\n[Antigravity] Installing Google Antigravity platform adapter...');
    const agRes = installAntigravity(targetDir, options, context);
    agRes.createdFiles.forEach((f) => allCreatedFiles.add(f));
    agRes.createdDirectories.forEach((d) => allCreatedDirs.add(d));
    agRes.modifiedFiles.forEach((m) => {
      if (!modifiedMap.has(m.path)) {
        modifiedMap.set(m.path, m);
      }
    });
    console.log(`  • Installed canonical skills & orchestrator to .agents/skills/`);
    console.log(`  • Injected standing rules to GEMINI.md and .agents/rules/AGENTS.md`);
    if (mcp) {
      console.log(`  • Merged .agents/mcp_config.json`);
    }
  }

  // 2. Claude Code Adapter
  if (client === 'claude' || client === 'all') {
    console.log('\n[Claude Code] Installing Anthropic Claude Code platform adapter...');
    const clRes = installClaude(targetDir, options, context);
    clRes.createdFiles.forEach((f) => allCreatedFiles.add(f));
    clRes.createdDirectories.forEach((d) => allCreatedDirs.add(d));
    clRes.modifiedFiles.forEach((m) => {
      if (!modifiedMap.has(m.path)) {
        modifiedMap.set(m.path, m);
      }
    });
    console.log(`  • Installed slash command /orchestrator to .claude/commands/`);
    console.log(`  • Installed canonical skills to .claude/skills/`);
    console.log(`  • Injected standing rules to CLAUDE.md`);
    console.log(`  • Configured hooks in .claude/settings.json and .claude/hooks/`);
    if (mcp) {
      console.log(`  • Merged .claude/mcp.json`);
    }
  }

  // 3. Save Manifest
  if (!dryRun) {
    const manifestData = {
      name: 'project-intelligence',
      version: pkg.version,
      installedAt: (existingManifest && existingManifest.installedAt) || new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      client,
      mcpEnabled: Boolean(mcp),
      createdFiles: Array.from(allCreatedFiles),
      createdDirectories: Array.from(allCreatedDirs),
      modifiedFiles: Array.from(modifiedMap.values()),
    };
    saveManifest(targetDir, manifestData);
    console.log('\n[Manifest] Saved installation record to .project-intelligence/install-manifest.json');
  }

  console.log('\n========================================================================');
  console.log('INITIALIZATION COMPLETE');
  console.log('You can now interact with your AI assistant using Project Intelligence.');
  console.log(`Run \`${cliInvocation(PACKAGE_ROOT)} doctor\` anytime to check system health.`);
  console.log('========================================================================\n');
  return 0;
}

async function handleDoctor(options, targetDir) {
  console.log('========================================================================');
  console.log('PROJECT INTELLIGENCE — SYSTEM & RUNTIME DIAGNOSTIC DOCTOR');
  console.log(`Target Directory: ${targetDir}`);
  console.log('========================================================================\n');

  let overallPass = true;

  // 1. Node.js Check
  const node = detectNode();
  if (node.compatible) {
    console.log(`[PASS] Node.js Runtime: v${node.version} (>= 18 required)`);
  } else {
    console.error(`[FAIL] Node.js Runtime: v${node.version} is incompatible. Node >= 18.0.0 is required.`);
    overallPass = false;
  }

  // 2. Python Check
  const py = detectPython();
  if (py.available && py.compatible) {
    console.log(`[PASS] Python Runtime : ${py.bin} ${py.version} (>= 3.10 required)`);
  } else if (py.available) {
    console.error(`[FAIL] Python Runtime : ${py.bin} ${py.version} is incompatible. Python >= 3.10 is required.`);
    overallPass = false;
  } else {
    console.error('[FAIL] Python Runtime : Python 3.10+ was not found on PATH.');
    overallPass = false;
  }

  // 3. Git Repository Check
  const git = detectGit(targetDir);
  if (git.available && git.isRepo) {
    console.log(`[PASS] Git Repository : ${git.version} (Root: ${git.root})`);
  } else if (git.available) {
    console.log(`[WARN] Git Repository : Git is available (${git.version}), but '${targetDir}' is not inside a git repository.`);
  } else {
    console.log('[WARN] Git Repository : git executable was not found on PATH.');
  }

  // 4. Client Configurations
  const configs = detectClientConfigs(targetDir);
  console.log('\nClient Configuration Status:');
  console.log(`  • Claude Code (CLAUDE.md)         : ${configs.claude.hasClaudeMd ? 'FOUND' : 'NOT FOUND'}`);
  console.log(`  • Claude Settings (.claude)       : ${configs.claude.hasSettings ? 'FOUND' : 'NOT FOUND'}`);
  console.log(`  • Antigravity (GEMINI.md)         : ${configs.antigravity.hasGeminiMd ? 'FOUND' : 'NOT FOUND'}`);
  console.log(`  • Antigravity Rules (.agents)     : ${configs.antigravity.hasAgentsRules ? 'FOUND' : 'NOT FOUND'}`);

  // 5. Manifest Integrity
  console.log('\nManifest Integrity Check:');
  if (configs.manifest.exists) {
    const manifest = loadManifest(targetDir);
    if (!manifest) {
      console.error('  [FAIL] .project-intelligence/install-manifest.json is corrupt or unparseable.');
      overallPass = false;
    } else {
      let missingCount = 0;
      if (Array.isArray(manifest.createdFiles)) {
        for (const file of manifest.createdFiles) {
          if (!fs.existsSync(path.resolve(targetDir, file))) {
            missingCount++;
          }
        }
      }
      if (missingCount === 0) {
        console.log(`  [PASS] Install manifest valid (Version: ${manifest.version}, Files verified: ${manifest.createdFiles?.length || 0})`);
      } else {
        console.log(`  [WARN] Install manifest found, but ${missingCount} created files are missing from disk.`);
      }
    }
  } else {
    console.log('  [INFO] Project Intelligence manifest not found. Run `init` to install.');
  }

  console.log('\n========================================================================');
  console.log(`DOCTOR STATUS: ${overallPass ? 'HEALTHY / PASS' : 'ISSUES DETECTED / FAIL'}`);
  console.log('========================================================================\n');

  return overallPass ? 0 : 1;
}

async function handleUpdate(options, targetDir) {
  console.log('========================================================================');
  console.log('PROJECT INTELLIGENCE — UPDATING FRAMEWORK SKILLS & ENGINES');
  console.log(`Target Directory: ${targetDir}`);
  console.log('========================================================================');

  const manifest = loadManifest(targetDir);
  const client = manifest ? manifest.client : options.client || 'all';
  const mcp = manifest ? manifest.mcpEnabled : options.mcp;

  console.log(`Target client from configuration: ${client}`);
  console.log('Preserving all user contracts (contracts/) and durable memory (memory/)...');

  // Re-run init with force to update skills and engine rules non-destructively
  const initOpts = {
    ...options,
    client,
    mcp,
    force: true,
  };

  await handleInit(initOpts, targetDir);

  console.log('[OK] Framework skills, commands, and standing rules successfully updated.');
  return 0;
}

async function handleUninstall(options, targetDir) {
  const { dryRun } = options;
  console.log('========================================================================');
  console.log('PROJECT INTELLIGENCE — UNINSTALLING PLATFORM ADAPTERS');
  console.log(`Target Directory: ${targetDir}`);
  console.log(`Execution Mode  : ${dryRun ? 'DRY RUN (preview only)' : 'STANDARD'}`);
  console.log('========================================================================\n');

  const result = revertInstallation(targetDir, dryRun);
  if (!result.success) {
    console.log(`[NOTE] ${result.message}`);
    return 0;
  }

  if (result.revertedFiles.length > 0) {
    console.log('Reverted Standing Rules / Merged Configurations:');
    result.revertedFiles.forEach((f) => console.log(`  • ${f}`));
  }

  if (result.removedFiles.length > 0) {
    console.log('Removed Created Files:');
    result.removedFiles.forEach((f) => console.log(`  • ${f}`));
  }

  if (result.removedDirectories.length > 0) {
    console.log('Removed Created Directories:');
    result.removedDirectories.forEach((d) => console.log(`  • ${d}`));
  }

  console.log('\n[OK] Project Intelligence platform adapters cleanly uninstalled.');
  return 0;
}

/**
 * Runs a framework Python module from the package root, streaming its output.
 * Python 3.10+ with no third-party packages is the only requirement.
 */
function runPython(args) {
  const python = process.env.PYTHON || 'python3';
  // Run in the user's folder (council records and the lifecycle gate live there) and
  // import the framework from the package root.
  const env = { ...process.env, PYTHONPATH: [PACKAGE_ROOT, process.env.PYTHONPATH].filter(Boolean).join(path.delimiter) };
  const res = spawnSync(python, args, { cwd: process.cwd(), env, stdio: 'inherit' });
  if (res.error) {
    console.error(`[Project Intelligence] Could not run ${python}: ${res.error.message}. Install Python 3.10 or later, or set PYTHON.`);
    return 1;
  }
  return res.status === null ? 1 : res.status;
}

function handleAsk(options, targetDir) {
  const task = (options.task || '').trim();
  if (!task) {
    console.error('Usage: project-intelligence ask "<what you want done>" [--json]');
    return 2;
  }
  const args = ['-m', 'core.orchestrator.dispatch', task, '--workspace', targetDir, ...options.rest];
  if (options.json) args.push('--json');
  return runPython(args);
}

async function main(args = process.argv.slice(2)) {
  const options = parseArgs(args);

  if (options.version) {
    console.log(`project-intelligence version ${pkg.version}`);
    return 0;
  }

  if (options.help || !options.command) {
    printHelp();
    return 0;
  }

  const targetDir = options.dir ? path.resolve(options.dir) : detectProjectRoot(process.cwd());

  switch (options.command) {
    case 'init':
      return await handleInit(options, targetDir);
    case 'doctor':
      return await handleDoctor(options, targetDir);
    case 'update':
      return await handleUpdate(options, targetDir);
    case 'uninstall':
      return await handleUninstall(options, targetDir);
    case 'ask':
      return handleAsk(options, targetDir);
    case 'council':
      return runPython(['-m', 'core.council.referee', ...options.rest]);
    case 'mcp':
      // stdio MCP server for Copilot CLI, Cursor and other clients; stdout carries JSON-RPC only.
      return runPython([path.join(PACKAGE_ROOT, 'adapters', 'mcp', 'server.py')]);
    default:
      console.error(`Unknown command: ${options.command}`);
      printHelp();
      return 1;
  }
}

module.exports = {
  main,
  parseArgs,
  handleInit,
  handleDoctor,
  handleUpdate,
  handleUninstall,
  handleAsk,
};
