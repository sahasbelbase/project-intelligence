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

/** MCP server entry for client config files. It starts through Node, which finds the
 * right Python on every OS (python3 on macOS and Linux, py or python on Windows). */
function mcpServerEntry(packageRoot, targetDir) {
  if (isEphemeral(packageRoot)) {
    return { command: 'npx', args: ['-y', RUN_SPEC, 'mcp'], env: { PYTHONUNBUFFERED: '1' } };
  }
  const local = targetDir && path.resolve(targetDir) === path.resolve(packageRoot);
  const cli = local ? 'bin/cli.js' : path.join(packageRoot, 'bin', 'cli.js');
  return { command: 'node', args: [cli, 'mcp'], env: { PYTHONUNBUFFERED: '1' } };
}

module.exports = { RUN_SPEC, isEphemeral, cliInvocation, mcpServerEntry };
