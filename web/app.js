/**
 * Project Intelligence site. Renders window.PROJECT_DATA (built by web/build-data.js).
 * Read-only: councils are displayed here and run inside the coding agent.
 * Every interpolated value is HTML-escaped unless explicitly wrapped with raw().
 */
(function () {
  'use strict';

  const DATA = window.PROJECT_DATA || {};
  const main = document.getElementById('main');
  const state = {
    server: null,          // { commit } when served by web/server.js with git available
    client: (DATA.install && DATA.install.clients && DATA.install.clients[0].id) || 'claude',
    agentQuery: '',
    agentGroup: 'all',
    auditCode: '',
    auditResult: null,
    firstRender: true,
  };

  // ------------------------------------------------------------------ templating
  class Raw { constructor(v) { this.v = v; } }
  const raw = (v) => new Raw(v);
  const ESC = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ESC[c]);
  function fmt(v) {
    if (v instanceof Raw) return v.v;
    if (Array.isArray(v)) return v.map(fmt).join('');
    if (v === null || v === undefined || v === false) return '';
    return esc(v);
  }
  function html(strings, ...vals) {
    let out = '';
    strings.forEach((s, i) => { out += s + (i < vals.length ? fmt(vals[i]) : ''); });
    return raw(out);
  }

  const ICON = {
    copy: raw('<svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="9" width="12" height="12" rx="3"/><path d="M5 15V6a3 3 0 0 1 3-3h9"/></svg>'),
    download: raw('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M12 4v11m0 0 4.5-4.5M12 15l-4.5-4.5M5 20h14"/></svg>'),
    back: raw('<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.75" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M15 6l-6 6 6 6"/></svg>'),
  };

  const canDownload = () => !!(state.server && state.server.commit);
  const count = (n, one, many) => `${n} ${n === 1 ? one : (many || one + 's')}`;
  const shortDate = (iso) => {
    const d = new Date(iso);
    return isNaN(d) ? String(iso || '') : d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
  };
  const repoFile = (p) => (DATA.install && DATA.install.repoUrl ? `${DATA.install.repoUrl}/blob/main/${p}` : null);
  const initial = (s) => (String(s).replace(/^[^a-z0-9]+/i, '')[0] || '?').toUpperCase();

  function cmd(text, opts = {}) {
    return html`<div class="cmd ${opts.large ? 'cmd-lg' : ''}">
      <span class="prompt" aria-hidden="true">$</span><span class="text">${text}</span>
      <button class="btn btn-on-dark" type="button" data-copy="${text}" aria-label="Copy command: ${text}">Copy</button>
    </div>`;
  }

  // ------------------------------------------------------------------ lookups
  const skillIndex = {};
  (DATA.skills || []).forEach((s) => { skillIndex[s.id] = s; });
  (DATA.vendored || []).forEach((v) => { skillIndex[v.id] = { ...v, purpose: v.summary }; });
  const agentIndex = {};
  (DATA.agents || []).forEach((a) => { agentIndex[a.id] = a; });
  const personaIndex = {};
  (DATA.councils || []).forEach((c) => c.members.forEach((m) => { personaIndex[m.id] = { ...m, councilId: c.id, councilTitle: c.title }; }));
  const sessionIndex = {};
  (DATA.sessions || []).forEach((s) => { sessionIndex[s.brief.decisionId] = s; });
  const totalSkills = (DATA.counts.skills || 0) + (DATA.counts.vendoredSkills || 0);

  // ------------------------------------------------------------------ pages
  function skillsPage() {
    const inst = DATA.install;
    return html`
      <section class="hero hero-split" aria-labelledby="skills-title">
        <div>
          <h1 id="skills-title">Skills for your agents.</h1>
          <p class="lede">One install adds every skill, the agents and councils that use them, and the rules they follow. Then ask your agent for what you need, or call a skill by name.</p>
        </div>
        <div class="install-card">
          <span class="kicker">Install in Claude Code</span>
          <div class="cmd-stack">${cmd(inst.plugin.add)}${cmd(inst.plugin.install)}</div>
          <p class="note">Then type <code>${inst.plugin.use}</code>. Other tools: <code>${inst.init}</code> · ${count(totalSkills, 'skill')} · ${inst.license}</p>
        </div>
      </section>

      <div class="with-rail">
        <aside class="rail" aria-labelledby="rail-title">
          <h2 id="rail-title">Skills</h2>
          <p>Grouped by when you reach for them. Most people start with the main flow.</p>
          <ul class="rail-links">
            ${DATA.skillGroups.map((g) => html`<li><a href="#/skills" data-scroll="group-${g.n}"><span class="num">${g.n}</span>${g.title}</a></li>`)}
          </ul>
        </aside>
        <div class="groups">
          ${DATA.skillGroups.map((g, gi) => html`
            <section id="group-${g.n}" aria-labelledby="group-${g.n}-title">
              <div class="group-head"><span class="num" aria-hidden="true">${g.n}</span><h3 id="group-${g.n}-title">${g.title}</h3></div>
              <p class="group-sub">${g.sub}</p>
              <div class="tiles">
                ${g.skills.map((k, si) => html`
                  <button class="tile" type="button" data-skill="${k.id}">
                    <span class="badge tone-${(gi + si) % 4}" aria-hidden="true">${initial(k.id)}</span>
                    <span class="body">
                      <span class="name">/${k.id}</span>
                      <span class="desc">${k.desc}</span>
                      ${k.vendored ? html`<span class="meta"><span class="tag tag-accent-2">Third-party · ${skillIndex[k.id].license}</span></span>` : ''}
                    </span>
                  </button>`)}
              </div>
            </section>`)}
        </div>
      </div>

      <section class="section" aria-labelledby="what-title">
        <div class="columns">
          <div style="grid-column: 1 / -1">
            <h2 id="what-title">What is a skill?</h2>
            <p class="section-intro">A skill is an instruction file your agent follows for one kind of work, such as writing requirements or reviewing a change. The orchestrator picks skills for you, or you can call one by name.</p>
          </div>
          <div><h3>One install</h3><p>The installer copies every skill, the standing rules and the MCP server into your project, and records what it changed so it can be undone.</p></div>
          <div><h3>Same process every time</h3><p>Each skill lists its steps, outputs and checks, so the agent works the same way on every project.</p></div>
          <div><h3>They chain through gates</h3><p>Each skill's output is a contract the next gate checks, from discovery at G0 to release at G6.</p></div>
        </div>
      </section>

      <section class="section" aria-labelledby="changes-title">
        <h2 id="changes-title" style="margin-bottom:24px">What changed recently</h2>
        <ul class="changes">
          ${DATA.changelog.map((c) => html`<li>
            <span class="tag tag-accent">v${c.version}</span>
            <span class="date muted">${shortDate(c.date + 'T12:00:00Z')}</span>
            <span class="what">${c.summary}</span>
          </li>`)}
        </ul>
      </section>

      <section class="cta" aria-labelledby="cta-title">
        <div><h2 id="cta-title">Install and get to work</h2><p>${inst.license} licensed. Needs Node ${inst.node || '18+'} and Python 3.10 or later, with no other dependencies.</p></div>
        <div class="cmd-stack">${cmd(inst.plugin.add)}${cmd(inst.plugin.install)}</div>
      </section>`;
  }

  function councilsPage() {
    const sessions = DATA.sessions || [];
    const L = DATA.councilLimits || {};
    return html`
      <section class="hero hero-split" aria-labelledby="councils-title">
        <div>
          <h1 id="councils-title">Councils that argue before you build.</h1>
          <p class="lede">For decisions that matter, a small group of specialists convenes: a chair, a critic, and up to ${L.maxConveneSize - 2} experts the task needs. They assess the task independently, challenge each other, then revise. The chair writes the decision, and any disagreement stays on record.</p>
        </div>
        <div class="install-card">
          <span class="kicker">Plan a session from your terminal</span>
          ${cmd(`${DATA.install.run} council plan "Redesign the settings page"`)}
          <p class="note">Sessions run inside your coding agent. This page shows the councils and the decisions they have recorded.</p>
        </div>
      </section>

      <section class="section" aria-labelledby="tiers-title">
        <h2 id="tiers-title">How much process a task gets</h2>
        <p class="section-intro" style="margin-bottom:24px">Most requests never reach a council. The referee decides from the task itself.</p>
        <ol class="tiers">
          ${Object.entries(DATA.tiers || {}).map(([n, t]) => html`<li><div class="n">${n}</div><div class="t">${t.name}</div><p>${t.description}</p></li>`)}
        </ol>
      </section>

      <section class="section" aria-labelledby="decisions-title">
        <div class="section-head">
          <div><h2 id="decisions-title">Decisions on record</h2>
          <p class="section-intro">Saved in <code>memory/council-briefs/</code> and checked by the referee before they appear here.</p></div>
        </div>
        ${sessions.length ? html`<ul class="sessions">
          ${sessions.map((s) => html`<li><a class="session-link" href="#/councils/${s.brief.decisionId}">
            <span class="topic">${s.task}</span>
            <span class="tag ${s.brief.recommendation === 'Build' ? 'tag-pass' : 'tag-warn'}">${s.brief.recommendation}</span>
            <span class="meta">${s.councilTitle} · ${shortDate(s.createdAt)} · ${count(s.convened.length, 'persona')} · ${blindingLabel(s)} · ${s.brief.dissent.length ? count(s.brief.dissent.length, 'dissent') : 'no dissent'}${s.mode === 'simulated' ? ' · simulated' : ''}</span>
          </a></li>`)}
        </ul>` : html`<p class="empty">No decisions recorded yet. Run a council from your agent and save it with the referee to see it here.</p>`}
      </section>

      <section class="section" aria-labelledby="rosters-title">
        <h2 id="rosters-title">The councils</h2>
        <p class="section-intro" style="margin-bottom:32px">${count(DATA.councils.reduce((n, c) => n + c.members.length, 0), 'persona')} across ${count(DATA.councils.length, 'council')}. Select a persona to see what it looks for.</p>
        ${DATA.councils.map((c) => html`
          <section class="council" aria-labelledby="council-${c.id}">
            <div class="council-head"><h3 id="council-${c.id}">${c.title}</h3><span class="muted">${count(c.members.length, 'persona')}</span></div>
            <p class="council-purpose">${c.purpose}</p>
            <div class="tiles tiles-3">
              ${c.members.map((m, i) => html`
                <button class="tile" type="button" data-persona="${m.id}">
                  <span class="badge tone-${i % 4}" aria-hidden="true">${initial(m.title)}</span>
                  <span class="body">
                    <span class="title">${m.title}</span>
                    ${m.role !== 'specialist' ? html`<span class="meta"><span class="tag ${m.role === 'chair' ? 'tag-accent' : 'tag-accent-2'}">${m.role === 'chair' ? 'Chair' : 'Critic'}</span></span>` : ''}
                  </span>
                </button>`)}
            </div>
          </section>`)}
      </section>`;
  }

  function list(items) {
    return items && items.length ? html`<ul>${items.map((i) => html`<li>${typeof i === 'string' ? i : itemText(i)}</li>`)}</ul>` : html`<p class="muted">None recorded.</p>`;
  }
  function itemText(i) {
    if (i.statement) return `${i.category ? i.category.replace('_', ' ').toLowerCase() + ': ' : ''}${i.statement}${i.source ? ` (${i.source})` : ''}`;
    if (i.aspect) return `${i.aspect}: ${i.chosen}, instead of ${lowerFirst(i.sacrificed)}.${i.rationale ? ` ${i.rationale}` : ''}`;
    if (i.riskId) return `${i.description} (${i.severity.toLowerCase()} severity${i.probability ? `, ${i.probability.toLowerCase()} probability` : ''})`;
    if (i.metric) return `${i.metric}: ${i.target}${i.timeframe ? ` (${i.timeframe})` : ''}`;
    if (i.hypothesis) return `${i.hypothesis}. Test: ${i.experiment}. Pass if: ${i.passMetric}`;
    return JSON.stringify(i);
  }
  function lowerFirst(t) { return /^[A-Z][a-z]/.test(t) ? t[0].toLowerCase() + t.slice(1) : t; }
  // How the session was run: each persona as its own agent (Round 1 truly blind),
  // or one agent writing every persona.
  const blindingLabel = (s) => (s.blinding === 'separate-agents' ? 'independent agents' : 'one agent wrote every persona');
  const personaName = (id) => (personaIndex[id] ? personaIndex[id].title : id);

  function sessionPage(id) {
    const s = sessionIndex[id];
    if (!s) {
      return html`<section class="section" style="padding-top:64px"><h1 style="font-size:40px">Decision not found</h1>
        <p class="section-intro">There is no saved council decision with the id <code>${id}</code>.</p>
        <p style="margin-top:20px"><a class="btn btn-secondary" href="#/councils">${ICON.back} All councils</a></p></section>`;
    }
    const b = s.brief;
    const r = s.rounds;
    return html`
      <section class="hero" aria-labelledby="session-title" style="padding-bottom:32px">
        <p style="margin-bottom:20px"><a class="btn btn-ghost" href="#/councils">${ICON.back} All councils</a></p>
        <span class="kicker">${s.councilTitle} · ${shortDate(s.createdAt)} · ${blindingLabel(s)}${s.mode === 'simulated' ? ' · simulated' : ''}</span>
        <h1 id="session-title" class="session-title">${s.task}</h1>
      </section>
      <section class="section" style="padding-top:0">
        <div class="decision">
          <div>
            <span class="kicker">Recommendation</span>
            <div class="rec">${b.recommendation}</div>
            <p class="soft" style="margin-top:14px;max-width:70ch">${b.strongestArgumentsFor[0] || ''}</p>
          </div>
          <div class="confidence">
            <span class="kicker">Confidence</span>
            <span class="tag ${b.confidenceLevel === 'HIGH' ? 'tag-pass' : b.confidenceLevel === 'MEDIUM' ? 'tag-warn' : 'tag-fail'}">${b.confidenceLevel.toLowerCase()}</span>
          </div>
        </div>
        <div class="facts">
          ${b.dissent.length ? html`<div class="fact fact-wide dissent"><h3>Dissent on record</h3><ul>
            ${b.dissent.map((d) => html`<li><strong>${personaName(d.personaId)}</strong>: ${d.objection} ${d.rationale}${d.suggestedAlternative ? ` Alternative: ${d.suggestedAlternative}` : ''}</li>`)}
          </ul></div>` : ''}
          <div class="fact"><h3>For</h3>${list(b.strongestArgumentsFor)}</div>
          <div class="fact"><h3>Against</h3>${list(b.strongestArgumentsAgainst)}</div>
          <div class="fact"><h3>In scope</h3>${list(b.mvpScope)}</div>
          <div class="fact"><h3>Out of scope</h3>${list(b.excludedScope)}</div>
          <div class="fact fact-wide"><h3>Trade-offs</h3>${list(b.tradeOffs)}</div>
          <div class="fact"><h3>Risks</h3>${list(b.risks)}</div>
          <div class="fact"><h3>Mitigations</h3>${list(b.mitigations)}</div>
          <div class="fact"><h3>Evidence</h3>${list(b.evidence)}</div>
          <div class="fact"><h3>Assumptions and unknowns</h3>${list([...b.assumptions, ...b.unknowns.map((u) => `Unknown: ${u}`)])}</div>
          <div class="fact"><h3>Success measures</h3>${list(b.successMetrics)}</div>
          <div class="fact"><h3>Would change if</h3>${list(b.conditionsToChange)}</div>
          ${b.validationExperiments.length ? html`<div class="fact fact-wide"><h3>Validation</h3>${list(b.validationExperiments)}</div>` : ''}
        </div>
      </section>
      <section class="section" aria-labelledby="rounds-title" style="padding-top:0">
        <h2 id="rounds-title">How the council got there</h2>
        <p class="section-intro">${s.convened.map((m) => `${m.title}${m.role !== 'specialist' ? ` (${m.role})` : ''}`).join(', ')}. ${s.blinding === 'separate-agents'
          ? 'Each persona ran as its own agent, so the first round was written without seeing the others.'
          : 'One agent wrote every persona, so the first round was not strictly blind.'}</p>
        ${s.context ? html`<details class="round"><summary>Background every persona saw</summary><div class="round-body"><p class="soft" style="white-space:pre-wrap">${s.context}</p></div></details>` : ''}
        <details class="round"><summary>Round 1 · Independent assessments</summary><div class="round-body">
          ${r.independent.map((e) => html`<div class="entry"><div class="who">${personaName(e.personaId)} <span class="tag tag-neutral">${e.recommendation}</span></div>
            <p>${e.stance}</p>${list(e.keyArguments)}</div>`)}
        </div></details>
        <details class="round"><summary>Round 2 · Challenges</summary><div class="round-body">
          ${r.challenges.map((c) => html`<div class="entry"><div class="who">${personaName(c.challengerId)} challenged ${personaName(c.targetId)} <span class="tag tag-neutral">${c.challengeType.replace(/_/g, ' ').toLowerCase()}</span></div>
            <p>${c.critique}</p><p class="soft" style="margin-top:6px">Instead: ${c.counterProposal}</p></div>`)}
        </div></details>
        <details class="round"><summary>Round 3 · Revisions</summary><div class="round-body">
          ${r.revisions.map((v) => html`<div class="entry"><div class="who">${personaName(v.personaId)} <span class="tag tag-neutral">${v.revisedRecommendation}</span></div>
            ${(v.responses || []).map((a) => html`<p>${a.response.replace('_', ' ').toLowerCase()} ${personaName(a.challengerId)}'s challenge: ${a.reason}</p>`)}
            ${list([...(v.whatChanged || []).map((w) => `Changed: ${w}`), ...(v.whatRemainedUnchanged || []).map((w) => `Kept: ${w}`)])}</div>`)}
        </div></details>
      </section>`;
  }

  function agentsPage() {
    const groups = ['all', ...new Set(DATA.agents.map((a) => a.group))];
    const q = state.agentQuery.toLowerCase().trim();
    const shown = DATA.agents.filter((a) => (state.agentGroup === 'all' || a.group === state.agentGroup)
      && (!q || `${a.name} ${a.id} ${a.mission}`.toLowerCase().includes(q)));
    return html`
      <section class="hero" aria-labelledby="agents-title" style="padding-bottom:40px">
        <h1 id="agents-title">Agents with one job each.</h1>
        <p class="lede">${count(DATA.agents.length, 'agent')}. Each has a mission, the skills it may use, and things it must not do. The orchestrator hands work to them; councils draw on them for product decisions.</p>
      </section>
      <section class="section" style="padding-top:0" aria-label="Agent directory">
        <div class="toolbar">
          <div class="field"><label for="agent-search">Search agents</label>
            <input class="input" id="agent-search" type="search" value="${state.agentQuery}" placeholder="Name, id or mission" /></div>
          <div class="chips" role="group" aria-label="Filter by group" style="align-self:end">
            ${groups.map((g) => html`<button class="btn btn-secondary" type="button" data-agent-group="${g}" aria-pressed="${g === state.agentGroup}">${g === 'all' ? 'All' : g[0].toUpperCase() + g.slice(1)}</button>`)}
          </div>
        </div>
        <p class="muted" aria-live="polite" style="margin-bottom:14px">${count(shown.length, 'agent')} shown</p>
        ${shown.length ? html`<div class="tiles">
          ${shown.map((a, i) => html`<button class="tile" type="button" data-agent="${a.id}">
            <span class="badge tone-${i % 4}" aria-hidden="true">${initial(a.name)}</span>
            <span class="body"><span class="title">${a.name}</span><span class="desc">${a.mission.length > 150 ? a.mission.slice(0, 147).replace(/\s+\S*$/, '') + '…' : a.mission}</span>
            <span class="meta"><span class="tag tag-neutral">${a.group}</span></span></span>
          </button>`)}
        </div>` : html`<p class="empty">No agents match. Clear the search or choose All.</p>`}
      </section>`;
  }

  function gatesPage() {
    const v = DATA.validation;
    const approved = DATA.gates.filter((g) => g.contract && g.contract.status === 'APPROVED').length;
    const res = state.auditResult;
    return html`
      <section class="hero" aria-labelledby="gates-title" style="padding-bottom:40px">
        <h1 id="gates-title">Every change passes the same gates.</h1>
        <p class="lede">Seven gates take work from discovery to release. Each one needs a signed contract, and the quality baseline applies at every step.</p>
      </section>
      <section class="section" style="padding-top:0" aria-label="Status">
        <div class="stats">
          <div class="stat"><div class="v">${DATA.currentGate}</div><div class="k">Current gate</div></div>
          <div class="stat"><div class="v">${approved}/${DATA.gates.length}</div><div class="k">Gate contracts approved</div></div>
          ${v ? html`<div class="stat"><div class="v">${v.passed}/${v.totalRun}</div><div class="k">Checks passed · ${shortDate(v.timestamp)}</div></div>`
            : html`<div class="stat"><div class="v">None</div><div class="k">No validation report yet</div></div>`}
          <div class="stat"><div class="v">${DATA.qualityRules.length}</div><div class="k">Baseline rules</div></div>
        </div>
        ${v ? html`<p class="muted" style="margin-top:12px">From <code>validation/reports/master_validation_report.json</code>: ${v.failed} failed, ${v.skipped} skipped, ${v.durationSeconds}s. Re-run from a clone with <code>python3 validation/test_runner.py</code> (<code>py -3</code> on Windows).</p>` : ''}
      </section>
      <section class="section" aria-labelledby="lifecycle-title">
        <h2 id="lifecycle-title" style="margin-bottom:24px">The lifecycle</h2>
        <ol class="gates">
          ${DATA.gates.map((g) => html`<li class="gate ${g.id === DATA.currentGate ? 'current' : ''}" ${g.id === DATA.currentGate ? raw('aria-current="step"') : ''}>
            <span class="badge" aria-hidden="true">${g.id}</span>
            <div><div class="name">${g.name}</div><p class="desc">${g.description}</p></div>
            <span class="status">${g.contract
              ? html`<span class="tag ${g.contract.status === 'APPROVED' ? 'tag-pass' : 'tag-warn'}">${g.contract.status.toLowerCase()}</span>`
              : html`<span class="tag tag-neutral">no contract</span>`}</span>
          </li>`)}
        </ol>
      </section>
      <section class="section" aria-labelledby="rules-title">
        <h2 id="rules-title">The quality baseline</h2>
        <p class="section-intro" style="margin-bottom:24px">These rules apply to every project, whatever its quality profile.</p>
        <ul class="rules">
          ${DATA.qualityRules.map((r) => html`<li><strong>${r.ruleId}</strong>${r.description}</li>`)}
        </ul>
      </section>
      <section class="section checker" aria-labelledby="check-title">
        <h2 id="check-title">Check a snippet</h2>
        <p class="section-intro" style="margin-bottom:20px">Paste code to scan it against the baseline rules. The check runs on the local server.</p>
        <label class="visually-hidden" for="audit-code">Code to check</label>
        <textarea id="audit-code" spellcheck="false" placeholder="Paste code here">${state.auditCode}</textarea>
        <p style="margin-top:12px"><button class="btn btn-primary" type="button" id="audit-run" ${state.server ? '' : raw('disabled aria-describedby="audit-off"')}>Check code</button></p>
        ${state.server ? '' : html`<p class="muted" id="audit-off" style="margin-top:8px">Start the site with <code>npm run site</code> to use the checker.</p>`}
        <div class="result" aria-live="polite">
          ${res && res.error ? html`<p class="tag tag-fail">${res.error}</p>` : ''}
          ${res && !res.error ? (res.compliant
            ? html`<p><span class="tag tag-pass">No violations</span> <span class="muted">${res.rulesEvaluated} rules checked.</span></p>`
            : res.violations.map((x) => html`<div class="entry"><div class="who"><span class="tag tag-fail">${x.ruleId}</span> ${x.name}</div><p>${x.message}</p></div>`)) : ''}
        </div>
      </section>`;
  }

  function installPage() {
    const inst = DATA.install;
    const c = DATA.counts;
    const client = inst.clients.find((x) => x.id === state.client) || inst.clients[0];
    const included = [
      { n: totalSkills, tone: 0, title: 'Skills', body: `${c.skills} framework skills and ${c.vendoredSkills} third-party design skills, with their licenses.` },
      { n: c.councils, tone: 1, title: 'Councils', body: `Design, development and product councils drawing on ${c.personas} persona definitions, plus the referee.` },
      { n: c.agents, tone: 2, title: 'Agents', body: 'Lifecycle, business, quality and commercial agents, each with clear boundaries.' },
      { n: c.mcpTools, tone: 3, title: 'MCP tools', body: 'Gates, contracts, quality checks and memory over the Model Context Protocol.' },
    ];
    return html`
      <section class="hero" aria-labelledby="install-title" style="padding-bottom:48px">
        <h1 id="install-title" style="max-width:15ch">The whole framework, in one install.</h1>
        <p class="lede" style="max-width:56ch">In Claude Code it's a plugin: skills, the <code>/project-intelligence:ask</code> command and the MCP server in one install that updates itself. Everywhere else, one <code>npx</code> command sets up a project and keeps a manifest so <code>uninstall</code> can undo it.</p>
        <div class="cmd-stack" style="max-width:660px;margin-top:32px">
          <div><div class="step-label"><span class="step-dot" aria-hidden="true">1</span>Add the marketplace in Claude Code</div>${cmd(inst.plugin.add, { large: true })}</div>
          <div><div class="step-label"><span class="step-dot" aria-hidden="true">2</span>Install the plugin, then type <code>${inst.plugin.use}</code></div>${cmd(inst.plugin.install, { large: true })}</div>
          <div><div class="step-label"><span class="step-dot" aria-hidden="true">or</span>Any other tool: set up the current project</div>${cmd(inst.init, { large: true })}</div>
        </div>
        <p class="soft" style="margin-top:16px">${canDownload()
          ? html`Prefer a file? <a href="/api/download/framework.zip" download>Download the framework as a ZIP</a> (last commit, ${state.server.commit}).`
          : html`Check your setup any time with <code>${inst.doctor}</code>.`}</p>
      </section>

      <section class="section" style="padding-top:0" aria-labelledby="os-title">
        <h2 id="os-title" style="font-size:26px;margin-bottom:10px">Works on macOS, Linux and Windows</h2>
        <p class="section-intro">The same commands work in Terminal, PowerShell and Command Prompt. You need Node 18 or later and Python 3.10 or later. On Windows, install Python from python.org and tick "Add python.exe to PATH"; the tool finds it as <code>py</code>, <code>python</code> or <code>python3</code>. If it is somewhere else, set <code>PYTHON</code>, for example <code>$env:PYTHON="py -3"</code> in PowerShell.</p>
      </section>

      <section class="section two-col" style="padding-top:24px" aria-label="What you get">
        <div>
          <span class="kicker">What's included</span>
          <ul class="included">
            ${included.map((i) => html`<li><span class="badge tone-${i.tone}" aria-hidden="true">${i.n}</span>
              <div><div class="title">${i.title}</div><div class="desc">${i.body}</div></div></li>`)}
          </ul>
        </div>
        <div class="panel">
          <h2>Pick your client</h2>
          <p class="soft">Claude Code and Antigravity get skills and rules installed directly. Other clients connect through the MCP server.</p>
          <div class="chips" role="tablist" aria-label="Client" style="margin-top:18px">
            ${inst.clients.map((x) => html`<button class="btn btn-secondary" type="button" role="tab" id="tab-${x.id}" aria-controls="client-panel" aria-selected="${x.id === client.id}" data-client="${x.id}">${x.label}</button>`)}
          </div>
          <div id="client-panel" role="tabpanel" aria-labelledby="tab-${client.id}">
            <div class="panel-row"><strong>${client.how}</strong><button class="btn btn-secondary" type="button" data-copy="${client.code}">${ICON.copy} Copy</button></div>
            <pre class="code">${client.code}</pre>
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="dl-title">
        <h2 id="dl-title">Just the parts you need</h2>
        <p class="section-intro" style="margin-bottom:24px">Each part has a command to run from your clone${canDownload() ? ' and a ZIP of the last commit' : ''}.</p>
        <div class="cards">
          ${inst.bundles.map((b) => html`<div class="card">
            <div><span class="tag ${b.type === 'Skills' ? 'tag-accent' : b.type === 'Councils' ? 'tag-accent-2' : 'tag-neutral'}">${b.type}</span></div>
            <div class="card-title">${b.title}</div>
            <div class="card-body">${b.desc}</div>
            ${cmd(b.cmd)}
            <div class="card-foot">
              <span class="card-meta">${b.paths[0] === '.' ? 'Whole repository' : b.paths.join(', ')}</span>
              ${canDownload() ? html`<a class="btn btn-ghost" href="/api/download/${b.id}.zip" download>${ICON.download} Download ZIP</a>` : ''}
            </div>
          </div>`)}
        </div>
      </section>

      <section class="section" aria-labelledby="third-title">
        <h2 id="third-title">Third-party skills</h2>
        <p class="section-intro" style="margin-bottom:24px">Copied unchanged from their authors, with licenses kept alongside. Others we recommend but don't redistribute; install them from their source.</p>
        <div class="cards">
          ${DATA.vendored.map((v) => html`<div class="card">
            <div class="chips"><span class="tag tag-pass">Included</span><span class="tag tag-neutral">${v.license}</span></div>
            <div class="card-title">${v.name}</div>
            <div class="card-body">${v.summary}</div>
            <div class="card-foot"><a href="${v.repository}" rel="noopener" target="_blank">${v.source}</a><span class="card-meta mono">${v.commit.slice(0, 7)}</span></div>
          </div>`)}
          ${DATA.referencedSkills.map((v) => html`<div class="card">
            <div class="chips"><span class="tag tag-outline">Install separately</span></div>
            <div class="card-title">${v.name}</div>
            <div class="card-body">${v.summary}</div>
            ${cmd(v.install)}
            <div class="card-foot"><a href="${v.repository}" rel="noopener" target="_blank">Source</a><span class="card-meta">${v.reasonNotVendored}</span></div>
          </div>`)}
        </div>
      </section>`;
  }

  // ------------------------------------------------------------------ how it works
  const ARROW = raw('<svg width="16" height="36" viewBox="0 0 16 36" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M8 1v31M3 26l5 7 5-7"/></svg>');
  const CLIENTS = [
    { id: 'claude', label: 'Claude Code', bar: 'claude · ~/my-project' },
    { id: 'copilot', label: 'Copilot CLI', bar: 'copilot · ~/my-project' },
    { id: 'terminal', label: 'Terminal', bar: 'zsh · ~/my-project' },
  ];
  const DEMO_NOTES = {
    question: 'Tier 0. Answered straight from the gate definitions.',
    fix: 'Tier 1. One specialist, one change, one new test.',
    design: 'Tier 2. The design council, then a follow-up improvement.',
    dev: 'Tier 2. The development council on this integration.',
    independent: 'Tier 2. Each persona ran as its own agent; round 1 was truly blind.',
    feature: 'Tier 3. Three councils in sequence. Plan only.',
    custom: 'Your request, planned live by the local server.',
  };
  const demoState = { scenario: 'design', client: 'claude', step: 2, playing: null, custom: null, error: null, busy: false };
  const scenarios = () => [...DATA.demo, ...(demoState.custom ? [demoState.custom] : [])];
  const currentScenario = () => scenarios().find((x) => x.id === demoState.scenario) || DATA.demo[0];

  function demoFrames(sc) {
    const frames = [];
    sc.turns.forEach((t) => {
      frames.push({ type: 'user', turn: t });
      frames.push({ type: 'plan', turn: t });
      const ses = t.sessionId && sessionIndex[t.sessionId];
      if (ses) {
        frames.push({ type: 'divider', text: `Round 1 · Independent views (${ses.councilTitle.toLowerCase()}${ses.blinding === 'separate-agents' ? ', one agent per persona' : ''})` });
        ses.rounds.independent.forEach((e) => frames.push({ type: 'r1', e, ses }));
        frames.push({ type: 'divider', text: 'Round 2 · Challenges' });
        ses.rounds.challenges.forEach((c) => frames.push({ type: 'r2', c, ses }));
        frames.push({ type: 'divider', text: 'Round 3 · Revisions' });
        ses.rounds.revisions.forEach((v) => frames.push({ type: 'r3', v, ses }));
        frames.push({ type: 'divider', text: 'Round 4 · Decision' });
        frames.push({ type: 'decision', ses });
        if (ses.brief.dissent.length) frames.push({ type: 'dissent', ses });
      } else if (t.reply) {
        frames.push({ type: 'reply', turn: t });
      }
    });
    return frames;
  }

  const roleOf = (ses, id) => ((ses.convened.find((m) => m.personaId === id) || {}).role || 'specialist');
  const avatar = (ses, id) => html`<span class="avatar ${roleOf(ses, id)}" aria-hidden="true">${initial(personaName(id))}</span>`;
  const roleChip = (ses, id) => (roleOf(ses, id) === 'specialist' ? '' : html`<span class="dchip">${roleOf(ses, id)}</span>`);

  function userLine(t, client) {
    const task = t.task;
    const flag = (t.council ? ` --council ${t.council}` : '') + (t.include || []).map((p) => ` --include ${p}`).join('');
    if (client === 'claude') {
      return html`<div class="term-line"><span class="glyph">&gt;</span>/project-intelligence:ask ${task}</div>
        <div class="term-line muted"><span class="glyph">•</span>Bash(project-intelligence ask "${task}"${flag})</div>`;
    }
    if (client === 'copilot') {
      return html`<div class="term-line"><span class="glyph">&gt;</span>${task}</div>
        <div class="term-line muted"><span class="glyph">•</span>plan_task (MCP: project-intelligence)${t.council ? `, council: ${t.council}` : ''}${(t.include || []).length ? `, include: ${t.include.join(', ')}` : ''}</div>`;
    }
    return html`<div class="term-line"><span class="glyph">$</span>${DATA.install.run.replace(' -y', '')} ask "${task}"${flag}</div>`;
  }

  function renderFrame(f, client) {
    switch (f.type) {
      case 'user': return userLine(f.turn, client);
      case 'plan': return html`<pre class="term-out">${f.turn.plan.summary}</pre>`;
      case 'divider': return html`<div class="round-divider">${f.text}</div>`;
      case 'r1': return html`<div class="bubble">${avatar(f.ses, f.e.personaId)}<div class="msg">
          <div class="who">${personaName(f.e.personaId)} ${roleChip(f.ses, f.e.personaId)}<span class="dchip">${f.e.recommendation}</span></div>
          <p>${f.e.stance}</p><ul>${f.e.keyArguments.map((a) => html`<li>${a}</li>`)}</ul></div></div>`;
      case 'r2': return html`<div class="bubble reply">${avatar(f.ses, f.c.challengerId)}<div class="msg">
          <div class="who">${personaName(f.c.challengerId)} <span class="dchip to">to ${personaName(f.c.targetId)}</span><span class="dchip">${f.c.challengeType.replace(/_/g, ' ').toLowerCase()}</span></div>
          <p>${f.c.critique}</p><p class="term-line muted" style="font-family:var(--font-body)">Instead: ${f.c.counterProposal}</p></div></div>`;
      case 'r3': return html`<div class="bubble">${avatar(f.ses, f.v.personaId)}<div class="msg">
          <div class="who">${personaName(f.v.personaId)} <span class="dchip">${f.v.revisedRecommendation}</span></div>
          ${(f.v.responses || []).map((a) => html`<p><span class="dchip ${a.response === 'REJECTED' ? 'no' : 'ok'}">${a.response.replace('_', ' ').toLowerCase()}</span> ${personaName(a.challengerId)}: ${a.reason}</p>`)}
          ${(f.v.whatChanged || []).length ? html`<ul>${f.v.whatChanged.map((w) => html`<li>Changed: ${w}</li>`)}</ul>` : html`<p>No change. Kept: ${(f.v.whatRemainedUnchanged || []).join('; ')}</p>`}
        </div></div>`;
      case 'decision': {
        const b = f.ses.brief;
        return html`<div class="card-dark"><span class="label">Decision · ${b.confidenceLevel.toLowerCase()} confidence</span>
          <div class="big">${b.recommendation}</div><p>${b.strongestArgumentsFor[0]}</p>
          <p style="margin-top:8px"><a href="#/councils/${b.decisionId}" style="color:var(--code-accent)">Read the full decision</a></p></div>`;
      }
      case 'dissent': return html`<div class="card-dark warn"><span class="label">Dissent on record</span>
          ${f.ses.brief.dissent.map((d) => html`<p><strong>${personaName(d.personaId)}:</strong> ${d.objection} ${d.rationale}</p>`)}</div>`;
      case 'reply': {
        const r = f.turn.reply;
        if (r.kind === 'pipeline') {
          return html`<div class="card-dark"><span class="label">Plan only</span>
            <p>No recorded session for this request yet. Your agent runs each council in order with the prompts above, and every decision is checked by the referee before it is saved.</p></div>`;
        }
        const who = r.kind === 'answer' ? 'Orchestrator' : r.title;
        return html`<div class="bubble"><span class="avatar ${r.kind === 'answer' ? 'chair' : ''}" aria-hidden="true">${initial(who)}</span><div class="msg">
          <div class="who">${who}${r.kind === 'answer' ? html` <span class="dchip">${r.title}</span>` : ''}</div>
          <ul>${r.lines.map((l) => html`<li>${l}</li>`)}</ul></div></div>`;
      }
      default: return '';
    }
  }

  function demoWindow() {
    const sc = currentScenario();
    const frames = demoFrames(sc);
    const step = Math.min(demoState.step, frames.length);
    const client = CLIENTS.find((c) => c.id === demoState.client);
    return html`
      <div class="chips" role="tablist" aria-label="Client" style="margin-bottom:12px">
        ${CLIENTS.map((c) => html`<button class="btn btn-secondary" type="button" role="tab" aria-selected="${c.id === client.id}" aria-controls="demo-log" data-demo-client="${c.id}">${c.label}</button>`)}
      </div>
      <div class="window">
        <div class="window-bar"><span class="dots" aria-hidden="true"><span></span><span></span><span></span></span>${client.bar}</div>
        <div class="window-body" id="demo-log" role="log" aria-live="polite" aria-label="Conversation">
          ${frames.slice(0, step).map((f) => html`<div class="frame">${renderFrame(f, client.id)}</div>`)}
        </div>
        <div class="window-controls">
          <button class="btn btn-primary" type="button" data-demo-action="next" ${step >= frames.length ? raw('disabled') : ''}>Next step</button>
          <button class="btn btn-secondary" type="button" data-demo-action="play" aria-pressed="${!!demoState.playing}" ${step >= frames.length ? raw('disabled') : ''}>${demoState.playing ? 'Pause' : 'Play'}</button>
          <button class="btn btn-secondary" type="button" data-demo-action="all" ${step >= frames.length ? raw('disabled') : ''}>Show all</button>
          <button class="btn btn-secondary" type="button" data-demo-action="restart">Restart</button>
          <span class="progress" id="demo-progress">${step} / ${frames.length}</span>
        </div>
      </div>
      <form class="try" id="demo-form">
        <div class="field"><label for="demo-task">Try your own request</label>
          <input class="input" id="demo-task" name="task" maxlength="2000" placeholder="For example: Add search to the agents page" ${state.server ? '' : raw('disabled aria-describedby="demo-off"')} /></div>
        <button class="btn btn-primary" type="submit" ${state.server && !demoState.busy ? '' : raw('disabled')}>${demoState.busy ? 'Planning…' : 'Plan it'}</button>
      </form>
      ${state.server ? '' : html`<p class="muted" id="demo-off" style="margin-top:8px">Start the site with <code>npm run site</code> to plan your own requests with the real dispatcher.</p>`}
      ${demoState.error ? html`<p class="tag tag-fail" style="margin-top:8px">${demoState.error}</p>` : ''}`;
  }

  function howPage() {
    const tiers = [
      { n: 0, name: 'Answer', demo: 'question', what: ['Questions about the framework', 'Answered from its own files'], uses: ['lifecycle', 'contracts'] },
      { n: 1, name: 'Specialist', demo: 'fix', what: ['One focused change', 'The best-matching persona applies its skills'], uses: ['agents/', 'skills/', 'vendor/skills/'] },
      { n: 2, name: 'Council', demo: 'design', what: ['Chair, critic and up to 3 specialists', 'Four rounds, dissent kept'], uses: ['councils.json', 'personas/'] },
      { n: 3, name: 'Cross-council', demo: 'feature', what: ['Product, then design, then development', 'Quality review, then synthesis'], uses: ['hand-offs', 'qa-analyst'] },
    ];
    return html`
      <section class="hero" aria-labelledby="how-title" style="padding-bottom:40px">
        <h1 id="how-title" style="max-width:16ch">How a request moves through the system.</h1>
        <p class="lede" style="max-width:60ch">Whatever tool you use, every request goes to the same orchestrator. It decides how much process the work needs, hands it to a specialist or a council, and keeps the result on record.</p>
      </section>

      <section class="section" aria-labelledby="flow-title" style="padding-top:0">
        <h2 id="flow-title" class="visually-hidden">Flowchart</h2>
        <div class="flow">
          <div class="flow-row" aria-label="Entry points">
            ${DATA.entryPoints.map((e) => html`<div class="flow-node"><span class="k">${e.how}</span><div class="t">${e.label}</div><code class="path">${e.example}</code></div>`)}
          </div>
          <div class="flow-arrow">${ARROW}</div>
          <div class="flow-node flow-hub">
            <div><span class="k">Orchestrator</span><div class="t">Plans every request</div>
              <p class="d">Combines the referee's routing with the current lifecycle gate and returns one plan: the tier, who handles it, and the next commands.</p>
              <span class="path">core/orchestrator/dispatch.py</span></div>
            <div class="reads"><span class="k">Asks the referee</span><p class="d">Which tier, which council, which ${count(DATA.councilLimits.maxConveneSize, 'persona')} at most. Builds each persona's prompt.</p><span class="path">core/council/referee.py</span></div>
            <div class="reads"><span class="k">Checks the gate</span><p class="d">Current gate ${DATA.currentGate} and its contract, so work doesn't skip a step.</p><span class="path">memory/execution-state.json</span></div>
          </div>
          <div class="flow-arrow">${ARROW}</div>
          <div class="flow-branches">
            ${tiers.map((t) => html`<div class="flow-node flow-branch">
              <div><span class="tier">${t.n}</span> <span class="t" style="display:inline">${t.name}</span></div>
              <ol>${t.what.map((w) => html`<li>${w}</li>`)}</ol>
              <div class="chips">${t.uses.map((u) => html`<span class="tag tag-accent-2">${u}</span>`)}</div>
              <button class="btn btn-ghost" type="button" data-demo-jump="${t.demo}">Watch it below</button>
            </div>`)}
          </div>
          <div class="flow-arrow">${ARROW}</div>
          <div class="flow-row outputs">
            <div class="flow-node"><span class="k">Referee</span><div class="t">Validates and records</div><p class="d">Blinded first round, two challenges each, every challenge answered, dissent kept.</p><span class="path">memory/council-briefs/</span></div>
            <div class="flow-node"><span class="k">Lifecycle</span><div class="t">Gates and contracts</div><p class="d">Changes count as done only after the gate's checks pass, G0 through G6.</p><span class="path">core/lifecycle/ · contracts/</span></div>
            <div class="flow-node"><span class="k">You</span><div class="t">Review and improve</div><p class="d">Read decisions on the Councils page, then ask for changes. Follow-ups are planned the same way.</p><span class="path">#/councils</span></div>
          </div>
        </div>
      </section>

      <section class="section" aria-labelledby="demo-title" id="demo">
        <h2 id="demo-title">See it respond</h2>
        <p class="section-intro" style="margin-bottom:24px">Pick a request and step through it. Plans are real output from the orchestrator, and council messages come from recorded sessions. Switch the client tab to see how the same request looks in each tool.</p>
        <div class="demo">
          <ul class="scenarios" aria-label="Example requests">
            ${scenarios().map((sc) => html`<li><button class="scenario" type="button" data-demo-scenario="${sc.id}" aria-pressed="${sc.id === currentScenario().id}">
              <span class="name">${sc.label}</span><span class="what">${DEMO_NOTES[sc.id] || ''}</span></button></li>`)}
          </ul>
          <div id="demo-area">${demoWindow()}</div>
        </div>
      </section>

      <section class="section" aria-labelledby="tools-title">
        <h2 id="tools-title">Use it from your tool</h2>
        <p class="section-intro" style="margin-bottom:24px">Set up once per tool. After that, ask in plain words.</p>
        <div class="entry-points">
          ${DATA.entryPoints.map((e) => html`<div class="card"><div class="card-title">${e.label}</div>
            <div class="card-body">${e.how}. Then: <code>${e.example}</code></div>
            <pre class="code" style="font-size:12.5px;padding:14px 16px">${e.setup}</pre>
            <div><button class="btn btn-secondary" type="button" data-copy="${e.setup}">${ICON.copy} Copy setup</button></div></div>`)}
        </div>
      </section>`;
  }

  function refreshDemo(scrollToEnd = true) {
    const area = document.getElementById('demo-area');
    if (!area) return;
    area.innerHTML = fmt(demoWindow());
    document.querySelectorAll('[data-demo-scenario]').forEach((b) => b.setAttribute('aria-pressed', String(b.dataset.demoScenario === currentScenario().id)));
    const log = document.getElementById('demo-log');
    if (log && scrollToEnd) log.scrollTop = log.scrollHeight;
  }

  // Playback timing: about 2.2s per message, longer pauses where a new round starts
  // or the decision lands, so the conversation can be read as it plays.
  const STEP_MS = 2200;
  const PAUSE_AFTER = { divider: 3400, decision: 3200, dissent: 3000, plan: 3000 };
  const reducedMotion = () => matchMedia('(prefers-reduced-motion: reduce)').matches;

  function stopDemo() {
    clearTimeout(demoState.playing);
    demoState.playing = null;
  }

  // Update the buttons and counter without touching the conversation log.
  function syncDemoControls() {
    const total = demoFrames(currentScenario()).length;
    const done = demoState.step >= total;
    const q = (a) => document.querySelector(`[data-demo-action="${a}"]`);
    ['next', 'all'].forEach((a) => { if (q(a)) q(a).disabled = done; });
    const play = q('play');
    if (play) {
      play.disabled = done;
      play.textContent = demoState.playing ? 'Pause' : 'Play';
      play.setAttribute('aria-pressed', String(!!demoState.playing));
    }
    const progress = document.getElementById('demo-progress');
    if (progress) progress.textContent = `${Math.min(demoState.step, total)} / ${total}`;
  }

  // Append the next frame to the log instead of re-rendering the window.
  function appendNextFrame() {
    const frames = demoFrames(currentScenario());
    const log = document.getElementById('demo-log');
    if (!log || demoState.step >= frames.length) return null;
    const frame = frames[demoState.step];
    const nearBottom = log.scrollHeight - log.scrollTop - log.clientHeight < 160;
    const el = document.createElement('div');
    el.className = reducedMotion() ? 'frame' : 'frame frame-enter';
    el.innerHTML = fmt(renderFrame(frame, demoState.client));
    log.appendChild(el);
    demoState.step += 1;
    if (nearBottom || demoState.playing) {
      log.scrollTo({ top: log.scrollHeight, behavior: reducedMotion() ? 'auto' : 'smooth' });
    }
    syncDemoControls();
    return frame;
  }

  function scheduleNext(delay) {
    demoState.playing = setTimeout(() => {
      const frame = appendNextFrame();
      if (!frame || demoState.step >= demoFrames(currentScenario()).length) {
        stopDemo();
        syncDemoControls();
        return;
      }
      scheduleNext(PAUSE_AFTER[frame.type] || STEP_MS);
    }, delay);
  }

  function demoAction(action) {
    const total = demoFrames(currentScenario()).length;
    if (action === 'next') {
      stopDemo();
      appendNextFrame();
    } else if (action === 'all') {
      stopDemo();
      demoState.step = total;
      refreshDemo();
    } else if (action === 'restart') {
      stopDemo();
      demoState.step = 2;
      refreshDemo(false);
    } else if (action === 'play') {
      if (demoState.playing) {
        stopDemo();
        syncDemoControls();
      } else if (reducedMotion()) {
        demoState.step = total;
        refreshDemo();
      } else {
        // Show the first new message right away, then keep the reading pace.
        const frame = appendNextFrame();
        if (frame && demoState.step < total) {
          scheduleNext(PAUSE_AFTER[frame.type] || STEP_MS);
          syncDemoControls();
        }
      }
    }
  }

  function selectScenario(id) {
    stopDemo();
    demoState.scenario = id;
    demoState.step = 2;
    refreshDemo(false);
  }

  async function planCustom(task) {
    demoState.busy = true;
    demoState.error = null;
    refreshDemo(false);
    try {
      const r = await fetch('/api/plan', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ task }) });
      const body = await r.json();
      if (!r.ok) throw new Error(body.error || `The planner returned ${r.status}.`);
      demoState.custom = { id: 'custom', label: 'Your request', turns: [{ task, plan: body }] };
      demoState.scenario = 'custom';
      demoState.step = 2;
    } catch (err) {
      demoState.error = err.message || 'Could not reach the planner.';
    }
    demoState.busy = false;
    if (currentRoute().page === 'how') render();
  }

  // ------------------------------------------------------------------ detail sheets
  const detail = document.getElementById('detail');
  function openDetail(title, body) {
    document.getElementById('detail-title').textContent = title;
    document.getElementById('detail-body').innerHTML = fmt(body);
    detail.showModal();
  }
  const section = (title, content) => html`<div><h3>${title}</h3>${content}</div>`;
  const fileLink = (p) => {
    const url = repoFile(p);
    return html`<p class="muted">${url ? html`<a href="${url}" rel="noopener" target="_blank"><code>${p}</code></a>` : html`<code>${p}</code>`}</p>`;
  };

  function showSkill(id) {
    const s = skillIndex[id];
    if (!s) return;
    if (s.source === 'vendored') {
      openDetail(`/${s.id}`, html`<p>${s.summary}</p>
        ${section('Source', html`<p><a href="${s.repository}" rel="noopener" target="_blank">${s.source}</a> at <code>${s.commit.slice(0, 7)}</code> · ${s.license} · ${s.copyright}</p>`)}
        ${section('Used by', list(s.usedBy.map(personaName)))}
        ${fileLink(s.path)}`);
      return;
    }
    openDetail(`/${s.id}`, html`<p>${s.purpose}</p>
      ${s.gates.length ? html`<div class="chips">${s.gates.map((g) => html`<span class="tag tag-accent">${g}</span>`)}</div>` : ''}
      ${section('When to use it', list(s.whenToUse))}
      ${section('Steps', html`<ol>${s.procedure.map((p) => html`<li><strong>${p.title}.</strong> ${p.action}</li>`)}</ol>`)}
      ${section('What it produces', list(s.outputs))}
      ${section('Done when', list(s.verification))}
      ${fileLink(s.path)}`);
  }

  function showAgent(id) {
    const a = agentIndex[id];
    if (!a) return;
    openDetail(a.name, html`<p>${a.mission}</p>
      ${section('Responsibilities', list(a.responsibilities))}
      ${a.whenToInvoke.length ? section('Call on it when', list(a.whenToInvoke)) : ''}
      ${a.prohibitions.length ? section('It must not', list(a.prohibitions)) : ''}
      ${a.skills.length ? section('Skills', html`<div class="chips">${a.skills.map((k) => html`<span class="tag tag-accent">${k}</span>`)}</div>`) : ''}
      ${fileLink(a.path)}`);
  }

  function showPersona(id) {
    const p = personaIndex[id];
    if (!p) return;
    const skillLabel = (k) => k.replace(/^vendor:/, '').replace(/^ext:/, '') + (k.startsWith('ext:') ? ' (install separately)' : '');
    openDetail(p.title, html`<div class="chips"><span class="tag tag-neutral">${p.councilTitle}</span>${p.role !== 'specialist' ? html`<span class="tag ${p.role === 'chair' ? 'tag-accent' : 'tag-accent-2'}">${p.role}</span>` : ''}</div>
      <p>${p.mission}</p>
      ${p.challengeFocus ? section('Challenges others on', html`<p class="soft">${p.challengeFocus}</p>`) : ''}
      ${section('Questions it asks', list(p.questions))}
      ${p.skills.length ? section('Skills', html`<div class="chips">${p.skills.map((k) => html`<span class="tag tag-accent">${skillLabel(k)}</span>`)}</div>`) : ''}
      ${p.sources.length ? section('Grounded in', list(p.sources)) : ''}
      ${fileLink(p.path)}`);
  }

  // ------------------------------------------------------------------ search
  const searchDialog = document.getElementById('search');
  const searchInput = document.getElementById('search-input');
  const searchResults = document.getElementById('search-results');
  const searchItems = [
    ...Object.values(skillIndex).map((s) => ({ label: `/${s.id}`, kind: 'Skill', text: `${s.id} ${s.name} ${s.purpose}`, run: () => showSkill(s.id) })),
    ...Object.values(personaIndex).map((p) => ({ label: p.title, kind: p.councilTitle, text: `${p.title} ${p.mission}`, run: () => showPersona(p.id) })),
    ...DATA.agents.map((a) => ({ label: a.name, kind: 'Agent', text: `${a.name} ${a.id} ${a.mission}`, run: () => showAgent(a.id) })),
    ...(DATA.sessions || []).map((s) => ({ label: s.task, kind: 'Decision', text: s.task, run: () => { location.hash = `#/councils/${s.brief.decisionId}`; } })),
    { label: 'How it works', kind: 'Page', text: 'how it works flowchart demo orchestrator chat claude code copilot cli terminal', run: () => { location.hash = '#/how'; } },
    ...DATA.gates.map((g) => ({ label: `${g.id} ${g.name}`, kind: 'Gate', text: `${g.id} ${g.name} ${g.description}`, run: () => { location.hash = '#/gates'; } })),
  ];
  let searchMatches = [];
  let searchActive = 0;
  function renderSearch() {
    const q = searchInput.value.toLowerCase().trim();
    searchMatches = (q ? searchItems.filter((i) => i.text.toLowerCase().includes(q)) : searchItems).slice(0, 12);
    searchActive = Math.min(searchActive, Math.max(searchMatches.length - 1, 0));
    searchResults.innerHTML = searchMatches.length
      ? fmt(searchMatches.map((m, i) => html`<li role="presentation"><button type="button" role="option" aria-selected="${i === searchActive}" class="${i === searchActive ? 'active' : ''}" data-result="${i}"><span>${m.label}</span><span class="muted">${m.kind}</span></button></li>`))
      : fmt(html`<li class="muted" style="padding:10px 16px">Nothing matches “${searchInput.value}”.</li>`);
  }
  function openSearch() {
    searchInput.value = '';
    searchActive = 0;
    renderSearch();
    searchDialog.showModal();
    searchInput.focus();
  }
  function chooseResult(i) {
    const m = searchMatches[i];
    if (!m) return;
    searchDialog.close();
    m.run();
  }

  // ------------------------------------------------------------------ advisor
  // A chat that suggests skills, agents and gates for a question. It searches the
  // repository's own skill, agent and gate text in the browser (BM25), says why each
  // result matched and how sure it is, and, when the local server is running, also
  // asks the real orchestrator planner. It never invents files, gates or commands.
  const advisorState = { messages: [], busy: false };
  try {
    const saved = JSON.parse(sessionStorage.getItem('pi-advisor') || 'null');
    if (saved && Array.isArray(saved.messages)) advisorState.messages = saved.messages.slice(-40);
  } catch { /* Storage unavailable: start with an empty conversation. */ }
  function saveAdvisor() {
    try { sessionStorage.setItem('pi-advisor', JSON.stringify({ messages: advisorState.messages.slice(-40) })); } catch { /* ignore */ }
  }

  const ADVISOR_STOP = new Set([
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
  // Filler verbs and nouns that appear in almost any request; matching on them alone
  // produced confident but wrong answers ("add a pricing page" matched an SEO skill).
  const ADVISOR_GENERIC = new Set(['add', 'adding', 'fix', 'fixing', 'make', 'making', 'want', 'need', 'needs',
    'build', 'create', 'write', 'help', 'get', 'use', 'using', 'new', 'please', 'thing', 'things', 'stuff',
    'work', 'working', 'project', 'app', 'code', 'best', 'way', 'good', 'better', 'start']);

  function tokenizeAdvisor(text) {
    if (!text) return [];
    return String(text).toLowerCase().replace(/[^a-z0-9_\-\s]/g, ' ').split(/\s+/)
      .filter((t) => t.length > 1 && !ADVISOR_STOP.has(t) && !ADVISOR_GENERIC.has(t));
  }

  function bm25Retrieve(queryText, topK = 8) {
    const index = DATA.advisorIndex;
    if (!index || !index.docs) return [];
    const qTokens = [...new Set(tokenizeAdvisor(queryText))];
    if (!qTokens.length) return [];
    const k1 = 1.2;
    const b = 0.75;
    const N = index.totalDocs;
    const avgdl = index.avgDocLen || 30;
    const scored = [];
    for (const doc of index.docs) {
      let score = 0;
      const hits = [];
      for (const term of qTokens) {
        const f = doc.tf && doc.tf[term];
        if (!f) continue;
        hits.push(term);
        const df = (index.df && index.df[term]) || 1;
        const idf = Math.log((N - df + 0.5) / (df + 0.5) + 1);
        score += idf * ((f * (k1 + 1)) / (f + k1 * (1 - b + b * (doc.docLen / avgdl))));
      }
      if (score > 0) scored.push({ ...doc, score: Math.round(score * 10) / 10, hits });
    }
    return scored.sort((x, y) => y.score - x.score).slice(0, topK);
  }

  const isSkillDoc = (d) => d.kind === 'skill' || d.kind === 'vendored-skill';
  const firstSentence = (t) => {
    const s = String(t || '').split(/(?<=\.)\s/)[0];
    return s.length > 170 ? s.slice(0, 167).replace(/\s+\S*$/, '') + '…' : s;
  };
  const gateById = (id) => (DATA.gates || []).find((g) => g.id === id);
  function gateInfo(id) {
    const gates = DATA.gates || [];
    const i = gates.findIndex((g) => g.id === id);
    if (i < 0) return null;
    const g = gates[i];
    const next = gates[i + 1];
    return { id: g.id, name: g.name, contract: g.contract ? g.contract.path : null, next: next ? `${next.id} · ${next.name}` : null };
  }

  // Confidence: the best skill must score well on real topic words and clearly beat
  // the next skill. Otherwise the answer says it is unsure and shows the closest matches.
  function adviseFromSearch(query) {
    const matches = bm25Retrieve(query);
    const skills = matches.filter(isSkillDoc);
    const agent = matches.find((m) => m.kind === 'agent');
    const top = skills[0];
    const next = skills[1];
    const margin = top && next ? (top.score - next.score) / top.score : 1;
    // Confident when the best skill scores well and clearly leads, or when it matches
    // many distinct topic words and still leads.
    const confident = !!top && top.score >= 8 && (margin >= 0.3 || (top.hits.length >= 4 && margin >= 0.1));
    const gate = top && top.gates && top.gates.length ? gateInfo(top.gates[0]) : null;
    return { query, confident, top, others: skills.slice(1, 3), agent, gate };
  }

  const SETUP_RX = /\b(set ?up|install(ation)?|initiali[sz]e|get(ting)? started|how (do i|to) (use|install|start))\b/i;
  const STEPS_RX = /^(?:what are the )?steps for \/([a-z0-9-]+)\??$/i;
  const NEXT_GATE_RX = /^what comes after (G[0-6])\??$/i;

  async function handleAdvisorSubmit(text) {
    const q = (text || '').trim();
    if (!q || advisorState.busy) return;
    advisorState.messages.push({ role: 'user', text: q });
    let reply;
    const steps = q.match(STEPS_RX);
    const nextGate = q.match(NEXT_GATE_RX);
    if (steps) reply = { kind: 'steps', skillId: steps[1].toLowerCase() };
    else if (nextGate) reply = { kind: 'gate', gateId: nextGate[1].toUpperCase() };
    else if (SETUP_RX.test(q)) reply = { kind: 'setup' };
    else reply = { kind: 'advice', ...adviseFromSearch(q) };
    advisorState.messages.push({ role: 'assistant', reply });
    saveAdvisor();
    if (currentRoute().page !== 'advisor') location.hash = '#/advisor';
    if (reply.kind === 'advice' && state.server) {
      advisorState.busy = true;
      refreshAdvisor();
      try {
        const r = await fetch('/api/plan', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ task: q }) });
        if (r.ok) reply.plan = await r.json();
      } catch { /* The planner is optional; search results still stand. */ }
      advisorState.busy = false;
      saveAdvisor();
    }
    refreshAdvisor();
  }

  // Slash commands are typed into the coding agent, not a terminal, so they get their
  // own style without a "$" prompt. The plugin namespaces them; `init` installs them bare.
  function slashCommand(id) {
    const text = `/project-intelligence:${id}`;
    return html`<div class="slash"><span class="slash-label">Claude Code</span><code>${text}</code>
      <button class="btn btn-secondary btn-sm" type="button" data-copy="${text}" aria-label="Copy ${text}">Copy</button></div>`;
  }

  function copyTextOf(reply) {
    if (reply.kind !== 'advice') return '';
    const lines = [];
    if (reply.plan) lines.push(`Planner: tier ${reply.plan.tier} (${reply.plan.tierName}). ${reply.plan.steps.map((s) => s.text).join(' ')}`);
    if (reply.top) lines.push(`${reply.confident ? 'Best match' : 'Closest match'}: /project-intelligence:${reply.top.id}. ${firstSentence(reply.top.summary)}`);
    reply.others.forEach((o) => lines.push(`Also: /project-intelligence:${o.id}`));
    if (reply.gate) lines.push(`Gate ${reply.gate.id} · ${reply.gate.name}${reply.gate.contract ? ` (${reply.gate.contract})` : ''}`);
    lines.push(`Plan it: ${DATA.install.run} ask "${reply.query}"`);
    return lines.join('\n');
  }

  function followUps(reply) {
    const chips = [];
    if (reply.top) chips.push(`Steps for /${reply.top.id}`);
    if (reply.gate) chips.push(`What comes after ${reply.gate.id}?`);
    return chips;
  }

  function renderAdvisorReply(reply, index) {
    if (reply.kind === 'setup') {
      return html`<p>Pick your tool and run its command once in your project folder.</p>
        <div class="advisor-setup">
          <div><strong>Claude Code</strong> (plugin)<div class="cmd-stack">${cmd(DATA.install.plugin.add)}${cmd(DATA.install.plugin.install)}</div></div>
          <div><strong>GitHub Copilot CLI</strong> (MCP server)${cmd(`copilot mcp add project-intelligence -- ${DATA.install.run} mcp`)}</div>
          <div><strong>Antigravity or any terminal</strong>${cmd(DATA.install.init)}</div>
        </div>
        <p class="muted">Check the setup any time with <code>${DATA.install.doctor}</code>. More on the <a href="#/install">Install page</a>.</p>`;
    }
    if (reply.kind === 'steps') {
      const s = skillIndex[reply.skillId];
      if (!s) return html`<p>There is no skill called <code>/${reply.skillId}</code>. Search the <a href="#/skills">Skills page</a>.</p>`;
      const steps = s.procedure || [];
      return html`<p><strong>/${s.id}</strong>: ${firstSentence(s.purpose)}</p>
        ${steps.length ? html`<ol class="advisor-steps">${steps.map((p) => html`<li><strong>${p.title}.</strong> ${p.action}</li>`)}</ol>`
          : html`<p class="muted">This third-party skill describes its steps in its own file. <button class="btn btn-ghost btn-sm" type="button" data-skill="${s.id}">Open it</button></p>`}
        ${slashCommand(s.id)}`;
    }
    if (reply.kind === 'gate') {
      const g = gateInfo(reply.gateId);
      if (!g) return html`<p>Gates run from G0 to G6.</p>`;
      if (!g.next) return html`<p>${g.id} · ${g.name} is the last gate. After it, the work is released and handed off.</p>`;
      const nextId = g.next.split(' ')[0];
      const ng = gateById(nextId);
      return html`<p>After <strong>${g.id} · ${g.name}</strong> comes <strong>${g.next}</strong>: ${ng ? ng.description : ''}</p>
        ${ng && ng.contract ? html`<p class="muted">It needs an approved contract in <code>${ng.contract.path}</code>.</p>` : ''}`;
    }
    // Search-based advice, optionally led by the real planner.
    const { top, others, agent, gate, confident, plan } = reply;
    // Show the planner only when it routes the work somewhere (tier 1 or higher).
    const planBlock = plan && plan.tier > 0 ? html`<div class="advisor-plan">
        <span class="advisor-label">The orchestrator would</span>
        <p>${plan.steps.length ? plan.steps[0].text : ''} <span class="muted">(tier ${plan.tier} · ${plan.tierName}${plan.confidence === 'low' ? ', low confidence: confirm before acting' : ''})</span></p>
      </div>` : '';
    if (!top) {
      return html`${planBlock}<p>Nothing in the skills or agents clearly matches that. Try naming the area (for example database, API, design tokens, security, testing), or let the orchestrator plan it:</p>
        ${cmd(`${DATA.install.run} ask "${reply.query.slice(0, 120)}"`)}`;
    }
    return html`
      ${planBlock}
      <p>${confident
        ? html`<strong>Best match: /${top.id}.</strong> ${firstSentence(top.summary)}`
        : html`<strong>I'm not sure.</strong> The closest match is <strong>/${top.id}</strong>: ${firstSentence(top.summary)}`}</p>
      <p class="advisor-why">Matched on: ${top.hits.join(', ')}${confident ? '' : '. Add a detail or two for a clearer answer.'}</p>
      ${slashCommand(top.id)}
      ${(others.length || agent || gate) ? html`<details class="advisor-more"><summary>More detail</summary>
        ${others.length ? html`<p><span class="advisor-label">Also relevant</span></p><ul>${others.map((o) => html`<li><button class="linklike" type="button" data-skill="${o.id}">/${o.id}</button>: ${firstSentence(o.summary)}</li>`)}</ul>` : ''}
        ${agent ? html`<p><span class="advisor-label">Specialist</span> ${agent.name}</p>` : ''}
        ${gate ? html`<p><span class="advisor-label">Lifecycle gate</span> ${gate.id} · ${gate.name}${gate.contract ? html`, contract <code>${gate.contract}</code>` : ''}${gate.next ? `. Next: ${gate.next}.` : '.'}</p>` : ''}
        <p><span class="advisor-label">Plan it in a terminal</span></p>${cmd(`${DATA.install.run} ask "${reply.query.slice(0, 120)}"`)}
      </details>` : ''}
      <div class="advisor-actions">
        ${followUps(reply).map((f) => html`<button class="chip" type="button" data-advisor-prompt="${f}">${f}</button>`)}
        <button class="btn btn-ghost btn-sm" type="button" data-copy="${copyTextOf(reply)}">Copy answer</button>
        <button class="btn btn-ghost btn-sm" type="button" data-skill="${top.id}">View steps</button>
      </div>`;
  }

  function renderAdvisorMessage(m, i) {
    if (m.role === 'user') return html`<div class="advisor-msg user"><p>${m.text}</p></div>`;
    return html`<div class="advisor-msg assistant">${renderAdvisorReply(m.reply, i)}</div>`;
  }

  const ADVISOR_STARTERS = [
    ['Document a legacy codebase', 'We have an unmaintained legacy codebase with raw SQL and want to document the domain entities before modernizing.'],
    ['Migrate a database safely', 'Migrate our database schema without downtime, with a rollback.'],
    ['Design tokens and type scale', 'Set up design tokens, a typography scale and WCAG AA contrast for our UI.'],
    ['Audit for secrets and injection', 'Security audit for hardcoded secrets and injection vulnerabilities.'],
    ['Keep the API in sync', 'Keep our OpenAPI contract in sync with server routes and catch breaking changes.'],
    ['Turn an idea into a PRD', 'We have a rough feature idea and need a PRD with user stories.'],
    ['How do I install it?', 'How do I install it?'],
  ];

  function advisorConversation() {
    if (!advisorState.messages.length) {
      return html`<div class="advisor-empty">
        <p><strong>Ask what to use for your project.</strong> Describe the problem or the area you are working in, and the advisor suggests the skill, specialist and lifecycle gate that fit.</p>
        <div class="chips">${ADVISOR_STARTERS.map(([label, prompt]) => html`<button class="chip" type="button" data-advisor-prompt="${prompt}">${label}</button>`)}</div>
      </div>`;
    }
    return html`${advisorState.messages.map(renderAdvisorMessage)}
      ${advisorState.busy ? html`<div class="advisor-msg assistant typing" aria-label="Thinking"><span></span><span></span><span></span></div>` : ''}`;
  }

  function advisorPage() {
    return html`
      <section class="section advisor-page" aria-labelledby="advisor-title">
        <div class="advisor-head">
          <div>
            <h1 id="advisor-title">Advisor</h1>
            <p class="soft">Answers come from the ${DATA.skills.length + DATA.vendored.length} skills, ${DATA.agents.length} agents and ${DATA.gates.length} gates in this project, searched in your browser. ${state.server ? 'The local orchestrator also plans each question.' : 'Nothing you type leaves your browser.'}</p>
          </div>
          ${advisorState.messages.length ? html`<button class="btn btn-secondary btn-sm" type="button" data-advisor-action="new">New conversation</button>` : ''}
        </div>
        <div class="advisor-messages" id="advisor-messages" role="log" aria-live="polite" aria-label="Conversation">${advisorConversation()}</div>
        <form class="advisor-composer" id="advisor-form">
          <label class="visually-hidden" for="advisor-input">Your question</label>
          <textarea class="input advisor-input" id="advisor-input" rows="1" placeholder="Describe what you are working on…" required></textarea>
          <button class="btn btn-primary" id="advisor-submit" type="submit" ${advisorState.busy ? raw('disabled') : ''}>Send</button>
          <span class="advisor-hint muted">Enter to send, Shift+Enter for a new line</span>
        </form>
      </section>
    `;
  }

  // Update only the conversation, keeping the text box and its focus.
  function refreshAdvisor() {
    const log = document.getElementById('advisor-messages');
    if (!log) return;
    log.innerHTML = fmt(advisorConversation());
    const head = document.querySelector('.advisor-head');
    if (head) head.outerHTML = fmt(html`<div class="advisor-head">${raw(head.firstElementChild.outerHTML)}
      ${advisorState.messages.length ? html`<button class="btn btn-secondary btn-sm" type="button" data-advisor-action="new">New conversation</button>` : ''}</div>`);
    const send = document.getElementById('advisor-submit');
    if (send) send.disabled = advisorState.busy;
    const last = log.lastElementChild;
    if (last) last.scrollIntoView({ block: 'nearest', behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth' });
  }

  // ------------------------------------------------------------------ routing
  const ROUTES = { skills: skillsPage, advisor: advisorPage, how: howPage, councils: councilsPage, agents: agentsPage, gates: gatesPage, install: installPage };
  const TITLES = { skills: 'Skills', advisor: 'Advisor', how: 'How it works', councils: 'Councils', agents: 'Agents', gates: 'Gates', install: 'Install' };

  function currentRoute() {
    const parts = location.hash.replace(/^#\/?/, '').split('/').filter(Boolean);
    const page = ROUTES[parts[0]] ? parts[0] : 'skills';
    return { page, sub: page === 'councils' ? parts[1] : null };
  }

  function render(opts = {}) {
    const { page, sub } = currentRoute();
    if (page !== 'how') stopDemo();
    main.innerHTML = fmt(sub ? sessionPage(sub) : ROUTES[page]());
    document.querySelectorAll('[data-route]').forEach((a) => {
      if (a.dataset.route === page) a.setAttribute('aria-current', 'page');
      else a.removeAttribute('aria-current');
    });
    document.title = `${sub && sessionIndex[sub] ? sessionIndex[sub].task : TITLES[page]} · Project Intelligence`;
    if (opts.navigated && !state.firstRender) {
      window.scrollTo(0, 0);
      main.focus({ preventScroll: true });
    }
    state.firstRender = false;
  }

  const AUTHOR = {
    name: 'Sahas Belbase',
    links: [
      { label: 'GitHub', href: 'https://github.com/sahasbelbase' },
      { label: 'LinkedIn', href: 'https://www.linkedin.com/in/sahas-belbase/' },
      { label: 'Portfolio', href: 'https://sahas.netlify.app/' },
    ],
    projects: [
      { label: 'JustTalk', href: 'https://sahasbelbase.github.io/JustTalk' },
      { label: 'MacNotch', href: 'https://sahasbelbase.github.io/MacNotch/' },
      { label: 'JSON Converter', href: 'https://jsonconverter-dev.vercel.app/' },
      { label: 'Movie Recommendation', href: 'https://movierecommendation.pages.dev/' },
    ],
  };

  function renderFooter() {
    const m = DATA.meta;
    const ext = (l) => html`<li><a href="${l.href}" target="_blank" rel="noopener">${l.label}</a></li>`;
    document.getElementById('site-footer').innerHTML = fmt(html`
      <div class="footer-grid">
        <div>
          <div class="footer-brand">Project Intelligence</div>
          <p class="muted">Made by ${AUTHOR.name}.</p>
        </div>
        <nav aria-label="${AUTHOR.name}">
          <h2 class="footer-head">Find me</h2>
          <ul class="footer-links">${AUTHOR.links.map(ext)}</ul>
        </nav>
        <nav aria-label="Other projects">
          <h2 class="footer-head">Other projects</h2>
          <ul class="footer-links">${AUTHOR.projects.map(ext)}</ul>
        </nav>
      </div>
      <div class="footer-meta">
        <span>v${m.version} · ${m.license}</span>
      </div>`);
    const gh = document.getElementById('github-link');
    if (DATA.install.repoUrl) { gh.href = DATA.install.repoUrl; gh.target = '_blank'; gh.rel = 'noopener'; }
  }

  // ------------------------------------------------------------------ events
  function copyText(btn, text) {
    const done = (label) => {
      const original = btn.dataset.label || btn.innerHTML;
      btn.dataset.label = original;
      btn.textContent = label;
      clearTimeout(btn._t);
      btn._t = setTimeout(() => { btn.innerHTML = original; }, 1500);
    };
    if (navigator.clipboard && navigator.clipboard.writeText) {
      navigator.clipboard.writeText(text).then(() => done('Copied'), () => done('Copy failed'));
    } else {
      done('Copy failed');
    }
  }

  document.addEventListener('click', (e) => {
    const t = e.target.closest('[data-copy],[data-skill],[data-agent],[data-persona],[data-client],[data-agent-group],[data-scroll],[data-close],[data-result],[data-demo-action],[data-demo-scenario],[data-demo-client],[data-demo-jump],[data-advisor-prompt],[data-advisor-action],#audit-run,#theme-toggle');
    if (!t) return;
    if (t.dataset.copy !== undefined) copyText(t, t.dataset.copy);
    else if (t.dataset.skill) showSkill(t.dataset.skill);
    else if (t.dataset.agent) showAgent(t.dataset.agent);
    else if (t.dataset.persona) showPersona(t.dataset.persona);
    else if (t.dataset.advisorPrompt) handleAdvisorSubmit(t.dataset.advisorPrompt);
    else if (t.dataset.advisorAction === 'new') {
      advisorState.messages = [];
      saveAdvisor();
      render();
      const input = document.getElementById('advisor-input');
      if (input) input.focus();
    }
    else if (t.dataset.client) { state.client = t.dataset.client; render(); document.getElementById(`tab-${state.client}`).focus(); }
    else if (t.dataset.agentGroup) { state.agentGroup = t.dataset.agentGroup; render(); }
    else if (t.dataset.scroll) { e.preventDefault(); document.getElementById(t.dataset.scroll).scrollIntoView(); }
    else if (t.dataset.close !== undefined) t.closest('dialog').close();
    else if (t.dataset.result) chooseResult(Number(t.dataset.result));
    else if (t.dataset.demoAction) demoAction(t.dataset.demoAction);
    else if (t.dataset.demoScenario) selectScenario(t.dataset.demoScenario);
    else if (t.dataset.demoClient) { demoState.client = t.dataset.demoClient; refreshDemo(false); document.querySelector(`[data-demo-client="${demoState.client}"]`).focus(); }
    else if (t.dataset.demoJump) { selectScenario(t.dataset.demoJump); document.getElementById('demo').scrollIntoView(); }
    else if (t.id === 'audit-run') runAudit();
    else if (t.id === 'theme-toggle') toggleTheme();
  });

  document.addEventListener('submit', (e) => {
    if (e.target.id === 'demo-form') {
      e.preventDefault();
      const task = (new FormData(e.target).get('task') || '').toString().trim();
      if (task) planCustom(task);
      return;
    }
    if (e.target.id === 'advisor-form') {
      e.preventDefault();
      const inputEl = e.target.querySelector('#advisor-input') || document.getElementById('advisor-input');
      const text = (inputEl && inputEl.value || '').toString().trim();
      if (text) {
        if (inputEl) inputEl.value = '';
        handleAdvisorSubmit(text);
      }
      return;
    }
  });

  document.addEventListener('input', (e) => {
    if (e.target && e.target.id === 'advisor-input') {
      e.target.style.height = 'auto';
      e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
    }
  });

  document.addEventListener('keydown', (e) => {
    if (e.target && e.target.id === 'advisor-input' && e.key === 'Enter' && !e.shiftKey && !e.isComposing) {
      e.preventDefault();
      const text = e.target.value.trim();
      if (text) {
        e.target.value = '';
        handleAdvisorSubmit(text);
      }
    }
  });

  // ------------------------------------------------------------------ theme
  const themeBtn = document.getElementById('theme-toggle');
  const darkQuery = matchMedia('(prefers-color-scheme: dark)');
  const effectiveTheme = () => document.documentElement.dataset.theme || (darkQuery.matches ? 'dark' : 'light');
  function syncTheme() {
    const t = effectiveTheme();
    document.documentElement.dataset.themeEffective = t;
    themeBtn.setAttribute('aria-label', t === 'dark' ? 'Switch to light theme' : 'Switch to dark theme');
  }
  function toggleTheme() {
    const next = effectiveTheme() === 'dark' ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    try { localStorage.setItem('pi-theme', next); } catch { /* Private mode: the choice lasts for this page only. */ }
    syncTheme();
  }
  darkQuery.addEventListener('change', syncTheme);
  syncTheme();

  document.addEventListener('input', (e) => {
    if (e.target.id === 'agent-search') {
      state.agentQuery = e.target.value;
      const pos = e.target.selectionStart;
      render();
      const input = document.getElementById('agent-search');
      input.focus();
      input.setSelectionRange(pos, pos);
    } else if (e.target.id === 'audit-code') {
      state.auditCode = e.target.value;
    } else if (e.target === searchInput) {
      searchActive = 0;
      renderSearch();
    }
  });

  searchInput.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
      e.preventDefault();
      const n = searchMatches.length;
      if (!n) return;
      searchActive = (searchActive + (e.key === 'ArrowDown' ? 1 : n - 1)) % n;
      renderSearch();
    } else if (e.key === 'Enter') {
      e.preventDefault();
      chooseResult(searchActive);
    }
  });

  [detail, searchDialog].filter(Boolean).forEach((d) => d.addEventListener('click', (e) => { if (e.target === d) d.close(); }));

  // Shortcut hints match the visitor's OS: the Command key on Apple devices, Ctrl elsewhere.
  const isApple = /mac|iphone|ipad/i.test((navigator.userAgentData && navigator.userAgentData.platform) || navigator.platform || navigator.userAgent || '');
  document.querySelectorAll('kbd[data-shortcut]').forEach((k) => { k.textContent = `${isApple ? '⌘' : 'Ctrl '}${k.dataset.shortcut}`; });

  function openAdvisor() {
    if (currentRoute().page === 'advisor') {
      const input = document.getElementById('advisor-input');
      if (input) { input.focus(); input.scrollIntoView({ block: 'center' }); }
    } else {
      location.hash = '#/advisor';
    }
  }

  window.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'k') {
      e.preventDefault();
      if (searchDialog.open) searchDialog.close(); else openSearch();
    } else if ((e.metaKey || e.ctrlKey) && e.key.toLowerCase() === 'j') {
      e.preventDefault();
      openAdvisor();
    }
  });
  document.getElementById('search-open').addEventListener('click', openSearch);
  const advisorOpenBtn = document.getElementById('advisor-open');
  if (advisorOpenBtn) {
    advisorOpenBtn.addEventListener('click', (e) => {
      e.preventDefault();
      openAdvisor();
    });
  }

  const menuBtn = document.getElementById('menu-btn');
  const navLinks = document.getElementById('nav-links');
  menuBtn.addEventListener('click', () => {
    const open = navLinks.classList.toggle('open');
    menuBtn.setAttribute('aria-expanded', String(open));
  });
  navLinks.addEventListener('click', (e) => {
    if (e.target.closest('a')) { navLinks.classList.remove('open'); menuBtn.setAttribute('aria-expanded', 'false'); }
  });

  const header = document.getElementById('site-header');
  window.addEventListener('scroll', () => header.classList.toggle('scrolled', window.scrollY > 4), { passive: true });
  window.addEventListener('hashchange', () => render({ navigated: true }));

  async function runAudit() {
    try {
      const r = await fetch('/api/audit', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ code: state.auditCode }) });
      state.auditResult = r.ok ? await r.json() : { error: `The checker returned ${r.status}.` };
    } catch {
      state.auditResult = { error: 'Could not reach the local server.' };
    }
    render();
  }

  async function detectServer() {
    if (location.protocol === 'file:') return;
    try {
      const r = await fetch('/api/status');
      if (!r.ok) return;
      const s = await r.json();
      state.server = { commit: s.downloadsCommit || null };
      render();
    } catch {
      /* Static hosting: the site works without the local API; downloads and the checker stay hidden. */
    }
  }

  renderFooter();
  render();
  detectServer();
})();
