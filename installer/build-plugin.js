#!/usr/bin/env node
/**
 * Generates the Claude Code plugin files from the same sources the installer uses,
 * so the plugin and `init` never drift apart:
 *
 *   .claude-plugin/plugin.json       plugin manifest (version from package.json)
 *   .claude-plugin/marketplace.json  makes this repository a plugin marketplace
 *   plugin-skills/ask/SKILL.md       /project-intelligence:ask <request>
 *
 * The repository root is the plugin root. Skills load from skills/ and vendor/skills/,
 * and the MCP server runs from adapters/mcp/server.py. Run `npm run build:plugin`
 * after changing the orchestrator instructions or the package version.
 */
const fs = require('fs');
const path = require('path');
const { routingSection } = require('./adapters/antigravity');

const root = path.resolve(__dirname, '..');
const pkg = JSON.parse(fs.readFileSync(path.join(root, 'package.json'), 'utf8'));

const PLUGIN_NAME = 'project-intelligence';
const MARKETPLACE_NAME = 'sahasbelbase';
const AUTHOR = { name: 'Sahas Belbase', url: 'https://github.com/sahasbelbase' };
// Resolved by Claude Code when it loads the command, so the plugin calls its own copy.
const CLI = 'node "${CLAUDE_PLUGIN_ROOT}/bin/cli.js"';

const askCommand = `---
name: ask
description: Plan and run a request through Project Intelligence - answer it, hand it to a specialist, or convene a design, development or product council. Use for any broad or multi-step project request.
argument-hint: <what you want done>
---

You are the Project Intelligence Lead Orchestrator. The request is:

$ARGUMENTS

${routingSection(CLI)}
Council sessions and the lifecycle gate belong to the user's project: run the commands above from the project folder. Follow the anti-slop rules: no emojis in code, real tests, verbatim execution evidence.
`;

const countSkills = (rel) => fs.readdirSync(path.join(root, rel), { withFileTypes: true })
  .filter((d) => d.isDirectory() && fs.existsSync(path.join(root, rel, d.name, 'SKILL.md'))).length;
const skillCount = countSkills('skills') + countSkills('vendor/skills');
const personaCount = (() => {
  const councils = JSON.parse(fs.readFileSync(path.join(root, 'core', 'council', 'councils.json'), 'utf8')).councils;
  return Object.values(councils).reduce((n, c) => n + c.roster.length, 0);
})();

const manifest = {
  name: PLUGIN_NAME,
  displayName: 'Project Intelligence',
  version: pkg.version,
  description: `Plans every request: answers it, hands it to a specialist, or convenes a design, development or product council. Ships ${skillCount} skills, ${personaCount} council personas, lifecycle gates and an MCP server.`,
  author: AUTHOR,
  homepage: pkg.homepage,
  repository: 'https://github.com/sahasbelbase/project-intelligence',
  license: pkg.license,
  keywords: ['orchestrator', 'council', 'skills', 'lifecycle', 'code-quality', 'seo', 'mcp'],
  skills: ['./vendor/skills/', './plugin-skills/'],
  // The repository's agents/ folder holds persona definitions for the referee, not
  // Claude Code subagents, so the default agents/ scan is turned off.
  agents: [],
  mcpServers: {
    'project-intelligence': {
      command: 'python3',
      args: ['${CLAUDE_PLUGIN_ROOT}/adapters/mcp/server.py'],
      env: { PYTHONUNBUFFERED: '1' },
    },
  },
};

const marketplace = {
  name: MARKETPLACE_NAME,
  owner: AUTHOR,
  description: 'Plugins by Sahas Belbase',
  plugins: [
    {
      name: PLUGIN_NAME,
      source: './',
      description: manifest.description,
    },
  ],
};

function write(rel, content) {
  const full = path.join(root, rel);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  fs.writeFileSync(full, content, 'utf8');
  return rel;
}

if (require.main === module) {
  const written = [
    write('.claude-plugin/plugin.json', JSON.stringify(manifest, null, 2) + '\n'),
    write('.claude-plugin/marketplace.json', JSON.stringify(marketplace, null, 2) + '\n'),
    write('plugin-skills/ask/SKILL.md', askCommand),
  ];
  console.log(`Wrote ${written.join(', ')}`);
}

module.exports = { manifest, marketplace, askCommand, PLUGIN_NAME, MARKETPLACE_NAME };
