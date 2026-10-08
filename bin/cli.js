#!/usr/bin/env node
/**
 * Project Intelligence — CLI Entrypoint
 * Forwards execution to installer/cli.js
 */

const path = require('path');
const cli = require(path.join(__dirname, '..', 'installer', 'cli.js'));

if (require.main === module) {
  cli.main(process.argv.slice(2)).then((code) => {
    process.exitCode = typeof code === 'number' ? code : 0;
  }).catch((err) => {
    console.error(`[Project Intelligence] Fatal error: ${err && err.message ? err.message : err}`);
    process.exit(1);
  });
}

module.exports = cli;
