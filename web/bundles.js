/**
 * Download bundles shared by web/build-data.js (what the site lists) and
 * web/server.js (what /api/download/<id>.zip may archive). Paths are
 * repository-relative and archived with `git archive` at HEAD.
 */
module.exports = [
  { id: 'framework', title: 'Full framework', type: 'Framework', paths: ['.'] },
  { id: 'skills', title: 'Skills only', type: 'Skills', paths: ['skills', 'vendor/skills'] },
  { id: 'councils', title: 'Council personas', type: 'Councils', paths: ['core/council', 'core/schemas'] },
  { id: 'mcp', title: 'MCP server', type: 'MCP', paths: ['adapters/mcp', 'core', 'memory', 'contracts'] },
];
