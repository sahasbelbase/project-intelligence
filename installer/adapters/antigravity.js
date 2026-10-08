/**
 * Project Intelligence — Google Antigravity Platform Adapter Installer
 * Installs canonical skills, orchestrator skill, injects GEMINI.md/AGENTS.md rules,
 * and configures .agents/mcp_config.json.
 * Conformance: Zero external npm dependencies.
 */

const fs = require('fs');
const path = require('path');
const { injectMarkerBlock } = require('../manifest');

/**
 * Routing instructions shared by the installed orchestrator skill and the Claude Code
 * /orchestrator command. cliPath is the absolute path to this package's bin/cli.js,
 * so installed projects call the framework they were installed from.
 */
function routingSection(cliPath) {
  const cli = `node ${JSON.stringify(cliPath)}`;
  return `## Handling a request
1. **Plan it first.** Run \`${cli} ask "<request>"\` (or call the MCP tool \`plan_task\`). It returns a tier and who handles the work.
2. **Tier 0, answer:** answer directly from the framework files.
3. **Tier 1, specialist:** act as the named specialist and apply its listed skills.
4. **Tier 2 or 3, council:** for each convened persona, get its instructions with \`${cli} council prompt <council> <persona> <round> "<request>"\` and write that persona's response.
   - Round 1 is blinded: each persona writes without seeing the others.
   - Round 2: each persona raises at most two challenges; the critic raises at least one.
   - Round 3: every challenged persona answers each challenge and may revise.
   - Round 4: the chair writes the decision. Keep unresolved disagreement as dissent.
   - Show the user a short summary of each round as you go.
5. **Record it.** Save the rounds as JSON and run \`${cli} council record <file.json>\`; it validates the session and writes \`memory/council-briefs/\`. Then run \`${cli} council check\`.
6. **Improve on request.** When the user asks for a change to a decision or result, plan the follow-up the same way; small fixes usually route to one specialist.
`;
}

function buildOrchestratorSkillMd(cliPath) {
  return `---
name: orchestrator
description: Lead Project Orchestrator. Plans every request (answer, specialist or council), governs lifecycle gates G0 through G6, validates contracts and enforces anti-slop rules.
triggers:
  - "orchestrator"
  - "project intelligence"
  - "council"
  - "govern gates"
  - "lifecycle status"
  - "next action"
---

# Lead Project Orchestrator

## Overview
Plans every request, convenes councils when a decision needs several perspectives, and governs the canonical project lifecycle across Gates G0 through G6.

${routingSection(cliPath)}
## Core Responsibilities
1. **Deterministic Gate Transitions**: Progression between lifecycle gates (G0–G6) strictly follows \`core/lifecycle/lifecycle-fsm.json\`.
2. **Mandatory Human-in-the-Loop Sign-Off**: The orchestrator never bypasses required human approvals.
3. **Evidence-Based Quality**: Verify exit code 0 and actual logs before declaring completion.
4. **Collision-Free Subagents**: Assign disjoint, non-overlapping file ownership boundaries.
5. **No invented opinions**: Council content comes from the personas' prompts and the user's context; never fabricate sources, quotes or numbers.

## Gate Mapping
- G0: Discovery (\`contracts/project/contract.json\`)
- G1: Requirements (\`contracts/requirements/contract.json\`)
- G2: Design (\`contracts/design/contract.json\`)
- G3: Architecture (\`contracts/architecture/contract.json\`)
- G4: Implementation (\`contracts/implementation/contract.json\`)
- G5: Verification & Review (\`contracts/quality/contract.json\`)
- G6: Release & Handoff (\`contracts/release/contract.json\`)
`;
}

const ORCHESTRATOR_SKILL_MD = buildOrchestratorSkillMd(path.resolve(__dirname, '..', '..', 'bin', 'cli.js'));

const REQUIREMENTS_SKILL_MD = `---
name: requirements-analysis
description: Analyze project charter, extract functional and non-functional requirements, formulate acceptance criteria, and author Gate G1 Requirements Contract.
triggers:
  - "requirements"
  - "user stories"
  - "acceptance criteria"
  - "gate G1"
---

# Requirements Analysis & Specification

## Overview
Analyzes requirements for Gate G1 of the Project Intelligence lifecycle, creating structured functional and non-functional criteria with verifiable acceptance tests.

## Key Activities
1. Extract user personas, functional workflows, and non-functional constraints.
2. Formulate testable Given/When/Then acceptance criteria.
3. Author and validate \`contracts/requirements/contract.json\`.
4. Secure human sign-off for Gate G1 to G2 transition.
`;

function installAntigravity(targetDir, options, context) {
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

  function writeFile(relPath, content) {
    const fullPath = path.resolve(targetDir, relPath);
    ensureDir(path.dirname(relPath));
    const existed = fs.existsSync(fullPath);
    if (!existed) {
      results.createdFiles.push(relPath);
    }
    if (!dryRun) {
      fs.writeFileSync(fullPath, content, 'utf8');
    }
  }

  // 1. Setup Skills Directories
  ensureDir('.agents');
  ensureDir('.agents/skills');

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
          writeFile(`.agents/skills/${skillName}/SKILL.md`, content);
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
        writeFile(`.agents/skills/${entry.name}/${file.name}`, content);
      }
    }
  }

  // Install orchestrator and requirements-analysis skills
  writeFile('.agents/skills/orchestrator/SKILL.md', buildOrchestratorSkillMd(path.join(packageRoot, 'bin', 'cli.js')));
  writeFile('.agents/skills/requirements-analysis/SKILL.md', REQUIREMENTS_SKILL_MD);

  // 2. Standing Rules for GEMINI.md and .agents/rules/AGENTS.md
  ensureDir('.agents/rules');
  const templatePath = path.join(packageRoot, 'adapters', 'antigravity', 'templates', 'GEMINI.md.template');
  let standingRulesTemplate = '';
  if (fs.existsSync(templatePath)) {
    standingRulesTemplate = fs.readFileSync(templatePath, 'utf8');
  } else {
    standingRulesTemplate = `# Project Intelligence — Google Antigravity Rules\n\n- Project: {{PROJECT_NAME}}\n- Gate: {{ACTIVE_GATE}}`;
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
    .trim();

  // Helper for injecting standing rules into a markdown file
  function injectRules(relPath) {
    const fullPath = path.resolve(targetDir, relPath);
    const existed = fs.existsSync(fullPath);
    let original = '';
    if (existed) {
      original = fs.readFileSync(fullPath, 'utf8');
    }
    const modified = injectMarkerBlock(original, renderedBlock);

    results.modifiedFiles.push({
      path: relPath,
      existedBefore: existed,
      backupContent: existed ? original : null,
    });

    if (!dryRun) {
      ensureDir(path.dirname(relPath));
      fs.writeFileSync(fullPath, modified, 'utf8');
    }
  }

  injectRules('GEMINI.md');
  injectRules('.agents/rules/AGENTS.md');

  // 3. MCP Configuration (.agents/mcp_config.json)
  if (mcp !== false && mcp !== 'false') {
    const mcpRelPath = '.agents/mcp_config.json';
    const mcpFullPath = path.resolve(targetDir, mcpRelPath);
    const existed = fs.existsSync(mcpFullPath);
    let original = null;
    let mcpConfig = {};

    if (existed) {
      try {
        original = fs.readFileSync(mcpFullPath, 'utf8');
        mcpConfig = JSON.parse(original);
      } catch {
        mcpConfig = {};
      }
    }

    results.modifiedFiles.push({
      path: mcpRelPath,
      existedBefore: existed,
      backupContent: original,
    });

    let serverScriptPath = 'adapters/mcp/server.py';
    if (path.resolve(targetDir) !== path.resolve(packageRoot)) {
      serverScriptPath = path.join(packageRoot, 'adapters', 'mcp', 'server.py');
    }

    mcpConfig.mcpServers = mcpConfig.mcpServers || {};
    mcpConfig.mcpServers['project-intelligence'] = {
      command: 'python3',
      args: [serverScriptPath],
      env: {
        PYTHONUNBUFFERED: '1',
      },
    };

    if (!dryRun) {
      fs.writeFileSync(mcpFullPath, JSON.stringify(mcpConfig, null, 2) + '\n', 'utf8');
    }
  }

  return results;
}

module.exports = {
  installAntigravity,
  ORCHESTRATOR_SKILL_MD,
  buildOrchestratorSkillMd,
  routingSection,
  REQUIREMENTS_SKILL_MD,
};
