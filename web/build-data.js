/**
 * Generates web/data.js from repository files: skills, vendored skills, councils,
 * council session records, agents, lifecycle gates, contracts, quality rules,
 * the latest validation report and the changelog.
 * Every number and command the site shows comes from here (BL-002: no fake data).
 */
const fs = require('fs');
const path = require('path');
const { execFileSync } = require('child_process');

const root = path.resolve(__dirname, '..');
const readJson = (rel) => JSON.parse(fs.readFileSync(path.join(root, rel), 'utf8'));
const exists = (rel) => fs.existsSync(path.join(root, rel));

function git(args) {
  try {
    return execFileSync('git', args, { cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  } catch {
    return null;
  }
}

const pkg = readJson('package.json');
const repoUrl = (git(['remote', 'get-url', 'origin']) || '').replace(/\.git$/, '') || null;

// ---------------------------------------------------------------- skills
const skills = fs.readdirSync(path.join(root, 'skills'), { withFileTypes: true })
  .filter((d) => d.isDirectory() && exists(`skills/${d.name}/skill.json`))
  .map((d) => {
    const s = readJson(`skills/${d.name}/skill.json`);
    return {
      id: s.skillId,
      name: s.name,
      purpose: s.purpose,
      whenToUse: s.whenToUse || [],
      procedure: (s.procedure || []).map((p) => ({ title: p.title, action: p.action })),
      outputs: s.expectedOutputs || [],
      gates: s.applicableApprovalGates || [],
      verification: s.verificationCriteria || [],
      path: `skills/${d.name}/SKILL.md`,
      source: 'framework',
    };
  });

const vendorRegistry = exists('vendor/skills/registry.json') ? readJson('vendor/skills/registry.json') : { vendored: [], referenced: [] };
const vendored = vendorRegistry.vendored.map((v) => ({
  ...v,
  path: `vendor/skills/${v.id}/SKILL.md`,
  source: 'vendored',
}));

// Short, plain descriptions for the skills page, grouped by when people reach for them.
// Ids must exist in skills/ or vendor/skills/; the build fails loudly otherwise.
const SKILL_GROUPS = [
  {
    title: 'Getting started',
    sub: 'Point the framework at a project and let it route your requests.',
    skills: [
      ['orchestrator', 'Reads your request, checks the current gate and hands work to the right skill or council.'],
      ['project-discovery', 'Inspects the repo and environment and writes the G0 project contract.'],
      ['existing-project-analysis', 'Maps an existing codebase: structure, build, conventions and drift.'],
      ['cross-platform-adaptation', 'Translates skills and rules into Claude Code, Antigravity and other clients.'],
    ],
  },
  {
    title: 'The main flow',
    sub: 'From requirements to release, one gate at a time.',
    skills: [
      ['requirements-analysis', 'Turns a request into requirements, acceptance criteria and open questions.'],
      ['design-discovery', 'Captures flows, visual direction and constraints, or records why design is exempt.'],
      ['architecture-and-contracts', 'Sets boundaries, schemas, API contracts and decision records.'],
      ['phase-planning', 'Breaks the architecture into phases and tasks with clear file ownership.'],
      ['controlled-implementation', 'Builds one bounded task at a time, test-first, inside its files.'],
      ['testing-and-verification', 'Runs the checks and records real output as evidence.'],
      ['documentation-and-handoff', 'Writes the changelog, guides and release contract, and updates memory.'],
    ],
  },
  {
    title: 'Councils and decisions',
    sub: 'For choices that deserve more than one point of view.',
    skills: [
      ['council-review', 'Runs a four-round council: independent views, challenges, revisions, decision.'],
      ['business-case', 'Puts value, cost and risk side by side for a proposal.'],
      ['feature-prioritization', 'Scores features and draws a firm line around the first release.'],
      ['project-planning', 'Builds the work breakdown, critical path and dependencies.'],
    ],
  },
  {
    title: 'Design craft',
    sub: 'Tokens, layout, motion and accessibility for anything people see.',
    skills: [
      ['design-system-engineering', 'Turns design decisions into tokens, components and themes.'],
      ['baseline-ui', 'Checks spacing, tokens, contrast and motion against the baseline.'],
      ['ui-skills-routing', 'Picks the smallest set of UI skills a task needs.'],
      ['fixing-accessibility', 'Finds and fixes names, keyboard, focus and form problems.'],
      ['fixing-motion-performance', 'Finds animation that causes layout or paint work and fixes it.'],
      ['emil-design-eng', 'Decides whether and how something should animate, and polishes components.'],
      ['review-animations', 'Strict review of motion code against a written standard.'],
    ],
  },
  {
    title: 'Quality and recovery',
    sub: 'Review, tests and getting back on track.',
    skills: [
      ['independent-review', 'Reviews a change against its contract, the baseline rules and security policy.'],
      ['thermo-nuclear-review', 'Pushes for simpler code: less nesting, fewer wrappers, smaller files.'],
      ['test-case-generation', 'Writes positive, negative, boundary and regression cases traced to requirements.'],
      ['failure-recovery-and-improvement', 'Diagnoses a failed gate or broken test and rolls back or repairs.'],
    ],
  },
  {
    title: 'Reach and growth',
    sub: 'Help the right people find what you built.',
    skills: [
      ['seo-audit', 'Fixes titles, previews, structured data, sitemaps and repository metadata so search and social can find you.'],
      ['project-reach', 'Plans an honest launch: positioning, the right communities, launch posts and measuring what worked.'],
    ],
  },
];

const allSkillIds = new Set([...skills.map((s) => s.id), ...vendored.map((v) => v.id)]);
const grouped = new Set();
const skillGroups = SKILL_GROUPS.map((g, i) => ({
  n: String(i + 1).padStart(2, '0'),
  title: g.title,
  sub: g.sub,
  skills: g.skills.map(([id, desc]) => {
    if (!allSkillIds.has(id)) throw new Error(`build-data: skill group lists unknown skill '${id}'`);
    grouped.add(id);
    return { id, desc, vendored: vendored.some((v) => v.id === id) };
  }),
}));
const ungrouped = [...allSkillIds].filter((id) => !grouped.has(id));
if (ungrouped.length) throw new Error(`build-data: skills missing from SKILL_GROUPS: ${ungrouped.join(', ')}`);

// ---------------------------------------------------------------- agents
function findAgents(dir) {
  let list = [];
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (!entry.isDirectory()) continue;
    const full = path.join(dir, entry.name);
    const jsonPath = path.join(full, 'agent.json');
    if (fs.existsSync(jsonPath)) {
      const raw = JSON.parse(fs.readFileSync(jsonPath, 'utf8'));
      const rel = path.relative(path.join(root, 'agents'), full);
      list.push({
        id: raw.personaId || raw.roleId || rel,
        name: raw.title || raw.roleName || raw.name || rel,
        group: raw.group || (rel.includes('/') ? rel.split('/')[0] : 'lifecycle'),
        mission: raw.mission || raw.description || '',
        responsibilities: raw.responsibilities || [],
        whenToInvoke: raw.whenToInvoke || [],
        prohibitions: (raw.boundaries && raw.boundaries.prohibitions) || (Array.isArray(raw.boundaries) ? raw.boundaries : []),
        skills: raw.equippedSkills || raw.skills || [],
        path: `agents/${rel}/agent.json`,
      });
    }
    list = list.concat(findAgents(full));
  }
  return list;
}
const agents = findAgents(path.join(root, 'agents')).sort((a, b) => a.name.localeCompare(b.name));

// ---------------------------------------------------------------- councils
const councilConfig = readJson('core/council/councils.json');
const personaIndex = {};
function indexPersonas(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) indexPersonas(full);
    else if (entry.name.endsWith('.json')) {
      const p = JSON.parse(fs.readFileSync(full, 'utf8'));
      if (p.personaId) personaIndex[p.personaId] = { ...p, path: path.relative(root, full) };
    }
  }
}
indexPersonas(path.join(root, 'core', 'council', 'personas'));
for (const a of findAgents(path.join(root, 'agents'))) {
  if (!personaIndex[a.id]) {
    const raw = readJson(a.path);
    if (raw.personaId) personaIndex[a.id] = { ...raw, path: a.path };
  }
}

const councils = Object.entries(councilConfig.councils).map(([id, c]) => ({
  id,
  title: c.title,
  purpose: c.purpose,
  chair: c.chair,
  critic: c.critic,
  workOrder: c.workOrder || [],
  members: c.roster.map((pid) => {
    const p = personaIndex[pid];
    if (!p) throw new Error(`build-data: council '${id}' lists unknown persona '${pid}'`);
    return {
      id: pid,
      title: p.title,
      role: pid === c.chair ? 'chair' : pid === c.critic ? 'critic' : 'specialist',
      mission: p.mission,
      questions: (p.typicalQuestions || []).slice(0, 3),
      challengeFocus: (p.collaborationResponsibilities && p.collaborationResponsibilities.challengeFocus) || '',
      sources: (p.evidenceRequirements && p.evidenceRequirements.acceptableSources) || [],
      skills: (c.skills && c.skills[pid]) || [],
      path: p.path,
    };
  }),
}));

const briefsDir = path.join(root, 'memory', 'council-briefs');
const sessions = fs.existsSync(briefsDir)
  ? fs.readdirSync(briefsDir).filter((f) => f.endsWith('.json')).map((f) => {
    const r = JSON.parse(fs.readFileSync(path.join(briefsDir, f), 'utf8'));
    return { ...r, path: `memory/council-briefs/${f}` };
  }).sort((a, b) => String(b.createdAt).localeCompare(String(a.createdAt)))
  : [];

// ---------------------------------------------------------------- governance
const lifecycle = readJson('core/lifecycle/lifecycle-fsm.json');
const executionState = readJson('memory/execution-state.json');
const contracts = {};
for (const dir of fs.readdirSync(path.join(root, 'contracts'))) {
  const rel = `contracts/${dir}/contract.json`;
  if (exists(rel)) {
    const c = readJson(rel);
    contracts[c.lifecycleGate || dir] = {
      id: c.contractId, type: c.contractType, title: c.title, status: c.status, gate: c.lifecycleGate,
      updatedAt: c.updatedAt, approvedBy: c.approval && c.approval.approvedBy, approvedAt: c.approval && c.approval.approvedAt, path: rel,
    };
  }
}
const gates = lifecycle.gates.map((g) => ({
  id: g.gateId, name: g.name, description: g.description, exitCriteria: g.exitCriteria || [],
  allowedExemption: !!g.allowedExemption, contract: contracts[g.gateId] || null,
}));
const qualityRules = readJson('core/quality/profiles.json').mandatoryBaseline.rules;
const validation = exists('validation/reports/master_validation_report.json')
  ? (({ timestamp, totalRun, passed, failed, skipped, durationSeconds }) => ({ timestamp, totalRun, passed, failed, skipped, durationSeconds }))(readJson('validation/reports/master_validation_report.json'))
  : null;

// ---------------------------------------------------------------- changelog
const changelog = [];
const clText = exists('CHANGELOG.md') ? fs.readFileSync(path.join(root, 'CHANGELOG.md'), 'utf8') : '';
for (const block of clText.split(/^## /m).slice(1)) {
  const head = block.split('\n')[0].match(/^\[([^\]]+)\]\s*-\s*(\S+)/);
  if (!head) continue;
  const summary = (block.match(/^Summary:\s*(.+)$/m) || [])[1]
    || ((block.match(/^- \*\*([^*]+)\*\*/m) || [])[1] || '').replace(/\s*\(.*\)$/, '');
  changelog.push({ version: head[1], date: head[2], summary });
}

// ---------------------------------------------------------------- install
const mcpTools = (() => {
  const src = fs.readFileSync(path.join(root, 'adapters', 'mcp', 'README.md'), 'utf8');
  return (src.match(/^\| `[a-z_]+` ?\|/gm) || []).length;
})();
const cloneDir = 'project-intelligence';
const BUNDLES = require('./bundles');
const BUNDLE_TEXT = {
  framework: { desc: 'Skills, agents, councils, contracts, instructions, adapters and the installer.', cmd: `node ${cloneDir}/bin/cli.js init --dir .` },
  skills: { desc: `All ${skills.length} framework skills plus ${vendored.length} third-party skills, with their licenses.`, cmd: `cp -R ${cloneDir}/skills ${cloneDir}/vendor/skills .claude/` },
  councils: { desc: `${Object.keys(personaIndex).length} persona definitions, council rosters and the referee.`, cmd: `python3 -m core.council.referee list` },
  mcp: { desc: `${mcpTools} tools for gates, contracts, quality checks and memory, with no pip dependencies.`, cmd: `python3 ${cloneDir}/adapters/mcp/server.py --workspace-root .` },
};
const install = {
  repoUrl,
  clone: repoUrl ? `git clone ${repoUrl}.git` : null,
  init: `node ${cloneDir}/bin/cli.js init --dir .`,
  doctor: `node ${cloneDir}/bin/cli.js doctor`,
  clients: [
    { id: 'claude', label: 'Claude Code', how: 'Run in your project folder', code: `node ${cloneDir}/bin/cli.js init --client claude --dir .` },
    { id: 'antigravity', label: 'Antigravity', how: 'Run in your project folder', code: `node ${cloneDir}/bin/cli.js init --client antigravity --dir .` },
    { id: 'copilot', label: 'GitHub Copilot CLI', how: 'Add the MCP server, then ask Copilot to plan with plan_task', code: `copilot mcp add project-intelligence -- python3 /path/to/${cloneDir}/adapters/mcp/server.py --workspace-root .` },
    {
      id: 'mcp', label: 'Any MCP client', how: 'Add to your client’s MCP config',
      code: JSON.stringify({ mcpServers: { 'project-intelligence': { command: 'python3', args: [`/path/to/${cloneDir}/adapters/mcp/server.py`, '--workspace-root', '/path/to/your/project'] } } }, null, 2),
    },
  ],
  bundles: BUNDLES.map((b) => ({ ...b, desc: BUNDLE_TEXT[b.id].desc, cmd: BUNDLE_TEXT[b.id].cmd })),
  license: pkg.license,
  node: pkg.engines && pkg.engines.node,
};

// ---------------------------------------------------------------- orchestrator demo
// Plans come from running the real dispatcher; council turns come from recorded
// sessions; specialist replies describe changes that were actually made.
function plan(task) {
  try {
    const out = execFileSync(process.env.PYTHON || 'python3', ['-m', 'core.orchestrator.dispatch', task, '--json'],
      { cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'] });
    return JSON.parse(out);
  } catch (err) {
    throw new Error(`build-data: could not run the dispatcher for "${task}": ${err.message}`);
  }
}

function hexLum(hex) {
  const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
    .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
  return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
}
const ratio = (a, b) => {
  const [x, y] = [hexLum(a), hexLum(b)].sort((m, n) => n - m);
  return ((x + 0.05) / (y + 0.05)).toFixed(1);
};
const css = fs.readFileSync(path.join(__dirname, 'styles.css'), 'utf8');
const lightRoot = css.slice(css.indexOf(':root {'), css.indexOf('}', css.indexOf(':root {')));
const token = (name) => (lightRoot.match(new RegExp(`--${name}:\\s*(#[0-9a-f]{6})`, 'i')) || [])[1];
const g3 = lifecycle.gates.find((g) => g.gateId === 'G3');
const sessionById = Object.fromEntries(sessions.map((x) => [x.brief.decisionId, x]));
const demoSession = (id) => {
  if (!sessionById[id]) throw new Error(`build-data: demo needs the recorded session ${id}`);
  return sessionById[id];
};

const demo = [
  {
    id: 'question', label: 'Ask a question',
    turns: [
      { task: 'What does gate G3 check?', reply: { kind: 'answer', title: `${g3.gateId} · ${g3.name}`, lines: [g3.description, ...g3.exitCriteria.map((c) => `Exit check: ${c}`)] } },
    ],
  },
  {
    id: 'fix', label: 'Fix one thing',
    turns: [
      {
        task: 'Fix the contrast on the primary button',
        reply: {
          kind: 'specialist',
          lines: [
            `White text on the old hover color (${token('color-accent-600')}) measures ${ratio('#ffffff', token('color-accent-600'))}:1, below the 4.5:1 minimum.`,
            `Hover now uses --btn-bg-hover (${token('btn-bg-hover')}): ${ratio('#ffffff', token('btn-bg-hover'))}:1.`,
            'A contrast test now fails the build if any text token drops below 4.5:1 (validation/universal-tests/test_site.py).',
          ],
        },
      },
    ],
  },
  {
    id: 'design', label: 'Design council',
    turns: [
      { task: demoSession('dec-website-revamp-slate').task, sessionId: 'dec-website-revamp-slate' },
      {
        task: 'Make the site work in dark mode too',
        reply: {
          kind: 'specialist',
          lines: [
            'Added a dark palette built from the same OKLCH ramps, reversed so tints stay dark and text stays light.',
            'The site follows your system setting; the header button overrides it and remembers your choice.',
            'Buttons keep their own fill tokens so white text passes 4.5:1 in both themes, and the contrast test checks both.',
          ],
        },
      },
    ],
  },
  {
    id: 'dev', label: 'Development council',
    turns: [{ task: demoSession('dec-orchestrator-council-integration').task, sessionId: 'dec-orchestrator-council-integration' }],
  },
  {
    id: 'feature', label: 'New feature',
    turns: [{ task: 'Add a new feature: team workspaces with permissions, pricing and a new dashboard', reply: { kind: 'pipeline' } }],
  },
].map((sc) => ({
  ...sc,
  turns: sc.turns.map((t) => {
    const p = plan(t.task);
    const reply = t.reply && t.reply.kind === 'specialist' ? { ...t.reply, title: p.specialist.title } : t.reply;
    return { ...t, reply, plan: p };
  }),
}));

const entryPoints = [
  { id: 'claude', label: 'Claude Code', how: 'Slash command installed by init', example: '/orchestrator Redesign the settings page', setup: `node ${'project-intelligence'}/bin/cli.js init --client claude --dir .` },
  { id: 'copilot', label: 'GitHub Copilot CLI', how: 'MCP tool plan_task', example: 'Plan this with project-intelligence: redesign the settings page', setup: 'copilot mcp add project-intelligence -- python3 /path/to/project-intelligence/adapters/mcp/server.py --workspace-root .' },
  { id: 'antigravity', label: 'Antigravity', how: 'Orchestrator skill installed by init', example: 'Use the orchestrator skill to redesign the settings page', setup: `node project-intelligence/bin/cli.js init --client antigravity --dir .` },
  { id: 'terminal', label: 'Any terminal', how: 'CLI command', example: 'node project-intelligence/bin/cli.js ask "Redesign the settings page"', setup: 'git clone the repository, then run the command from anywhere' },
];

const data = {
  meta: {
    name: 'Project Intelligence',
    version: pkg.version,
    license: pkg.license,
    commit: git(['rev-parse', '--short', 'HEAD']),
    generatedAt: new Date().toISOString(),
  },
  counts: {
    skills: skills.length,
    vendoredSkills: vendored.length,
    agents: agents.length,
    personas: Object.keys(personaIndex).length,
    councils: councils.length,
    mcpTools,
  },
  skills,
  vendored,
  referencedSkills: vendorRegistry.referenced,
  skillGroups,
  agents,
  councils,
  councilLimits: councilConfig.limits,
  tiers: councilConfig.tiers,
  sessions,
  gates,
  currentGate: executionState.currentGate,
  qualityRules,
  validation,
  changelog,
  install,
  demo,
  entryPoints,
};

const out = `/* Generated by web/build-data.js from repository files. Do not edit by hand. */\nwindow.PROJECT_DATA = ${JSON.stringify(data, null, 2)};\n`;
fs.writeFileSync(path.join(__dirname, 'data.js'), out, 'utf8');
console.log(`web/data.js written: ${skills.length} skills, ${vendored.length} vendored, ${agents.length} agents, ${Object.keys(personaIndex).length} personas, ${sessions.length} council sessions (${out.length} bytes)`);
