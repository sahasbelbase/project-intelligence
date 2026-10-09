/**
 * Finds a Python 3.10+ interpreter. macOS and Linux usually have `python3`; Windows
 * usually has the `py` launcher or `python`, and its `python3` is often a Store alias
 * that does nothing. PYTHON overrides the search (for example PYTHON="py -3").
 */
const { spawnSync } = require('child_process');

let cached = null;

function works(cmd, args) {
  const res = spawnSync(cmd, [...args, '-c', 'import sys; print(sys.version_info >= (3, 10))'],
    { encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'], windowsHide: true });
  return !res.error && res.status === 0 && res.stdout.trim() === 'True';
}

/** Returns { cmd, args } to spawn Python with, or null if none is found. */
function findPython() {
  if (cached) return cached;
  if (process.env.PYTHON) {
    const [cmd, ...args] = process.env.PYTHON.split(' ').filter(Boolean);
    cached = { cmd, args };
    return cached;
  }
  const candidates = process.platform === 'win32'
    ? [['py', ['-3']], ['python', []], ['python3', []]]
    : [['python3', []], ['python', []]];
  for (const [cmd, args] of candidates) {
    if (works(cmd, args)) {
      cached = { cmd, args };
      return cached;
    }
  }
  return null;
}

const PYTHON_HELP = process.platform === 'win32'
  ? 'Install Python 3.10 or later from python.org (tick "Add python.exe to PATH"), or set PYTHON, for example PYTHON="py -3".'
  : 'Install Python 3.10 or later, or set PYTHON to its path.';

module.exports = { findPython, PYTHON_HELP };
