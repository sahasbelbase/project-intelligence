/**
 * How installed files should call this package. A normal install (a clone or a global
 * npm install) is referenced by absolute path. A run from the npx cache is not: npm
 * may delete that folder at any time, so installed files call npx instead.
 */
const path = require('path');

// The package as npx fetches it from the npm registry.
const RUN_SPEC = '@sahasbelbase/project-intelligence';

function isEphemeral(packageRoot) {
  return path.resolve(packageRoot).split(path.sep).includes('_npx');
}

/** Command prefix for the CLI, for example `node "/opt/pi/bin/cli.js"` or `npx -y github:...`. */
function cliInvocation(packageRoot) {
  return isEphemeral(packageRoot)
    ? `npx -y ${RUN_SPEC}`
    : `node ${JSON.stringify(path.join(packageRoot, 'bin', 'cli.js'))}`;
}

/** MCP server entry for client config files. */
function mcpServerEntry(packageRoot, targetDir) {
  if (isEphemeral(packageRoot)) {
    return { command: 'npx', args: ['-y', RUN_SPEC, 'mcp'], env: { PYTHONUNBUFFERED: '1' } };
  }
  const local = targetDir && path.resolve(targetDir) === path.resolve(packageRoot);
  const script = local ? 'adapters/mcp/server.py' : path.join(packageRoot, 'adapters', 'mcp', 'server.py');
  return { command: 'python3', args: [script], env: { PYTHONUNBUFFERED: '1' } };
}

module.exports = { RUN_SPEC, isEphemeral, cliInvocation, mcpServerEntry };
