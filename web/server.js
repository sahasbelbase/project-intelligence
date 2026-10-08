#!/usr/bin/env node
/**
 * Project Intelligence — Local-First Web Server & API Gateway
 * Zero external npm dependencies.
 * Provides static file serving + live repository telemetry endpoints.
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const url = require('url');
const { execFile, execFileSync } = require('child_process');
const BUNDLES = require('./bundles');

const WEB_DIR = __dirname;
const ROOT_DIR = path.resolve(__dirname, '..');
const DEFAULT_PORT = parseInt(process.env.PORT, 10) || 3000;

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.md': 'text/markdown; charset=utf-8',
  '.zip': 'application/zip',
  '.txt': 'text/plain; charset=utf-8',
  '.xml': 'application/xml; charset=utf-8',
};

// Anti-Slop Evaluator Rule Checks
function evaluateAntiSlop(code) {
  const violations = [];

  // BL-001: Emoji check
  const emojiRegex = /[\u{1F300}-\u{1F9FF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/u;
  if (emojiRegex.test(code)) {
    violations.push({
      ruleId: "BL-001",
      name: "disallowGratuitousEmoji",
      message: "Decorative emojis detected in code/comments. Professional code must maintain strict clarity."
    });
  }

  // BL-002: Hardcoded fake data
  const fakeDataPatterns = [
    /(['"`])(lorem ipsum|fake[-_]?data|mock[-_]?user|test[-_]?credit[-_]?card|john\.doe@example\.com)\1/i,
    /0000-0000-0000-0000/
  ];
  for (const pat of fakeDataPatterns) {
    if (pat.test(code)) {
      violations.push({
        ruleId: "BL-002",
        name: "disallowFakeDataInProd",
        message: "Suspected fake production data or mock strings detected."
      });
      break;
    }
  }

  // BL-003: Unimplemented placeholders
  const placeholderPatterns = [
    /\/\/\s*TODO:\s*(implement|finish|fix later|add later)/i,
    /#\s*TODO:\s*(implement|finish|fix later|add later)/i,
    /function\s+\w+\([^)]*\)\s*\{\s*\/\*\s*TODO\s*\*\/|\bpass\s*#\s*implement/i,
    /throw new (NotImplementedException|Error\(["']not implemented["']\))/i
  ];
  for (const pat of placeholderPatterns) {
    if (pat.test(code)) {
      violations.push({
        ruleId: "BL-003",
        name: "disallowUnimplementedPlaceholders",
        message: "Unimplemented TODO placeholder, stub function, or unfinished branch detected."
      });
      break;
    }
  }

  // BL-004: Swallowed errors
  if (/catch\s*\([^)]*\)\s*\{\s*(\/\/[^\n]*)?\s*\}/.test(code) || /except\s*:\s*pass/.test(code)) {
    violations.push({
      ruleId: "BL-004",
      name: "disallowUnexplainedWorkarounds",
      message: "Silent error swallowing without documented root cause and telemetry logging."
    });
  }

  // BL-007: Secret leakage
  const secretPatterns = [
    /(api[_-]?key|secret|password|access[_-]?token|bearer)\s*[:=]\s*['"][a-zA-Z0-9_\-]{16,}['"]/i,
    /sk-[a-zA-Z0-9]{20,}/
  ];
  for (const pat of secretPatterns) {
    if (pat.test(code)) {
      violations.push({
        ruleId: "BL-007",
        name: "secretLeakagePrevention",
        message: "Suspected hardcoded API key, token, or secret detected in source text."
      });
      break;
    }
  }

  return {
    compliant: violations.length === 0,
    rulesEvaluated: 7,
    violationsCount: violations.length,
    violations
  };
}

function gitHead() {
  try {
    return execFileSync('git', ['rev-parse', '--short', 'HEAD'], { cwd: ROOT_DIR, encoding: 'utf8', stdio: ['ignore', 'pipe', 'ignore'] }).trim();
  } catch {
    return null;
  }
}

function gitHasPath(relPath) {
  try {
    execFileSync('git', ['cat-file', '-e', `HEAD:${relPath}`], { cwd: ROOT_DIR, stdio: 'ignore' });
    return true;
  } catch {
    return false;
  }
}

function handleApiRequest(req, res, parsedUrl) {
  const pathname = parsedUrl.pathname;

  // CORS headers for local development
  res.setHeader('Access-Control-Allow-Origin', `http://${req.headers.host || 'localhost'}`);
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  if (req.method === 'OPTIONS') {
    res.writeHead(204);
    res.end();
    return;
  }

  if (pathname === '/api/status' && req.method === 'GET') {
    try {
      const stateFile = path.join(ROOT_DIR, 'memory', 'execution-state.json');
      const state = JSON.parse(fs.readFileSync(stateFile, 'utf8'));
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        status: 'OK',
        timestamp: new Date().toISOString(),
        currentGate: state.currentGate,
        downloadsCommit: gitHead(),
        activePhase: state.activePhase,
        currentBranch: state.currentBranch,
        lastReconciledCommit: state.lastReconciledCommit,
        completedTasksCount: (state.completedTasks || []).length,
        uncommittedChangesCount: (state.uncommittedChanges || []).length,
        tasks: state.completedTasks || []
      }));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
    return;
  }

  if (pathname === '/api/memory' && req.method === 'GET') {
    try {
      const exec = JSON.parse(fs.readFileSync(path.join(ROOT_DIR, 'memory', 'execution-state.json'), 'utf8'));
      const durable = JSON.parse(fs.readFileSync(path.join(ROOT_DIR, 'memory', 'durable-knowledge.json'), 'utf8'));
      const backlog = JSON.parse(fs.readFileSync(path.join(ROOT_DIR, 'memory', 'backlog.json'), 'utf8'));
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ executionState: exec, durableKnowledge: durable, backlog }));
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: err.message }));
    }
    return;
  }

  if (pathname === '/api/audit' && req.method === 'POST') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const payload = JSON.parse(body || '{}');
        const code = payload.code || '';
        const result = evaluateAntiSlop(code);
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify(result));
      } catch (err) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Invalid JSON payload' }));
      }
    });
    return;
  }

  if (pathname === '/api/plan' && req.method === 'POST') {
    let body = '';
    req.on('data', (chunk) => {
      body += chunk;
      if (body.length > 10000) req.destroy();
    });
    req.on('end', () => {
      let task;
      try {
        task = JSON.parse(body || '{}').task;
      } catch {
        task = null;
      }
      if (typeof task !== 'string' || !task.trim() || task.length > 2000) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Send {"task": "..."} with 1 to 2000 characters.' }));
        return;
      }
      // Arguments are passed as a list (no shell), so task text cannot inject commands.
      execFile(process.env.PYTHON || 'python3', ['-m', 'core.orchestrator.dispatch', task.trim(), '--json'],
        { cwd: ROOT_DIR, timeout: 15000, maxBuffer: 1024 * 1024, env: { ...process.env, PI_CLI: 'project-intelligence' } }, (err, stdout) => {
          if (err) {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: 'The planner could not run. Is python3 installed?' }));
            return;
          }
          res.writeHead(200, { 'Content-Type': 'application/json' });
          res.end(stdout);
        });
    });
    return;
  }

  const download = pathname.match(/^\/api\/download\/([a-z-]+)\.zip$/);
  if (download && req.method === 'GET') {
    const bundle = BUNDLES.find((b) => b.id === download[1]);
    const commit = gitHead();
    if (!bundle || !commit) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: bundle ? 'Downloads need a git checkout with at least one commit' : 'Unknown bundle' }));
      return;
    }
    const paths = bundle.paths.filter((p) => p === '.' || gitHasPath(p));
    if (paths.length === 0) {
      res.writeHead(404, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'None of this bundle\'s files are committed yet' }));
      return;
    }
    let zip;
    try {
      zip = execFileSync('git', ['archive', '--format=zip', '--prefix=project-intelligence/', 'HEAD', '--', ...paths],
        { cwd: ROOT_DIR, maxBuffer: 256 * 1024 * 1024, stdio: ['ignore', 'pipe', 'pipe'] });
    } catch (err) {
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: 'git archive failed' }));
      return;
    }
    res.writeHead(200, {
      'Content-Type': 'application/zip',
      'Content-Length': zip.length,
      'Content-Disposition': `attachment; filename="project-intelligence-${bundle.id}-${commit}.zip"`,
    });
    res.end(zip);
    return;
  }

  res.writeHead(404, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify({ error: 'API endpoint not found' }));
}

function serveStatic(req, res, parsedUrl) {
  let reqPath = parsedUrl.pathname;
  if (reqPath === '/' || reqPath === '') {
    reqPath = '/index.html';
  }

  const filePath = path.join(WEB_DIR, path.normalize(reqPath).replace(/^(\.\.[\/\\])+/, ''));
  const ext = path.extname(filePath).toLowerCase();

  fs.stat(filePath, (err, stats) => {
    if (err || !stats.isFile()) {
      res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' });
      res.end('404 Not Found');
      return;
    }

    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });
    fs.createReadStream(filePath).pipe(res);
  });
}

const server = http.createServer((req, res) => {
  const parsedUrl = new URL(req.url, `http://${req.headers.host || 'localhost'}`);
  if (parsedUrl.pathname.startsWith('/api/')) {
    handleApiRequest(req, res, parsedUrl);
  } else {
    serveStatic(req, res, parsedUrl);
  }
});

function startServer(port) {
  server.listen(port, process.env.HOST || '127.0.0.1', () => {
    console.log('\n======================================================');
    console.log('   PROJECT INTELLIGENCE — Web Portal & Cockpit');
    console.log('======================================================');
    console.log(` -> Web Portal:  http://localhost:${port}`);
    console.log(` -> Live API:    http://localhost:${port}/api/status`);
    console.log(' -> Mode:        Local-First (Zero Cloud Dependencies)');
    console.log('======================================================\n');
  });

  server.on('error', (err) => {
    if (err.code === 'EADDRINUSE') {
      console.log(`Port ${port} in use, trying port ${port + 1}...`);
      startServer(port + 1);
    } else {
      console.error('Server error:', err);
    }
  });
}

if (require.main === module) {
  startServer(DEFAULT_PORT);
}

module.exports = { server, startServer, evaluateAntiSlop };
