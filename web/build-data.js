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
      ['legacy-codebase-knowledge-base', 'Reverse-engineers legacy code with lightweight sub-agents to extract domain entities, conventions, logging patterns and docs.'],
      ['web-scraping-and-research', 'Scrapes official documentation, package registries and web intelligence into clean markdown and structured data.'],
      ['cross-platform-adaptation', 'Translates skills and rules into Claude Code, Antigravity and other clients.'],
    ],
  },
  {
    title: 'From idea to plan',
    sub: 'Get the idea, the words and the code to agree before anyone builds.',
    skills: [
      ['idea-to-prd', 'Questions the idea, agrees the vocabulary, writes the PRD with the real CLI commands and slices it into tickets.'],
      ['grilling', 'Interviews you in rounds, each question with a recommended answer, until nothing is assumed.'],
      ['domain-modeling', 'Keeps a glossary and decision records so specs and code use the same words.'],
    ],
  },
  {
    title: 'The main flow',
    sub: 'From requirements to release, one gate at a time.',
    skills: [
      ['requirements-analysis', 'Turns a request into requirements, acceptance criteria and open questions.'],
      ['design-discovery', 'Captures flows, visual direction and constraints, or records why design is exempt.'],
      ['architecture-and-contracts', 'Sets boundaries, schemas, API contracts and decision records.'],
      ['api-contract-and-openapi-spec', 'Authors OpenAPI 3.1 contracts, detects breaking changes and generates mock fixtures and client SDK stubs.'],
      ['database-migration-and-schema-evolution', 'Designs zero-downtime database migrations, backward-compatible schemas and reversible rollback scripts.'],
      ['phase-planning', 'Breaks the architecture into phases and tasks with clear file ownership.'],
      ['controlled-implementation', 'Builds one bounded task at a time, test-first, inside its files.'],
      ['testing-and-verification', 'Runs the checks and records real output as evidence.'],
      ['ci-cd-pipeline-engineering', 'Authors secure CI/CD workflows, package caching, rootless multi-stage Docker builds and automated releases.'],
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
      ['open-design-system-and-prototyping', 'Authors DESIGN.md brand contracts, builds interactive HTML prototypes and dashboards, and refactors codebases to brand tokens.'],
      ['baseline-ui', 'Checks spacing, tokens, contrast and motion against the baseline.'],
      ['ui-skills-routing', 'Picks the smallest set of UI skills a task needs.'],
      ['fixing-accessibility', 'Finds and fixes names, keyboard, focus and form problems.'],
      ['fixing-motion-performance', 'Finds animation that causes layout or paint work and fixes it.'],
      ['emil-design-eng', 'Decides whether and how something should animate, and polishes components.'],
      ['review-animations', 'Strict review of motion code against a written standard.'],
    ],
  },
  {
    title: 'Coding craft',
    sub: 'Write less code, test the risky parts and review like the person on call.',
    skills: [
      ['ponytail', 'Finds the smallest change that fully solves the task, and finishes every caller it breaks.'],
      ['tdd', 'Red, green, refactor at the highest useful seam; test behaviour, not internals.'],
      ['safe-refactoring-and-migration', 'Modernizes legacy code incrementally behind typed seams using characterization tests and codemods.'],
      ['ponytail-review', 'Reviews a change: every finding has a concrete failing case and the smallest fix.'],
      ['ponytail-audit', 'Audits a whole repository for bugs, risk, missing tests and code to delete.'],
    ],
  },
  {
    title: 'Quality and recovery',
    sub: 'Review, tests and getting back on track.',
    skills: [
      ['independent-review', 'Reviews a change against its contract, the baseline rules and security policy.'],
      ['security-audit-and-hardening', 'Audits repositories for secret leaks, dependency CVEs, injection vectors and insecure headers.'],
      ['thermo-nuclear-review', 'Pushes for simpler code: less nesting, fewer wrappers, smaller files.'],
      ['test-case-generation', 'Writes positive, negative, boundary and regression cases traced to requirements.'],
      ['runtime-performance-profiling', 'Profiles CPU flamegraphs, eliminates N+1 database queries, plugs memory leaks and trims frontend bundles.'],
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
// Runs from npm with npx (the spec lives in installer/invocation.js).
const RUN = `npx -y ${require('../installer/invocation').RUN_SPEC}`;
const BUNDLES = require('./bundles');
const BUNDLE_TEXT = {
  framework: { desc: 'Skills, agents, councils, contracts, instructions, adapters and the installer.', cmd: `${RUN} init` },
  skills: { desc: `All ${skills.length} framework skills plus ${vendored.length} third-party skills, with their licenses.`, cmd: `cp -R ${cloneDir}/skills ${cloneDir}/vendor/skills .claude/` },
  councils: { desc: `${Object.keys(personaIndex).length} persona definitions, council rosters and the referee.`, cmd: `${RUN} council list` },
  mcp: { desc: `${mcpTools} tools for gates, contracts, quality checks and memory, with no pip dependencies.`, cmd: `${RUN} mcp` },
};
const install = {
  repoUrl,
  run: RUN,
  clone: repoUrl ? `git clone ${repoUrl}.git` : null,
  plugin: {
    add: 'claude plugin marketplace add sahasbelbase/project-intelligence',
    install: 'claude plugin install project-intelligence@sahasbelbase',
    use: '/project-intelligence:ask <what you want done>',
  },
  init: `${RUN} init`,
  doctor: `${RUN} doctor`,
  clients: [
    { id: 'claude', label: 'Claude Code', how: 'Install the plugin, then use /project-intelligence:ask', code: 'claude plugin marketplace add sahasbelbase/project-intelligence\nclaude plugin install project-intelligence@sahasbelbase' },
    { id: 'copilot', label: 'GitHub Copilot CLI', how: 'Add the MCP server, then ask Copilot to plan with plan_task', code: `copilot mcp add project-intelligence -- ${RUN} mcp` },
    { id: 'antigravity', label: 'Antigravity', how: 'Run in your project folder', code: `${RUN} init --client antigravity` },
    {
      id: 'mcp', label: 'Any MCP client', how: 'Add to your client’s MCP config',
      code: JSON.stringify({ mcpServers: { 'project-intelligence': { command: 'npx', args: ['-y', require('../installer/invocation').RUN_SPEC, 'mcp'] } } }, null, 2),
    },
  ],
  bundles: BUNDLES.map((b) => ({ ...b, desc: BUNDLE_TEXT[b.id].desc, cmd: BUNDLE_TEXT[b.id].cmd })),
  license: pkg.license,
  node: pkg.engines && pkg.engines.node,
};

// ---------------------------------------------------------------- orchestrator demo
// Plans come from running the real dispatcher; council turns come from recorded
// sessions; specialist replies describe changes that were actually made.
function plan(task, council, include = []) {
  try {
    const args = ['-m', 'core.orchestrator.dispatch', task, '--json', ...(council ? ['--council', council] : []),
      ...include.flatMap((p) => ['--include', p])];
    const out = execFileSync(process.env.PYTHON || 'python3', args,
      { cwd: root, encoding: 'utf8', stdio: ['ignore', 'pipe', 'pipe'], env: { ...process.env, PI_CLI: 'project-intelligence' } });
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
      {
        task: demoSession('dec-website-revamp-slate').task, sessionId: 'dec-website-revamp-slate',
        council: 'design', include: ['information-architect', 'accessibility-specialist', 'color-harmony-specialist'],
      },
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
    turns: [{
      task: demoSession('dec-orchestrator-council-integration').task, sessionId: 'dec-orchestrator-council-integration',
      council: 'development', include: ['api-integration-specialist', 'developer-experience-specialist', 'security-engineer'],
    }],
  },
  {
    id: 'independent', label: 'Independent agents',
    turns: [{
      task: demoSession('dec-routing-keywords-vs-model').task, sessionId: 'dec-routing-keywords-vs-model',
      council: 'development', include: ['test-quality-engineer', 'developer-experience-specialist'],
    }],
  },
  {
    id: 'feature', label: 'New feature',
    turns: [{ task: 'Add a new feature: team workspaces with permissions, pricing and a new dashboard', reply: { kind: 'pipeline' } }],
  },
].map((sc) => ({
  ...sc,
  turns: sc.turns.map((t) => {
    const p = plan(t.task, t.council, t.include);
    const reply = t.reply && t.reply.kind === 'specialist' ? { ...t.reply, title: p.specialist.title } : t.reply;
    return { ...t, reply, plan: p };
  }),
}));

const entryPoints = [
  { id: 'claude', label: 'Claude Code', how: 'Plugin skill', example: '/project-intelligence:ask Redesign the settings page', setup: `${install.plugin.add}\n${install.plugin.install}` },
  { id: 'copilot', label: 'GitHub Copilot CLI', how: 'MCP tool plan_task', example: 'Plan this with project-intelligence: redesign the settings page', setup: `copilot mcp add project-intelligence -- ${RUN} mcp` },
  { id: 'antigravity', label: 'Antigravity', how: 'Orchestrator skill installed by init', example: 'Use the orchestrator skill to redesign the settings page', setup: `${RUN} init --client antigravity` },
  { id: 'terminal', label: 'Any terminal', how: 'CLI command', example: `${RUN} ask "Redesign the settings page"`, setup: 'Nothing to install: npx fetches it on first run. Needs Node 18+ and Python 3.10+.' },
];

// ---------------------------------------------------------------- advisor retrieval index (BM25)
const ADVISOR_STOP_WORDS = new Set([
  'a','about','above','after','again','against','all','am','an','and','any','are','as','at',
  'be','because','been','before','being','below','between','both','but','by','can','could',
  'did','do','does','doing','down','during','each','few','for','from','further','had','has',
  'have','having','he','her','here','hers','herself','him','himself','his','how','i','if',
  'in','into','is','it','its','itself','just','me','more','most','my','myself','no','nor',
  'not','of','off','on','once','only','or','other','our','ours','ourselves','out','over',
  'own','same','should','so','some','such','than','that','the','their','theirs','them',
  'themselves','then','there','these','they','this','those','through','to','too','under',
  'until','up','very','was','we','were','what','when','where','which','while','who','whom',
  'why','with','would','you','your','yours','yourself','yourselves'
]);

function tokenizeAdvisorText(text) {
  if (!text) return [];
  return String(text)
    .toLowerCase()
    .replace(/[^a-z0-9_\-\s]/g, ' ')
    .split(/\s+/)
    .filter((t) => t.length > 1 && !ADVISOR_STOP_WORDS.has(t));
}

function buildAdvisorIndex() {
  const docs = [];

  // 1. Framework skills
  skills.forEach((s) => {
    const tf = {};
    const addWeighted = (tokens, weight) => {
      for (const t of tokens) {
        tf[t] = Math.round(((tf[t] || 0) + weight) * 10) / 10;
      }
    };
    addWeighted(tokenizeAdvisorText(`${s.id} ${s.name}`), 5.0);
    addWeighted(tokenizeAdvisorText((s.whenToUse || []).join(' ')), 3.5);
    addWeighted(tokenizeAdvisorText(s.purpose || ''), 2.5);
    addWeighted(tokenizeAdvisorText((s.procedure || []).map((p) => `${p.title} ${p.action}`).join(' ')), 1.5);
    addWeighted(tokenizeAdvisorText((s.outputs || []).join(' ')), 1.5);

    let docLen = 0;
    for (const k in tf) docLen += tf[k];

    docs.push({
      id: s.id,
      kind: 'skill',
      name: s.name,
      summary: s.purpose,
      gates: s.gates || [],
      command: `/${s.id}`,
      whenToUse: (s.whenToUse || []).slice(0, 3),
      tf,
      docLen: Math.round(docLen * 10) / 10,
    });
  });

  // 2. Vendored skills
  vendored.forEach((v) => {
    const tf = {};
    const addWeighted = (tokens, weight) => {
      for (const t of tokens) {
        tf[t] = Math.round(((tf[t] || 0) + weight) * 10) / 10;
      }
    };
    addWeighted(tokenizeAdvisorText(`${v.id} ${v.name}`), 5.0);
    addWeighted(tokenizeAdvisorText(v.summary || ''), 3.0);
    addWeighted(tokenizeAdvisorText((v.usedBy || []).join(' ')), 2.0);

    let docLen = 0;
    for (const k in tf) docLen += tf[k];

    docs.push({
      id: v.id,
      kind: 'vendored-skill',
      name: v.name,
      summary: v.summary,
      gates: [],
      command: `/${v.id}`,
      whenToUse: [v.summary],
      tf,
      docLen: Math.round(docLen * 10) / 10,
    });
  });

  // 3. Specialist agents
  agents.forEach((a) => {
    const tf = {};
    const addWeighted = (tokens, weight) => {
      for (const t of tokens) {
        tf[t] = Math.round(((tf[t] || 0) + weight) * 10) / 10;
      }
    };
    addWeighted(tokenizeAdvisorText(`${a.id} ${a.name}`), 4.5);
    addWeighted(tokenizeAdvisorText(a.mission || ''), 3.0);
    addWeighted(tokenizeAdvisorText(a.role || ''), 2.5);

    let docLen = 0;
    for (const k in tf) docLen += tf[k];

    docs.push({
      id: a.id,
      kind: 'agent',
      name: a.name,
      summary: a.mission,
      gates: [],
      command: `agent:${a.id}`,
      whenToUse: [a.mission],
      tf,
      docLen: Math.round(docLen * 10) / 10,
    });
  });

  // 4. Councils
  councils.forEach((c) => {
    const tf = {};
    const addWeighted = (tokens, weight) => {
      for (const t of tokens) {
        tf[t] = Math.round(((tf[t] || 0) + weight) * 10) / 10;
      }
    };
    addWeighted(tokenizeAdvisorText(`${c.id} ${c.title}`), 4.0);
    addWeighted(tokenizeAdvisorText(c.purpose || ''), 3.0);
    addWeighted(tokenizeAdvisorText((c.members || []).map((m) => `${m.title} ${m.mission}`).join(' ')), 2.0);

    let docLen = 0;
    for (const k in tf) docLen += tf[k];

    docs.push({
      id: c.id,
      kind: 'council',
      name: c.title,
      summary: c.purpose,
      gates: [],
      command: `council:${c.id}`,
      whenToUse: [c.purpose],
      tf,
      docLen: Math.round(docLen * 10) / 10,
    });
  });

  // 5. Lifecycle gates
  gates.forEach((g) => {
    const tf = {};
    const addWeighted = (tokens, weight) => {
      for (const t of tokens) {
        tf[t] = Math.round(((tf[t] || 0) + weight) * 10) / 10;
      }
    };
    addWeighted(tokenizeAdvisorText(`${g.id} ${g.name}`), 4.0);
    addWeighted(tokenizeAdvisorText(g.description || ''), 3.0);

    let docLen = 0;
    for (const k in tf) docLen += tf[k];

    docs.push({
      id: g.id,
      kind: 'gate',
      name: `${g.id}: ${g.name}`,
      summary: g.description,
      gates: [g.id],
      command: `gate:${g.id}`,
      whenToUse: [g.description],
      tf,
      docLen: Math.round(docLen * 10) / 10,
    });
  });

  // 6. Installation & Setup capability
  const setupTf = {};
  const addSetup = (tokens, weight) => {
    for (const t of tokens) {
      setupTf[t] = Math.round(((setupTf[t] || 0) + weight) * 10) / 10;
    }
  };
  addSetup(tokenizeAdvisorText('setup install installation initialize configure start getting started doctor'), 5.0);
  addSetup(tokenizeAdvisorText('how to install how to setup cli claude code copilot antigravity mcp'), 3.5);
  addSetup(tokenizeAdvisorText('Install skills, councils, and lifecycle gates into Claude Code, GitHub Copilot CLI, Google Antigravity, or any MCP client.'), 2.5);
  let setupDocLen = 0;
  for (const k in setupTf) setupDocLen += setupTf[k];
  docs.push({
    id: 'setup',
    kind: 'skill',
    name: 'Framework Installation & Setup',
    summary: 'Install Project Intelligence into Claude Code, GitHub Copilot CLI, Google Antigravity, or any MCP client with zero pip dependencies.',
    gates: ['G0'],
    command: 'npx -y @sahasbelbase/project-intelligence init',
    whenToUse: [
      'Setting up Project Intelligence in a new or existing repository',
      'Configuring Claude Code, GitHub Copilot CLI, or Antigravity agents',
      'Running doctor diagnostic checks to verify client environment health'
    ],
    tf: setupTf,
    docLen: Math.round(setupDocLen * 10) / 10,
  });

  // 7. Lead Orchestrator capability
  const orchTf = {};
  const addOrch = (tokens, weight) => {
    for (const t of tokens) {
      orchTf[t] = Math.round(((orchTf[t] || 0) + weight) * 10) / 10;
    }
  };
  addOrch(tokenizeAdvisorText('orchestrator orchestrate dispatch plan router referee tier council'), 5.0);
  addOrch(tokenizeAdvisorText('general task planning route plain words request question'), 3.0);
  addOrch(tokenizeAdvisorText('Lead Project Orchestrator plans every request, assigns tiers, and verifies gates.'), 2.0);
  let orchDocLen = 0;
  for (const k in orchTf) orchDocLen += orchTf[k];
  docs.push({
    id: 'orchestrator',
    kind: 'skill',
    name: 'Lead Project Orchestrator',
    summary: 'Plan requests, enforce lifecycle gate contracts, and dispatch to specialist agents or convene councils.',
    gates: ['G0', 'G1', 'G2', 'G3', 'G4', 'G5', 'G6'],
    command: '/orchestrator',
    whenToUse: [
      'Dispatching requests across answer, specialist, and council tiers',
      'Checking and enforcing lifecycle gate contracts before proceeding',
      'Coordinating multi-persona council deliberations with recorded dissent'
    ],
    tf: orchTf,
    docLen: Math.round(orchDocLen * 10) / 10,
  });

  // Compute DF across all docs
  const df = {};
  for (const doc of docs) {
    for (const term in doc.tf) {
      df[term] = (df[term] || 0) + 1;
    }
  }

  const totalLen = docs.reduce((acc, d) => acc + d.docLen, 0);
  const avgDocLen = Math.round((totalLen / (docs.length || 1)) * 10) / 10;

  return {
    docs,
    df,
    avgDocLen,
    totalDocs: docs.length,
  };
}

const advisorIndex = buildAdvisorIndex();

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
  advisorIndex,
};

const out = `/* Generated by web/build-data.js from repository files. Do not edit by hand. */\nwindow.PROJECT_DATA = ${JSON.stringify(data, null, 2)};\n`;
fs.writeFileSync(path.join(__dirname, 'data.js'), out, 'utf8');
console.log(`web/data.js written: ${skills.length} skills, ${vendored.length} vendored, ${agents.length} agents, ${Object.keys(personaIndex).length} personas, ${sessions.length} council sessions, ${advisorIndex.totalDocs} indexed advisor documents (${out.length} bytes)`);
