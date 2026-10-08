/**
 * Project Intelligence — Anthropic Claude Code Platform Adapter Installer
 * Installs orchestrator commands, canonical skills, hooks, standing CLAUDE.md rules,
 * and configures .claude/settings.json and .claude/mcp.json.
 * Conformance: Zero external npm dependencies.
 */

const fs = require('fs');
const path = require('path');
const { cliInvocation, mcpServerEntry } = require('../invocation');
const { COUNCIL_MEMBER_MD } = require('../council-member-agent');
const { injectMarkerBlock } = require('../manifest');
const { ORCHESTRATOR_SKILL_MD, REQUIREMENTS_SKILL_MD, buildOrchestratorSkillMd, routingSection } = require('./antigravity');

function buildClaudeOrchestratorCommand(cli) {
  return `---
description: Plan and run a request through Project Intelligence - answer, specialist or council.
argument-hint: <what you want done>
---

You are the Project Intelligence Lead Orchestrator. The request is:

$ARGUMENTS

${routingSection(cli)}
Before changing files, check the lifecycle gate with the MCP tool \`project_status\` (or \`memory/execution-state.json\`) and follow the anti-slop rules: no emojis in code, real tests, verbatim execution evidence.
`;
}

const CLAUDE_COMMAND_ORCHESTRATOR_MD = buildClaudeOrchestratorCommand(cliInvocation(path.resolve(__dirname, '..', '..')));

function installClaude(targetDir, options, context) {
  const { dryRun = false, mcp = true } = options;
  const { packageRoot } = context;

  const results = {
    createdFiles: [],
    createdDirectories: [],
    modifiedFiles: [],
  };

  function ensureDir(relDir) {
    const fullDir = path.resolve(targetDir, relDir);
    if (!fs.existsSync(fullDir)) {
      if (!dryRun) {
        fs.mkdirSync(fullDir, { recursive: true });
      }
      results.createdDirectories.push(relDir);
    }
  }

  function writeFile(relPath, content, mode = null) {
    const fullPath = path.resolve(targetDir, relPath);
    ensureDir(path.dirname(relPath));
    const existed = fs.existsSync(fullPath);
    if (!existed) {
      results.createdFiles.push(relPath);
    }
    if (!dryRun) {
      fs.writeFileSync(fullPath, content, { encoding: 'utf8', mode: mode || 0o644 });
      if (mode) {
        try {
          fs.chmodSync(fullPath, mode);
        } catch {
          // ignore chmod failure on restricted filesystems
        }
      }
    }
  }

  // 1. Setup Claude Directories
  ensureDir('.claude');
  ensureDir('.claude/commands');
  ensureDir('.claude/skills');
  ensureDir('.claude/hooks');

  // Install slash command /orchestrator
  writeFile('.claude/agents/council-member.md', COUNCIL_MEMBER_MD);
  writeFile('.claude/commands/orchestrator.md', buildClaudeOrchestratorCommand(cliInvocation(packageRoot)));

  // Copy canonical skills from packageRoot/skills
  const canonicalSkillsDir = path.join(packageRoot, 'skills');
  if (fs.existsSync(canonicalSkillsDir)) {
    const skillEntries = fs.readdirSync(canonicalSkillsDir, { withFileTypes: true });
    for (const entry of skillEntries) {
      if (entry.isDirectory()) {
        const skillName = entry.name;
        const skillSrc = path.join(canonicalSkillsDir, skillName, 'SKILL.md');
        if (fs.existsSync(skillSrc)) {
          const content = fs.readFileSync(skillSrc, 'utf8');
          writeFile(`.claude/skills/${skillName}/SKILL.md`, content);
        }
      }
    }
  }

  // Copy vendored third-party skills (every file, including the upstream LICENSE)
  const vendoredSkillsDir = path.join(packageRoot, 'vendor', 'skills');
  if (fs.existsSync(vendoredSkillsDir)) {
    const vendorEntries = fs.readdirSync(vendoredSkillsDir, { withFileTypes: true });
    for (const entry of vendorEntries) {
      if (!entry.isDirectory()) continue;
      const skillDir = path.join(vendoredSkillsDir, entry.name);
      if (!fs.existsSync(path.join(skillDir, 'SKILL.md'))) continue;
      for (const file of fs.readdirSync(skillDir, { withFileTypes: true })) {
        if (!file.isFile()) continue;
        const content = fs.readFileSync(path.join(skillDir, file.name), 'utf8');
        writeFile(`.claude/skills/${entry.name}/${file.name}`, content);
      }
    }
  }

  // Install orchestrator and requirements-analysis skills
  writeFile('.claude/skills/orchestrator/SKILL.md', buildOrchestratorSkillMd(cliInvocation(packageRoot)));
  writeFile('.claude/skills/requirements-analysis/SKILL.md', REQUIREMENTS_SKILL_MD);

  // 2. Install Hooks
  const hooksSrcDir = path.join(packageRoot, 'adapters', 'claude-code', 'hooks');
  const sessionStartSrc = path.join(hooksSrcDir, 'session-start.sh');
  const preToolUseSrc = path.join(hooksSrcDir, 'pre-tool-use.sh');

  if (fs.existsSync(sessionStartSrc)) {
    writeFile('.claude/hooks/session-start.sh', fs.readFileSync(sessionStartSrc, 'utf8'), 0o755);
  }
  if (fs.existsSync(preToolUseSrc)) {
    writeFile('.claude/hooks/pre-tool-use.sh', fs.readFileSync(preToolUseSrc, 'utf8'), 0o755);
  }

  // 3. Configure .claude/settings.json
  const settingsRelPath = '.claude/settings.json';
  const settingsFullPath = path.resolve(targetDir, settingsRelPath);
  const settingsExisted = fs.existsSync(settingsFullPath);
  let originalSettings = null;
  let settingsData = {};

  if (settingsExisted) {
    try {
      originalSettings = fs.readFileSync(settingsFullPath, 'utf8');
      settingsData = JSON.parse(originalSettings);
    } catch {
      settingsData = {};
    }
  }

  results.modifiedFiles.push({
    path: settingsRelPath,
    existedBefore: settingsExisted,
    backupContent: originalSettings,
  });

  settingsData.hooks = settingsData.hooks || {};

  // Helper to ensure hook entry doesn't duplicate
  function addHook(category, hookDef) {
    settingsData.hooks[category] = settingsData.hooks[category] || [];
    const exists = settingsData.hooks[category].some(
      (h) => h.command === hookDef.command || (h.matcher && h.matcher === hookDef.matcher && h.command === hookDef.command)
    );
    if (!exists) {
      settingsData.hooks[category].push(hookDef);
    }
  }

  addHook('SessionStart', {
    command: 'bash .claude/hooks/session-start.sh',
    description: 'Validates git working tree status, reconciles memory state, and displays active lifecycle gate.',
  });

  addHook('PreToolUse', {
    matcher: 'Bash',
    command: 'bash .claude/hooks/pre-tool-use.sh',
    description: 'Intercepts bash commands to block prohibited operations (force push, arbitrary deletes) and enforce exit code 2 denial.',
  });

  addHook('Stop', {
    command: "python3 -c 'print(\"[Claude Hook] Session ended. Verify git status and pending contract transitions.\")'",
    description: 'Notifies user of session termination and reminds them of uncommitted state.',
  });

  if (!dryRun) {
    fs.writeFileSync(settingsFullPath, JSON.stringify(settingsData, null, 2) + '\n', 'utf8');
  }

  // 4. Injects Standing Rules into CLAUDE.md
  const templatePath = path.join(packageRoot, 'adapters', 'claude-code', 'templates', 'CLAUDE.md.template');
  let standingRulesTemplate = '';
  if (fs.existsSync(templatePath)) {
    standingRulesTemplate = fs.readFileSync(templatePath, 'utf8');
  } else {
    standingRulesTemplate = `# Project Intelligence — Claude Code Instructions\n\n- Project: {{PROJECT_NAME}}\n- Gate: {{ACTIVE_GATE}}`;
  }

  const projectName = path.basename(targetDir);
  const renderedBlock = standingRulesTemplate
    .replace(/<!-- BEGIN PROJECT-INTELLIGENCE -->/g, '')
    .replace(/<!-- END PROJECT-INTELLIGENCE -->/g, '')
    .replace(/{{PROJECT_NAME}}/g, projectName)
    .replace(/{{PROJECT_MISSION}}/g, 'Deterministic engineering and lifecycle governance')
    .replace(/{{ACTIVE_GATE}}/g, 'G0')
    .replace(/{{GATE_NAME}}/g, 'Discovery')
    .replace(/{{ACTIVE_CONTRACT_PATH}}/g, 'contracts/project/contract.json')
    .replace(/{{ACTIVE_PROFILE}}/g, 'MANDATORY_BASELINE')
    .replace(/{{ALLOWED_COMMAND_PREFIXES}}/g, 'git, python, pytest, npm, node')
    .replace(/{{ALLOWED_MUTABLE_PATHS}}/g, '- `contracts/`\n- `memory/`\n- `skills/`')
    .trim();

  const claudeMdRelPath = 'CLAUDE.md';
  const claudeMdFullPath = path.resolve(targetDir, claudeMdRelPath);
  const claudeMdExisted = fs.existsSync(claudeMdFullPath);
  let originalClaudeMd = '';
  if (claudeMdExisted) {
    originalClaudeMd = fs.readFileSync(claudeMdFullPath, 'utf8');
  }
  const modifiedClaudeMd = injectMarkerBlock(originalClaudeMd, renderedBlock);

  results.modifiedFiles.push({
    path: claudeMdRelPath,
    existedBefore: claudeMdExisted,
    backupContent: claudeMdExisted ? originalClaudeMd : null,
  });

  if (!dryRun) {
    fs.writeFileSync(claudeMdFullPath, modifiedClaudeMd, 'utf8');
  }

  // 5. Deep-merges .claude/mcp.json if MCP is enabled
  if (mcp !== false && mcp !== 'false') {
    const mcpRelPath = '.claude/mcp.json';
    const mcpFullPath = path.resolve(targetDir, mcpRelPath);
    const mcpExisted = fs.existsSync(mcpFullPath);
    let originalMcp = null;
    let mcpConfig = {};

    if (mcpExisted) {
      try {
        originalMcp = fs.readFileSync(mcpFullPath, 'utf8');
        mcpConfig = JSON.parse(originalMcp);
      } catch {
        mcpConfig = {};
      }
    }

    results.modifiedFiles.push({
      path: mcpRelPath,
      existedBefore: mcpExisted,
      backupContent: originalMcp,
    });

    mcpConfig.mcpServers = mcpConfig.mcpServers || {};
    mcpConfig.mcpServers['project-intelligence'] = mcpServerEntry(packageRoot, targetDir);

    if (!dryRun) {
      fs.writeFileSync(mcpFullPath, JSON.stringify(mcpConfig, null, 2) + '\n', 'utf8');
    }
  }

  return results;
}

module.exports = {
  installClaude,
  CLAUDE_COMMAND_ORCHESTRATOR_MD,
  buildClaudeOrchestratorCommand,
};
