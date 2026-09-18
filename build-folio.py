#!/usr/bin/env python3
"""Build the Index Folio index.html from measured data.

Data: /tmp/folio-data/assembled.json (GitHub repo statistics, measured 2026-09-18)
plus live content counts verified the same day.
Every visualization answers one question; every mark passes the data-ink test.
"""
import json, datetime

D = json.load(open('/tmp/folio-data/assembled.json'))

META = {
 'portfolio':      dict(folio='01', name='Portfolio', slug='portfolio',
   url='https://dillingerstaffing.github.io/portfolio/',
   evidence='Proof cards across five layers (ISA, microarch, firmware, kernel, algorithm); a blog that teaches one atomic idea per post; a curated reading wire. New Proving Ground benches graduate into portfolio proof cards.'),
 'proving-ground': dict(folio='02', name='Proving Ground', slug='proving-ground',
   url='https://dillingerstaffing.github.io/proving-ground/',
   evidence='Seventy-two interactive benches across computer architecture, analog and power electronics, and bench craft, one per day.'),
 'notebook':       dict(folio='03', name='Notebook', slug='notebook',
   url='https://dillingerstaffing.github.io/notebook/',
   evidence='The complete language: material grammar, composition grammar, nine reusable patterns, information flow, the quality gate, and the build audit.'),
 'ghostlight':     dict(folio='04', name='GHOSTLIGHT', slug='ghostlight',
   url='https://dillingerstaffing.github.io/ghostlight/',
   evidence='Walkthroughs GH-001 through GH-010 with real screen recordings, mapped to MITRE ATT&CK TA0005 and D3FEND defenders.'),
 'wigmore':        dict(folio='05', name='Wigmore', slug='wigmore',
   url='https://dillingerstaffing.github.io/wigmore/',
   evidence='A chart builder with strict Wigmore schema validation, a built-in example, and a localStorage collection.'),
 'old-iron':       dict(folio='06', name='OLD IRON', slug='old-iron',
   url='https://dillingerstaffing.github.io/old-iron/',
   evidence='A terse service page: what is picked up, how wiping is certified per serial, how logistics are insured.'),
 'tapeout':        dict(folio='07', name='TAPEOUT', slug='tapeout',
   url='https://dillingerstaffing.github.io/tapeout/',
   evidence='A lean distribution page with no fake inventory, plus an open lab log of real progress.'),
 'unstuck':        dict(folio='08', name='UNSTUCK', slug='unstuck',
   url='https://dillingerstaffing.github.io/unstuck/',
   evidence='A one-page card: a plain-language fix list, a three-step process, tap-to-call.'),
 'signs':          dict(folio='09', name='Signs', slug='signs',
   url='https://dillingerstaffing.github.io/signs/',
   evidence="An experimental text-to-semiotics instrument using Peirce's own terms throughout."),
}

CONTENT = {
 'portfolio': (187, 'projects', '37 articles'), 'proving-ground': (72, 'benches', 'one per day'),
 'notebook': (9, 'patterns', 'the reusable nine'), 'ghostlight': (10, 'walkthroughs', 'GH-001 to GH-010'),
 'wigmore': (1, 'chart builder', 'strict schema'), 'old-iron': (1, 'service page', 'pickup and wiping'),
 'tapeout': (1, 'service page', 'open lab log'), 'unstuck': (1, 'service page', 'plain words'),
 'signs': (1, 'instrument', 'text to semiotics'),
}

sites = []
for slug, m in META.items():
    d = D[slug]
    n, unit, note = CONTENT[slug]
    sites.append(dict(
        folio=m['folio'], name=m['name'], slug=slug, url=m['url'], evidence=m['evidence'],
        weekly=d['weekly'], daily=d['daily28'], dow=d['dow'], c28=d['c28'],
        repo_kb=d['repo_kb'], page_kb=d['page_kb'], pushed=d['pushed'],
        content_n=n, content_unit=unit, content_note=note,
    ))

sites.sort(key=lambda s: s['folio'])
DATA_DATE = '2026-09-18T20:17:04Z'
data_js = json.dumps(sites, separators=(',', ':'))

# verdict facts
tot28 = sum(s['c28'] for s in sites)
top_active = max(sites, key=lambda s: sum(1 for v in s['daily'] if v > 0))
top_active_n = sum(1 for v in top_active['daily'] if v > 0)
wkday = sum(sum(s['dow'][1:6]) for s in sites)
wkend = sum(s['dow'][0] + s['dow'][6] for s in sites)
wk_pct = round(100 * wkday / (wkday + wkend))
top2 = sorted(sites, key=lambda s: -s['c28'])[:2]
top2_pct = round(100 * sum(s['c28'] for s in top2) / tot28)
top_content = max(sites, key=lambda s: s['content_n'])

html = '''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, user-scalable=no, viewport-fit=cover" />
  <meta name="color-scheme" content="light dark" />
  <meta name="theme-color" content="#e9e3d5" media="(prefers-color-scheme: light)" />
  <meta name="theme-color" content="#171815" media="(prefers-color-scheme: dark)" />
  <link rel="icon" href="icon.svg" type="image/svg+xml" />
  <link rel="icon" href="icon-192.png" type="image/png" sizes="192x192" />
  <link rel="apple-touch-icon" href="apple-touch-icon.png" />
  <link rel="manifest" href="manifest.json" />
  <title>The Index Folio, Chris Dillinger</title>
  <meta name="description" content="One page indexing every working site by Chris Dillinger: the RISC-V and kernel portfolio, the Proving Ground benches, GHOSTLIGHT red-team walkthroughs, Wigmore evidence charts, OLD IRON hardware retirement, TAPEOUT lean compute parts, UNSTUCK plain-words computer help, Signs semiotics, and the Notebook design language." />
  <link rel="canonical" href="https://dillingerstaffing.github.io/" />
  <meta property="og:title" content="The Index Folio, Chris Dillinger" />
  <meta property="og:description" content="Nine working sites on one page." />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="https://dillingerstaffing.github.io/" />
  <meta property="og:image" content="https://dillingerstaffing.github.io/og-image.png" />
  <meta property="og:image:width" content="1200" />
  <meta property="og:image:height" content="630" />
  <meta property="og:image:alt" content="The Index Folio: nine working sites, each with a one-line reason to visit." />
  <meta property="og:site_name" content="The Index Folio" />
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="The Index Folio, Chris Dillinger" />
  <meta name="twitter:description" content="Nine working sites on one page." />
  <meta name="twitter:image" content="https://dillingerstaffing.github.io/og-image.png" />
  <meta name="twitter:image:alt" content="The Index Folio: nine working sites, each with a one-line reason to visit." />
  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "WebSite",
    "name": "The Index Folio",
    "url": "https://dillingerstaffing.github.io/",
    "description": "One page indexing every working site by Chris Dillinger.",
    "author": { "@type": "Person", "name": "Chris Dillinger" },
    "inLanguage": "en"
  }
  </script>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Crimson+Pro:ital,wght@0,400;0,520;0,650;1,400&family=IBM+Plex+Mono:wght@400;500&display=swap');

    :root {
      color-scheme: light dark;
      --paper: #e9e3d5;
      --paper-deep: #d8cfbd;
      --paper-soft: #f2ede1;
      --ink: #1d1c18;
      --ink-soft: #5d574c;
      --hairline: #a59b87;
      --ghost: rgba(29, 28, 24, .085);
      --sanguine: #8b3e2f;
      --sanguine-soft: rgba(139, 62, 47, .11);
      --graphite: #465153;
      --wash: rgba(255, 255, 255, .2);
      --focus: #115d68;
      --font-reading: "Crimson Pro", Georgia, serif;
      --font-technical: "IBM Plex Mono", "Courier New", monospace;
    }
    @media (prefers-color-scheme: dark) {
      :root {
        --paper: #171815;
        --paper-deep: #20211d;
        --paper-soft: #1d1e1a;
        --ink: #ece6d8;
        --ink-soft: #b8b09f;
        --hairline: #625c50;
        --ghost: rgba(255, 255, 255, .065);
        --sanguine: #d17d69;
        --sanguine-soft: rgba(209, 125, 105, .13);
        --graphite: #aab8b8;
        --wash: rgba(255, 255, 255, .025);
        --focus: #8fcbd2;
      }
    }
    * { box-sizing: border-box; }
    html, body { margin: 0; min-width: 0; overflow-x: clip; }
    html { background: var(--paper-deep); scroll-behavior: smooth; }
    body {
      background: var(--paper);
      color: var(--ink);
      font-family: var(--font-reading);
      font-size: 19px;
      line-height: 1.48;
      text-rendering: optimizeLegibility;
      -webkit-font-smoothing: antialiased;
    }
    button, a { -webkit-tap-highlight-color: transparent; }
    button { font: inherit; }
    a { color: inherit; text-decoration-color: var(--sanguine); text-underline-offset: .18em; }
    a:hover { color: var(--sanguine); }
    :focus-visible { outline: 2px solid var(--focus); outline-offset: 4px; }

    .folio {
      width: min(1180px, 100%);
      margin: 0 auto;
      min-height: 100vh;
      padding: clamp(24px, 5vw, 72px) clamp(18px, 5vw, 78px) 96px;
      position: relative;
      background: linear-gradient(90deg, transparent 0, transparent calc(100% - 1px), var(--ghost) calc(100% - 1px));
    }
    .folio::before {
      content: "";
      position: absolute;
      left: clamp(7px, 2vw, 24px);
      top: 0; bottom: 0; width: 1px;
      background: var(--ghost);
      pointer-events: none;
    }
    .stamp, .kicker, .mono {
      font-family: var(--font-technical);
      letter-spacing: .055em;
      text-transform: uppercase;
    }

    .opening {
      min-height: min(52vh, 520px);
      padding: 5vh 0 56px;
      border-bottom: 1px solid var(--hairline);
    }
    .stamp { color: var(--sanguine); font-size: 11px; margin: 0 0 26px; }
    h1 {
      font-size: clamp(46px, 8.7vw, 112px);
      font-weight: 400; letter-spacing: -.055em; line-height: .84;
      margin: 0; max-width: 850px;
    }
    h1 em { color: var(--sanguine); font-weight: 400; }

    .section { padding: 72px 0; border-bottom: 1px solid var(--hairline); }
    .kicker { font-size: 11px; color: var(--sanguine); margin: 0 0 12px; }
    h2 { margin: 0 0 26px; font-size: clamp(35px, 5.2vw, 64px); line-height: .95; font-weight: 400; letter-spacing: -.035em; }
    h3 { font-size: 26px; line-height: 1.08; margin: 0 0 8px; font-weight: 520; }
    p { margin: 0 0 1em; }
    .quiet { color: var(--ink-soft); }

    .control-label { font: 10px/1.4 var(--font-technical); text-transform: uppercase; letter-spacing: .055em; color: var(--ink-soft); margin: 30px 0 0; }
    .control-row { display: flex; gap: 6px; flex-wrap: wrap; margin: 8px 0 0; }
    .control {
      border: 1px solid var(--hairline);
      border-radius: 0;
      background: transparent;
      color: var(--ink-soft);
      padding: 10px 12px;
      font: 500 11px/1 var(--font-technical);
      text-transform: uppercase;
      letter-spacing: .055em;
      cursor: pointer;
    }
    .control[aria-pressed="true"] { color: var(--ink); border-color: var(--sanguine); background: var(--sanguine-soft); }

    .field-wrap { margin-top: 26px; border-top: 1px solid var(--hairline); border-bottom: 1px solid var(--hairline); background: var(--wash); }
    #field { display: block; width: 100%; height: auto; }
    .verdict-line { font-size: clamp(20px, 2.4vw, 27px); line-height: 1.3; margin: 18px 0 0; max-width: 46rem; }
    .verdict-line .m { font-family: var(--font-technical); font-size: .72em; color: var(--sanguine); letter-spacing: .02em; }
    .key-line { font: 10px/1.6 var(--font-technical); text-transform: uppercase; letter-spacing: .05em; color: var(--ink-soft); margin: 14px 0 0; }

    .chart { margin-top: 30px; border-top: 1px solid var(--hairline); }
    .crow {
      display: grid;
      grid-template-columns: 158px minmax(0, 1fr) 150px;
      gap: 12px; align-items: center;
      padding: 9px 0;
      border-bottom: 1px solid var(--ghost);
    }
    .crow .cname { font: 500 11px/1.3 var(--font-technical); text-transform: uppercase; letter-spacing: .05em; }
    .crow .cname a { text-decoration: none; }
    .crow .cbar { height: 18px; position: relative; min-width: 0; }
    .crow .cbar i { display: block; height: 100%; background: var(--sanguine); min-width: 2px; }
    .crow .cval { font: 11px/1.3 var(--font-technical); color: var(--ink-soft); text-align: right; }

    .mults { margin-top: 30px; display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 0; border-top: 1px solid var(--hairline); border-left: 1px solid var(--hairline); }
    .mult { border-right: 1px solid var(--hairline); border-bottom: 1px solid var(--hairline); padding: 14px 14px 12px; min-width: 0; }
    .mult .mname { font: 500 10px/1.3 var(--font-technical); text-transform: uppercase; letter-spacing: .05em; margin: 0 0 8px; }
    .mult .mname a { text-decoration: none; }
    .wbars { display: flex; align-items: flex-end; gap: 3px; height: 44px; }
    .wbars i { flex: 1 1 0; background: var(--sanguine); min-width: 0; }
    .dowlabels { display: flex; gap: 3px; margin-top: 4px; }
    .dowlabels span { flex: 1 1 0; text-align: center; font: 9px/1 var(--font-technical); color: var(--ink-soft); }
    .mult .mtotal { font: 10px/1.4 var(--font-technical); color: var(--ink-soft); margin: 8px 0 0; }
    .mult .mtotal b { color: var(--sanguine); font-weight: 500; }

    .days { margin-top: 30px; border-top: 1px solid var(--hairline); }
    .drow {
      display: grid;
      grid-template-columns: 158px minmax(0, 1fr) 118px;
      gap: 12px; align-items: center;
      padding: 10px 0;
      border-bottom: 1px solid var(--ghost);
    }
    .drow .dname { font: 500 11px/1.3 var(--font-technical); text-transform: uppercase; letter-spacing: .05em; }
    .drow .dname a { text-decoration: none; }
    .dcal { display: grid; grid-template-rows: repeat(7, 11px); grid-auto-flow: column; gap: 3px; justify-content: start; min-width: 0; }
    .dcal i { width: 11px; height: 11px; display: block; background: var(--ghost); }
    .drow .dval { font: 11px/1.3 var(--font-technical); color: var(--ink-soft); text-align: right; }

    .lbar { display: flex; height: 34px; margin-top: 30px; border-top: 1px solid var(--hairline); border-bottom: 1px solid var(--hairline); }
    .lbar i { display: block; height: 100%; background: var(--sanguine); border-right: 1px solid var(--paper); min-width: 1px; }
    .lbar i:last-child { border-right: 0; }
    .lkey { display: flex; flex-wrap: wrap; gap: 6px 18px; margin-top: 12px; }
    .lkey span { font: 10px/1.6 var(--font-technical); text-transform: uppercase; letter-spacing: .05em; color: var(--ink-soft); }
    .lkey b { color: var(--sanguine); font-weight: 500; }
    .lkey a { text-decoration: none; }

    .register { margin-top: 40px; border-top: 1px solid var(--hairline); }
    .entry { display: grid; grid-template-columns: 58px minmax(0, 1fr); gap: 20px; padding: 26px 0; border-bottom: 1px solid var(--hairline); }
    .entry-no { font: 11px/1.4 var(--font-technical); letter-spacing: .055em; padding-top: 6px; color: var(--ink-soft); }
    .entry h3 { margin: 0 0 6px; }
    .entry h3 a { text-decoration-thickness: 1px; }
    .entry-meta { font: 10px/1.6 var(--font-technical); text-transform: uppercase; letter-spacing: .05em; color: var(--ink-soft); display: flex; align-items: center; gap: 10px; flex-wrap: wrap; }
    .entry-meta svg { display: block; transform: translateY(1px); }
    .entry-vitals { font: 10px/1.6 var(--font-technical); text-transform: uppercase; letter-spacing: .05em; color: var(--ink-soft); margin: 8px 0 0; }
    .entry-vitals b { color: var(--sanguine); font-weight: 500; }
    .entry details { margin-top: 12px; }
    .entry summary { cursor: pointer; font: 500 11px/1 var(--font-technical); text-transform: uppercase; letter-spacing: .055em; color: var(--ink-soft); display: inline-block; padding: 8px 0; }
    .entry summary:hover { color: var(--sanguine); }
    .entry .evidence-body { font-size: 16px; color: var(--ink-soft); max-width: 44rem; padding: 4px 0 6px; }
    .entry .evidence-body strong { color: var(--ink); font-weight: 520; }
    .visit { display: inline-block; margin-top: 10px; font: 500 11px/1 var(--font-technical); text-transform: uppercase; letter-spacing: .055em; border: 1px solid var(--hairline); padding: 10px 14px; text-decoration: none; }
    .visit:hover { border-color: var(--sanguine); color: var(--sanguine); }

    .rev { max-width: 46rem; font-size: 20px; line-height: 1.4; }
    .rev .rev-date { font: 11px/1.4 var(--font-technical); text-transform: uppercase; letter-spacing: .055em; color: var(--sanguine); display: block; margin-bottom: 10px; }
    .rev s { color: var(--ink-soft); text-decoration-color: var(--sanguine); }
    .rev + .rev { margin-top: 34px; }

    .source-list { list-style: none; padding: 0; margin: 38px 0 0; }
    .source-list li { display: grid; grid-template-columns: 36px minmax(0, 1fr); gap: 12px; padding: 14px 0; border-top: 1px solid var(--hairline); font-size: 15px; line-height: 1.38; }
    .src-no { font: 10px/1.4 var(--font-technical); letter-spacing: .055em; color: var(--sanguine); padding-top: 4px; }
    .source-list a { overflow-wrap: anywhere; }
    .source-list .snote { color: var(--ink-soft); display: block; font-size: 13px; }

    .final-mark { padding-top: 54px; display: flex; justify-content: space-between; align-items: end; gap: 24px; color: var(--ink-soft); font-size: 14px; }
    .final-mark strong { color: var(--ink); font-size: 20px; font-weight: 520; }
    .folio-id { font: 10px/1.4 var(--font-technical); text-transform: uppercase; letter-spacing: .06em; text-align: right; }

    @media (max-width: 760px) {
      body { font-size: 18px; }
      .folio { padding: 22px 18px 70px 24px; }
      .opening { min-height: 0; padding: 58px 0 44px; }
      h1 { font-size: clamp(50px, 16vw, 76px); max-width: 8ch; }
      .section { padding: 56px 0; }
      .crow { grid-template-columns: 104px minmax(0, 1fr) 92px; gap: 8px; }
      .drow { grid-template-columns: 104px minmax(0, 1fr) 64px; gap: 8px; }
      .mults { grid-template-columns: repeat(2, minmax(0, 1fr)); }
      .entry { grid-template-columns: 1fr; gap: 8px; }
      .final-mark { align-items: start; flex-direction: column; }
      .folio-id { text-align: left; }
    }
    @media (prefers-reduced-motion: reduce) {
      html { scroll-behavior: auto; }
      *, *::before, *::after { transition-duration: 0.01ms !important; }
    }
  </style>
</head>
<body>
<div class="folio">
  <header class="opening">
    <p class="stamp">Folio 00 / Collected works</p>
    <h1>The <em>Index</em> Folio.</h1>
  </header>

  <section class="section" id="field-s">
    <p class="kicker">01 · The field</p>
    <h2>Weight follows updates.</h2>
    <p class="control-label">Emphasis</p>
    <div class="control-row" role="group" aria-label="Emphasis premise">
      <button class="control" data-premise="activity" aria-pressed="true">Update activity</button>
      <button class="control" data-premise="recency" aria-pressed="false">Last push</button>
      <button class="control" data-premise="folio" aria-pressed="false">Folio order</button>
    </div>
    <div class="field-wrap">
      <svg id="field" viewBox="0 0 680 440" role="img" aria-label="Diagram of the nine sites. The most updated sites sit nearest the center, drawn darkest and largest."></svg>
    </div>
    <p class="verdict-line" id="verdictLine" aria-live="polite"></p>
  </section>

  <section class="section" id="measure">
    <p class="kicker">02 · The measure</p>
    <h2 id="measureH">Commits, last 28 days.</h2>
    <div class="chart" id="chart"></div>
  </section>

  <section class="section" id="weeks">
    <p class="kicker">03 · Twelve weeks</p>
    <h2>Twelve weeks.</h2>
    <div class="mults" id="mults"></div>
  </section>

  <section class="section" id="days-s">
    <p class="kicker">04 · Twenty-eight days</p>
    <h2>Day by day.</h2>
    <p class="key-line">Columns run week by week, rows Sunday to Saturday. Darker means more commits.</p>
    <div class="days" id="days"></div>
    <p class="verdict-line">__DAYS_VERDICT__</p>
  </section>

  <section class="section" id="rhythm-s">
    <p class="kicker">05 · The rhythm</p>
    <h2>When the work lands.</h2>
    <div class="mults" id="rhythm"></div>
    <p class="verdict-line">__RHYTHM_VERDICT__</p>
  </section>

  <section class="section" id="inventory-s">
    <p class="kicker">06 · The inventory</p>
    <h2>What the commits built.</h2>
    <div class="chart" id="inventory"></div>
    <p class="verdict-line">__INV_VERDICT__</p>
  </section>

  <section class="section" id="ledger-s">
    <p class="kicker">07 · The ledger</p>
    <h2>Share of the month.</h2>
    <div class="lbar" id="lbar" role="img" aria-label="__LEDGER_ARIA__"></div>
    <div class="lkey" id="lkey"></div>
    <p class="verdict-line">__LEDGER_VERDICT__</p>
  </section>

  <section class="section" id="register-s">
    <p class="kicker">08 · The register</p>
    <div class="register" id="register"></div>
  </section>

  <section class="section" id="revision">
    <p class="kicker">09 · Revision</p>
    <h2>Revision.</h2>
    <p class="rev"><span class="rev-date">2026-09-18</span>The measure widened: 28-day daily calendars, weekday rhythm, a content inventory, and a share-of-attention ledger join the twelve-week bars. <s>Twelve-week bars and sparklines carried the whole measure.</s></p>
    <p class="rev"><span class="rev-date">2026-09-18</span><s>Quiet sites were labeled settled and kept.</s> Emphasis now follows measured update activity. A quiet site is de-emphasized, not settled.</p>
  </section>

  <section class="section" id="provenance">
    <p class="kicker">10 · Provenance</p>
    <h2>Provenance.</h2>
    <p class="quiet" style="max-width:46rem">Commit counts: GitHub repository statistics (commit activity and punch card endpoints), measured 2026-09-18. Content units counted from the live pages the same day. All nine repositories were created between Sep 8 and Sep 17, 2026, so every commit falls inside the 28-day window. Push times UTC.</p>
    <ul class="source-list" id="sourceList"></ul>
  </section>

  <footer class="final-mark">
    <div><strong>The Index Folio.</strong><br />Folio 00.</div>
    <div class="folio-id">C. Dillinger<br />Working index</div>
  </footer>
</div>
<script>
(function () {
  "use strict";
  var DATA_DATE = Date.parse('__DATA_DATE__');
  var SITES = __DATA_JSON__;
  var MAXW = Math.max.apply(null, SITES.map(function (s) { return Math.max.apply(null, s.weekly); }));

  SITES.forEach(function (s) {
    s.hoursAgo = (DATA_DATE - Date.parse(s.pushed)) / 3600000;
    s.pushDay = s.pushed.slice(0, 10);
    s.activeDays = s.daily.reduce(function (a, v) { return a + (v > 0 ? 1 : 0); }, 0);
  });
  var MAXC = Math.max.apply(null, SITES.map(function (s) { return s.c28; }));
  var MAXH = Math.max.apply(null, SITES.map(function (s) { return s.hoursAgo; }));
  var MAXD = Math.max.apply(null, SITES.map(function (s) { return Math.max.apply(null, s.daily); }));
  var MAXN = Math.max.apply(null, SITES.map(function (s) { return s.content_n; }));
  var TOT28 = SITES.reduce(function (a, s) { return a + s.c28; }, 0);

  var premise = 'activity';
  var field = document.getElementById('field');
  var verdictLine = document.getElementById('verdictLine');
  var chartEl = document.getElementById('chart');
  var multsEl = document.getElementById('mults');
  var daysEl = document.getElementById('days');
  var rhythmEl = document.getElementById('rhythm');
  var invEl = document.getElementById('inventory');
  var lbarEl = document.getElementById('lbar');
  var lkeyEl = document.getElementById('lkey');
  var registerEl = document.getElementById('register');
  var measureH = document.getElementById('measureH');

  function ordered() {
    var a = SITES.slice();
    if (premise === 'activity') a.sort(function (x, y) { return y.c28 - x.c28; });
    else if (premise === 'recency') a.sort(function (x, y) { return x.hoursAgo - y.hoursAgo; });
    else a.sort(function (x, y) { return x.folio < y.folio ? -1 : 1; });
    return a;
  }

  function nodeR(s) {
    if (premise === 'activity') return 5 + 13 * Math.sqrt(s.c28 / MAXC);
    if (premise === 'recency') return 5 + 13 * (1 - s.hoursAgo / MAXH);
    return 9;
  }

  function renderField() {
    var CX = 340, CY = 218;
    var order = ordered();
    var out = '';
    [70, 140, 205].forEach(function (r) {
      out += '<circle cx="' + CX + '" cy="' + CY + '" r="' + r + '" fill="none" stroke="var(--graphite)" stroke-width="1" opacity="0.45"/>';
    });
    out += '<line x1="' + (CX - 225) + '" y1="' + CY + '" x2="' + (CX + 225) + '" y2="' + CY + '" stroke="var(--graphite)" stroke-width="1" opacity="0.3"/>';
    out += '<line x1="' + CX + '" y1="' + (CY - 205) + '" x2="' + CX + '" y2="' + (CY + 205) + '" stroke="var(--graphite)" stroke-width="1" opacity="0.3"/>';
    var centerWord = premise === 'activity' ? 'MOST UPDATED' : premise === 'recency' ? 'MOST RECENT' : 'FOLIO 01-09';
    out += '<text x="' + CX + '" y="' + (CY + 4) + '" text-anchor="middle" font-family="var(--font-technical)" font-size="9" letter-spacing="0.08em" fill="var(--graphite)">' + centerWord + '</text>';
    order.forEach(function (s, i) {
      var ang = (-90 + i * 137.5) * Math.PI / 180;
      var rr = 36 + i * (168 / 8);
      var x = CX + rr * Math.cos(ang), y = CY + rr * Math.sin(ang);
      var nr = nodeR(s);
      var style;
      if (premise === 'folio') style = 'fill="var(--paper)" stroke="var(--ink)" stroke-width="1.5"';
      else if (i < 3) style = 'fill="var(--ink)"';
      else if (i < 6) style = 'fill="var(--sanguine)"';
      else style = 'fill="none" stroke="var(--graphite)" stroke-width="1.5" stroke-dasharray="4 3"';
      var lx = CX + (rr + nr + 16) * Math.cos(ang), ly = CY + (rr + nr + 16) * Math.sin(ang);
      var cos = Math.cos(ang);
      var anchor = cos > 0.25 ? 'start' : cos < -0.25 ? 'end' : 'middle';
      var lfill = (premise !== 'folio' && i >= 6) ? 'var(--graphite)' : 'var(--ink)';
      out += '<line x1="' + (x + Math.cos(ang) * nr).toFixed(1) + '" y1="' + (y + Math.sin(ang) * nr).toFixed(1) +
        '" x2="' + lx.toFixed(1) + '" y2="' + ly.toFixed(1) + '" stroke="var(--sanguine)" stroke-width="1" opacity="0.75"/>';
      out += '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="' + nr.toFixed(1) + '" ' + style + '/>';
      out += '<text x="' + lx.toFixed(1) + '" y="' + (ly + 3.5).toFixed(1) + '" text-anchor="' + anchor +
        '" font-family="var(--font-technical)" font-size="10.5" letter-spacing="0.06em" fill="' + lfill + '">' +
        s.name.toUpperCase() + '</text>';
    });
    field.innerHTML = out;
  }

  function renderVerdict() {
    var top = ordered()[0];
    if (premise === 'activity') {
      verdictLine.innerHTML = top.name + ' carries the most weight: <span class="m">' + top.c28 + ' commits in the last 28 days.</span>';
    } else if (premise === 'recency') {
      var p = top.pushed.slice(0, 16).replace('T', ' ');
      verdictLine.innerHTML = top.name + ' was touched most recently: <span class="m">pushed ' + p + ' UTC.</span>';
    } else {
      verdictLine.innerHTML = 'Folio order: <span class="m">nine sites, 01 to 09.</span>';
    }
  }

  function renderChart() {
    var order = ordered();
    var html = '';
    order.forEach(function (s) {
      var val, label, pct;
      if (premise === 'recency') {
        val = s.hoursAgo; label = val.toFixed(1) + ' h'; pct = (1 - val / MAXH) * 100;
      } else {
        val = s.c28; label = '' + val; pct = (val / MAXC) * 100;
      }
      html += '<div class="crow"><span class="cname"><a href="' + s.url + '">' + s.name + '</a></span>' +
        '<span class="cbar"><i style="width:' + Math.max(pct, 0.6).toFixed(1) + '%"></i></span>' +
        '<span class="cval">' + label + '</span></div>';
    });
    chartEl.innerHTML = html;
    measureH.textContent = premise === 'recency' ? 'Hours since last push.' : 'Commits, last 28 days.';
  }

  function renderMults() {
    var html = '';
    ordered().forEach(function (s) {
      var bars = '';
      s.weekly.forEach(function (v) {
        var h = v > 0 ? Math.max((v / MAXW) * 100, 5) : 0;
        bars += '<i style="height:' + h.toFixed(1) + '%"></i>';
      });
      html += '<div class="mult"><p class="mname"><a href="' + s.url + '">' + s.name + '</a></p>' +
        '<div class="wbars" role="img" aria-label="' + s.name + ', weekly commits">' + bars + '</div>' +
        '<p class="mtotal"><b>' + s.c28 + '</b> commits / 28 days</p></div>';
    });
    multsEl.innerHTML = html;
  }

  function renderDays() {
    var html = '';
    ordered().forEach(function (s) {
      var cells = '';
      s.daily.forEach(function (v, i) {
        var wd = (6 + i) % 7;
        var wk = i === 0 ? 0 : Math.floor((i + 6) / 7);
        var bg = v > 0
          ? 'background:var(--sanguine);opacity:' + (0.3 + 0.7 * v / MAXD).toFixed(2)
          : '';
        cells += '<i style="grid-row:' + (wd + 1) + ';grid-column:' + (wk + 1) + ';' + bg + '"></i>';
      });
      html += '<div class="drow"><span class="dname"><a href="' + s.url + '">' + s.name + '</a></span>' +
        '<span class="dcal" role="img" aria-label="' + s.name + ': ' + s.c28 + ' commits in 28 days, active ' + s.activeDays + ' days">' + cells + '</span>' +
        '<span class="dval">' + s.activeDays + ' of 28 days</span></div>';
    });
    daysEl.innerHTML = html;
  }

  function renderRhythm() {
    var html = '';
    var dayL = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
    var maxDow = Math.max.apply(null, SITES.map(function (s) { return Math.max.apply(null, s.dow); }));
    ordered().forEach(function (s) {
      var bars = '', labels = '';
      s.dow.forEach(function (v, i) {
        var h = v > 0 ? Math.max((v / maxDow) * 100, 5) : 0;
        bars += '<i style="height:' + h.toFixed(1) + '%"></i>';
        labels += '<span>' + dayL[i] + '</span>';
      });
      var wkday = s.dow.slice(1, 6).reduce(function (a, b) { return a + b; }, 0);
      var tot = s.dow.reduce(function (a, b) { return a + b; }, 0);
      var pct = tot > 0 ? Math.round(100 * wkday / tot) : 0;
      html += '<div class="mult"><p class="mname"><a href="' + s.url + '">' + s.name + '</a></p>' +
        '<div class="wbars" role="img" aria-label="' + s.name + ', commits by weekday">' + bars + '</div>' +
        '<div class="dowlabels" aria-hidden="true">' + labels + '</div>' +
        '<p class="mtotal"><b>' + pct + '%</b> land Mon to Fri</p></div>';
    });
    rhythmEl.innerHTML = html;
  }

  function pluralUnit(s) {
    return s.content_n + ' ' + s.content_unit + (s.content_n === 1 ? '' : (s.content_unit.slice(-1) === 's' ? '' : 's'));
  }

  function renderInventory() {
    var html = '';
    ordered().forEach(function (s) {
      var pct = (s.content_n / MAXN) * 100;
      html += '<div class="crow"><span class="cname"><a href="' + s.url + '">' + s.name + '</a></span>' +
        '<span class="cbar"><i style="width:' + Math.max(pct, 0.6).toFixed(1) + '%"></i></span>' +
        '<span class="cval">' + pluralUnit(s) + '</span></div>';
    });
    invEl.innerHTML = html;
  }

  function renderLedger() {
    var order = ordered();
    var bar = '', key = '';
    order.forEach(function (s) {
      var pct = 100 * s.c28 / TOT28;
      bar += '<i style="width:' + Math.max(pct, 0.4).toFixed(2) + '%"></i>';
      key += '<span><a href="' + s.url + '">' + s.name + '</a> <b>' + pct.toFixed(1) + '%</b></span>';
    });
    lbarEl.innerHTML = bar;
    lkeyEl.innerHTML = key;
  }

  function weekBars(s, W, H) {
    var bw = W / 12, out = '';
    s.weekly.forEach(function (v, i) {
      var h = Math.max((v / MAXW) * (H - 4), v > 0 ? 1.5 : 0);
      out += '<rect x="' + (i * bw + 1).toFixed(1) + '" y="' + (H - h).toFixed(1) + '" width="' + (bw - 2).toFixed(1) +
        '" height="' + h.toFixed(1) + '" fill="var(--sanguine)"/>';
    });
    return out;
  }

  function spark(s) {
    return '<svg width="84" height="20" viewBox="0 0 84 20" role="img" aria-label="' + s.c28 + ' commits in 28 days">' +
      weekBars(s, 84, 20).replace(/var\\(--sanguine\\)/g, 'var(--ink-soft)') + '</svg>';
  }

  function fmtKB(n) { return n.toLocaleString('en-US') + ' KB'; }

  function renderRegister() {
    var html = '';
    ordered().forEach(function (s) {
      html += '<article class="entry"><span class="entry-no">' + s.folio + '</span><div>' +
        '<h3><a href="' + s.url + '">' + s.name + '</a></h3>' +
        '<p class="entry-meta">' + spark(s) + '<span>' + s.c28 + ' commits / 28 days \\u00B7 pushed ' + s.pushDay + '</span></p>' +
        '<p class="entry-vitals"><b>' + s.activeDays + '</b> of 28 days active \\u00B7 repo ' + fmtKB(s.repo_kb) + ' \\u00B7 page ' + fmtKB(s.page_kb) + '</p>' +
        '<details><summary>More</summary><div class="evidence-body">' + s.evidence + ' Ships ' + pluralUnit(s) + ' (' + s.content_note + ').</div></details>' +
        '<a class="visit" href="' + s.url + '">Visit ' + s.name.toLowerCase() + '</a>' +
        '</div></article>';
    });
    registerEl.innerHTML = html;
  }

  function renderSources() {
    var html = '';
    SITES.slice().sort(function (a, b) { return a.folio < b.folio ? -1 : 1; }).forEach(function (s) {
      html += '<li><span class="src-no">' + s.folio + '</span><div>' +
        '<a href="https://github.com/dillingerstaffing/' + s.slug + '">github.com/dillingerstaffing/' + s.slug + '</a>' +
        '<span class="snote">' + s.c28 + ' commits in 28 days \\u00B7 pushed ' + s.pushDay + '</span></div></li>';
    });
    document.getElementById('sourceList').innerHTML = html;
  }

  function renderAll() {
    renderField();
    renderVerdict();
    renderChart();
    renderMults();
    renderDays();
    renderRhythm();
    renderInventory();
    renderLedger();
    renderRegister();
  }

  document.querySelectorAll('[data-premise]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      premise = btn.getAttribute('data-premise');
      document.querySelectorAll('[data-premise]').forEach(function (b) {
        b.setAttribute('aria-pressed', b === btn ? 'true' : 'false');
      });
      renderAll();
    });
  });

  renderSources();
  renderAll();
})();
</script>
</body>
</html>
'''

html = html.replace('__DATA_JSON__', data_js)
html = html.replace('__DATA_DATE__', DATA_DATE)
html = html.replace('__DAYS_VERDICT__',
    '%s stayed active %d of the last 28 days, more than any other site. <span class="m">%d commits.</span>'
    % (top_active['name'], top_active_n, top_active['c28']))
html = html.replace('__RHYTHM_VERDICT__',
    '%d%% of all commits land Monday to Friday. <span class="m">The loops work weekdays; weekends go quiet.</span>' % wk_pct)
def _plural(n, unit):
    return '%d %s%s' % (n, unit, '' if n == 1 or unit.endswith('s') else 's')
html = html.replace('__INV_VERDICT__',
    '%s ships the most content: <span class="m">%s and %s.</span>'
    % (top_content['name'], _plural(top_content['content_n'], top_content['content_unit']), CONTENT['portfolio'][2]))
html = html.replace('__LEDGER_VERDICT__',
    '%s and %s together take %d%% of the month. <span class="m">%d commits across nine sites.</span>'
    % (top2[0]['name'], top2[1]['name'], top2_pct, tot28))
html = html.replace('__LEDGER_ARIA__',
    'Share of %d commits in the last 28 days by site' % tot28)

open('/home/hatch/workspace/deploy/index-site/index.html', 'w').write(html)
print('wrote', len(html), 'bytes')
print('days verdict:', top_active['name'], top_active_n)
print('rhythm verdict:', wk_pct)
print('ledger verdict:', top2[0]['name'], top2[1]['name'], top2_pct, tot28)
