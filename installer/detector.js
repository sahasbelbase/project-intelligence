/**
 * Project Intelligence — Environment & Runtime Detector
 * Detects project root, Python 3.10+, Node.js, and Git availability.
 * Conformance: Zero external npm dependencies.
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

function detectProjectRoot(cwd = process.cwd()) {
  try {
    const gitRoot = execSync('git rev-parse --show-toplevel', {
      cwd,
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'ignore'],
    }).trim();
    if (gitRoot && fs.existsSync(gitRoot)) {
      return path.resolve(gitRoot);
    }
  } catch {
    // Not a git repo or git not found
  }
  return path.resolve(cwd);
}

function detectNode() {
  const version = process.version; // e.g. "v20.10.0"
  const cleanVersion = version.replace(/^v/, '');
  const [major, minor, patch] = cleanVersion.split('.').map((n) => parseInt(n, 10));
  const compatible = major >= 18;

  return {
    version: cleanVersion,
    major,
    minor,
    patch,
    compatible,
    raw: version,
  };
}

function detectPython() {
  const candidates = [
    process.env.PYTHON,
    'python3',
    'python',
    '/usr/local/bin/python3',
    '/opt/homebrew/bin/python3',
    '/Library/Frameworks/Python.framework/Versions/3.14/bin/python3',
    '/usr/bin/python3',
  ].filter(Boolean);

  for (const bin of candidates) {
    try {
      const output = execSync(
        `"${bin}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"`,
        {
          encoding: 'utf8',
          stdio: ['pipe', 'pipe', 'ignore'],
        }
      ).trim();

      const [major, minor, patch] = output.split('.').map((n) => parseInt(n, 10));
      const compatible = major === 3 && minor >= 10;

      if (compatible) {
        return {
          available: true,
          bin,
          version: output,
          major,
          minor,
          patch,
          compatible: true,
        };
      }
    } catch {
      // Try next binary
    }
  }

  return {
    available: false,
    bin: null,
    version: null,
    major: 0,
    minor: 0,
    patch: 0,
    compatible: false,
  };
}

function detectGit(cwd = process.cwd()) {
  try {
    const gitVersionOutput = execSync('git --version', {
      encoding: 'utf8',
      stdio: ['pipe', 'pipe', 'ignore'],
    }).trim();

    let isRepo = false;
    let gitRoot = null;
    try {
      const repoCheck = execSync('git rev-parse --is-inside-work-tree', {
        cwd,
        encoding: 'utf8',
        stdio: ['pipe', 'pipe', 'ignore'],
      }).trim();
      isRepo = repoCheck === 'true';
      if (isRepo) {
        gitRoot = execSync('git rev-parse --show-toplevel', {
          cwd,
          encoding: 'utf8',
          stdio: ['pipe', 'pipe', 'ignore'],
        }).trim();
      }
    } catch {
      isRepo = false;
    }

    return {
      available: true,
      version: gitVersionOutput,
      isRepo,
      root: gitRoot,
    };
  } catch {
    return {
      available: false,
      version: null,
      isRepo: false,
      root: null,
    };
  }
}

function detectClientConfigs(targetDir = process.cwd()) {
  const claudeMdPath = path.join(targetDir, 'CLAUDE.md');
  const claudeSettingsPath = path.join(targetDir, '.claude', 'settings.json');
  const claudeMcpPath = path.join(targetDir, '.claude', 'mcp.json');
  const claudeOrchestratorPath = path.join(targetDir, '.claude', 'commands', 'orchestrator.md');

  const geminiMdPath = path.join(targetDir, 'GEMINI.md');
  const agentsRulesPath = path.join(targetDir, '.agents', 'rules', 'AGENTS.md');
  const agentsMcpPath = path.join(targetDir, '.agents', 'mcp_config.json');
  const agentsOrchestratorPath = path.join(targetDir, '.agents', 'skills', 'orchestrator', 'SKILL.md');

  const manifestPath = path.join(targetDir, '.project-intelligence', 'install-manifest.json');

  return {
    claude: {
      hasClaudeMd: fs.existsSync(claudeMdPath),
      hasSettings: fs.existsSync(claudeSettingsPath),
      hasMcp: fs.existsSync(claudeMcpPath),
      hasOrchestratorCommand: fs.existsSync(claudeOrchestratorPath),
    },
    antigravity: {
      hasGeminiMd: fs.existsSync(geminiMdPath),
      hasAgentsRules: fs.existsSync(agentsRulesPath),
      hasMcp: fs.existsSync(agentsMcpPath),
      hasOrchestratorSkill: fs.existsSync(agentsOrchestratorPath),
    },
    manifest: {
      exists: fs.existsSync(manifestPath),
      path: manifestPath,
    },
  };
}

module.exports = {
  detectProjectRoot,
  detectNode,
  detectPython,
  detectGit,
  detectClientConfigs,
};
