#!/usr/bin/env python3
"""Interactivity pass for the Index Folio.

Patches index.html in place:
- merges hourly/best-day fields into the embedded SITES data
- replaces the inline script with a linked-selection build
  (cross-highlighting, inspector sheet, measure switcher, scale
  toggles, cell readouts, hash state, keyboard walk)
- adds the hour-of-day section, inspector markup, and CSS
- renumbers kickers, extends the revision ledger and provenance
"""
import json, re

P = '/home/hatch/workspace/deploy/index-site/index.html'
html = open(P).read()

# ---- 1. merge new data fields into embedded SITES ----
m = re.search(r"var SITES = (\[.*?\]);", html, re.S)
sites = json.loads(m.group(1))
A = json.load(open('/tmp/folio-data/assembled.json'))
for s in sites:
    d = A[s['slug']]
    s['hourly'] = d['hourly']
    s['peak_hour'] = d['peak_hour']
    s['best_day_date'] = d['best_day_date']
    s['best_day_commits'] = d['best_day_commits']
data_js = json.dumps(sites, separators=(',', ':'))

tot_hr = [0] * 24
for s in sites:
    for h in range(24):
        tot_hr[h] += s['hourly'][h]
peak_h = max(range(24), key=lambda h: tot_hr[h])
hours_verdict = ("Commits land in every hour of the day. "
                 '<span class="m">%02d:00 UTC is the single busiest hour.</span>' % peak_h)

NEW_JS = r"""(function () {
  "use strict";
  var DATA_DATE = Date.parse('2026-09-18T20:17:04Z');
  var SITES = __DATA_JSON__;
  var MAXW = Math.max.apply(null, SITES.map(function (s) { return Math.max.apply(null, s.weekly); }));

  SITES.forEach(function (s) {
    s.hoursAgo = (DATA_DATE - Date.parse(s.pushed)) / 3600000;
    s.pushDay = s.pushed.slice(0, 10);
    s.activeDays = s.daily.reduce(function (a, v) { return a + (v > 0 ? 1 : 0); }, 0);
    var w = s.dow.slice(1, 6).reduce(function (a, b) { return a + b; }, 0);
    var t = s.dow.reduce(function (a, b) { return a + b; }, 0);
    s.wkdayPct = t > 0 ? Math.round(100 * w / t) : 0;
  });
  var MAXC = Math.max.apply(null, SITES.map(function (s) { return s.c28; }));
  var MAXH = Math.max.apply(null, SITES.map(function (s) { return s.hoursAgo; }));
  var MAXD = Math.max.apply(null, SITES.map(function (s) { return Math.max.apply(null, s.daily); }));
  var MAXN = Math.max.apply(null, SITES.map(function (s) { return s.content_n; }));
  var MAXP = Math.max.apply(null, SITES.map(function (s) { return s.page_kb; }));
  var MAXDOW = Math.max.apply(null, SITES.map(function (s) { return Math.max.apply(null, s.dow); }));
  var MAXHR = Math.max.apply(null, SITES.map(function (s) { return Math.max.apply(null, s.hourly); }));
  var TOT28 = SITES.reduce(function (a, s) { return a + s.c28; }, 0);

  var DAY_DATES = (function () {
    var out = [], months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    for (var i = 0; i < 28; i++) {
      var t = new Date(DATA_DATE - (27 - i) * 86400000);
      out.push(months[t.getUTCMonth()] + ' ' + t.getUTCDate());
    }
    return out;
  })();

  var state = { premise: 'activity', measure: 'commits', selected: null, dayScale: 'shared', dowScale: 'shared' };

  var field = document.getElementById('field');
  var verdictLine = document.getElementById('verdictLine');
  var chartEl = document.getElementById('chart');
  var measureH = document.getElementById('measureH');
  var multsEl = document.getElementById('mults');
  var daysEl = document.getElementById('days');
  var dayReadout = document.getElementById('dayReadout');
  var rhythmEl = document.getElementById('rhythm');
  var hoursEl = document.getElementById('hours');
  var hourReadout = document.getElementById('hourReadout');
  var invEl = document.getElementById('inventory');
  var lbarEl = document.getElementById('lbar');
  var lkeyEl = document.getElementById('lkey');
  var registerEl = document.getElementById('register');

  function ordered() {
    var a = SITES.slice();
    if (state.premise === 'activity') a.sort(function (x, y) { return y.c28 - x.c28; });
    else if (state.premise === 'recency') a.sort(function (x, y) { return x.hoursAgo - y.hoursAgo; });
    else a.sort(function (x, y) { return x.folio < y.folio ? -1 : 1; });
    return a;
  }
  function bySlug(slug) {
    for (var i = 0; i < SITES.length; i++) if (SITES[i].slug === slug) return SITES[i];
    return null;
  }

  var MEASURES = {
    commits: { h: 'Commits, last 28 days.', val: function (s) { return s.c28; },
               fmt: function (v) { return '' + v; }, max: MAXC, inv: false },
    days:    { h: 'Active days of 28.', val: function (s) { return s.activeDays; },
               fmt: function (v) { return v + ' of 28'; }, max: 28, inv: false },
    weight:  { h: 'Page weight.', val: function (s) { return s.page_kb; },
               fmt: function (v) { return v + ' KB'; }, max: MAXP, inv: false },
    push:    { h: 'Hours since last push.', val: function (s) { return s.hoursAgo; },
               fmt: function (v) { return v.toFixed(1) + ' h'; }, max: MAXH, inv: true }
  };

  function nodeR(s) {
    if (state.premise === 'activity') return 5 + 13 * Math.sqrt(s.c28 / MAXC);
    if (state.premise === 'recency') return 5 + 13 * (1 - s.hoursAgo / MAXH);
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
    var centerWord = state.premise === 'activity' ? 'MOST UPDATED' : state.premise === 'recency' ? 'MOST RECENT' : 'FOLIO 01-08';
    out += '<text x="' + CX + '" y="' + (CY + 4) + '" text-anchor="middle" font-family="var(--font-technical)" font-size="9" letter-spacing="0.08em" fill="var(--graphite)">' + centerWord + '</text>';
    order.forEach(function (s, i) {
      var ang = (-90 + i * 137.5) * Math.PI / 180;
      var rr = 36 + i * (168 / 7);
      var x = CX + rr * Math.cos(ang), y = CY + rr * Math.sin(ang);
      var nr = nodeR(s);
      var style;
      if (state.premise === 'folio') style = 'fill="var(--paper)" stroke="var(--ink)" stroke-width="1.5"';
      else if (i < 3) style = 'fill="var(--ink)"';
      else if (i < 6) style = 'fill="var(--sanguine)"';
      else style = 'fill="none" stroke="var(--graphite)" stroke-width="1.5" stroke-dasharray="4 3"';
      var lx = CX + (rr + nr + 16) * Math.cos(ang), ly = CY + (rr + nr + 16) * Math.sin(ang);
      var cos = Math.cos(ang);
      var anchor = cos > 0.25 ? 'start' : cos < -0.25 ? 'end' : 'middle';
      var lfill = (state.premise !== 'folio' && i >= 6) ? 'var(--graphite)' : 'var(--ink)';
      out += '<g class="node" data-slug="' + s.slug + '">';
      out += '<line x1="' + (x + Math.cos(ang) * nr).toFixed(1) + '" y1="' + (y + Math.sin(ang) * nr).toFixed(1) +
        '" x2="' + lx.toFixed(1) + '" y2="' + ly.toFixed(1) + '" stroke="var(--sanguine)" stroke-width="1" opacity="0.75"/>';
      out += '<circle cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="' + nr.toFixed(1) + '" ' + style + '/>';
      out += '<text x="' + lx.toFixed(1) + '" y="' + (ly + 3.5).toFixed(1) + '" text-anchor="' + anchor +
        '" font-family="var(--font-technical)" font-size="10.5" letter-spacing="0.06em" fill="' + lfill + '">' +
        s.name.toUpperCase() + '</text>';
      out += '</g>';
    });
    field.innerHTML = out;
  }

  function renderVerdict() {
    var top = ordered()[0];
    if (state.premise === 'activity') {
      verdictLine.innerHTML = top.name + ' carries the most weight: <span class="m">' + top.c28 + ' commits in the last 28 days.</span>';
    } else if (state.premise === 'recency') {
      var p = top.pushed.slice(0, 16).replace('T', ' ');
      verdictLine.innerHTML = top.name + ' was touched most recently: <span class="m">pushed ' + p + ' UTC.</span>';
    } else {
      verdictLine.innerHTML = 'Folio order: <span class="m">eight sites, 01 to 08.</span>';
    }
  }

  function renderChart() {
    var M = MEASURES[state.measure];
    var html = '';
    ordered().forEach(function (s) {
      var v = M.val(s);
      var pct = M.inv ? (1 - v / M.max) * 100 : (v / M.max) * 100;
      html += '<div class="crow" data-slug="' + s.slug + '"><span class="cname"><a href="' + s.url + '">' + s.name + '</a></span>' +
        '<span class="cbar"><i style="width:' + Math.max(pct, 0.6).toFixed(1) + '%"></i></span>' +
        '<span class="cval">' + M.fmt(v) + '</span></div>';
    });
    chartEl.innerHTML = html;
    measureH.textContent = M.h;
  }

  function renderMults() {
    var html = '';
    ordered().forEach(function (s) {
      var bars = '';
      s.weekly.forEach(function (v) {
        var h = v > 0 ? Math.max((v / MAXW) * 100, 5) : 0;
        bars += '<i style="height:' + h.toFixed(1) + '%"></i>';
      });
      html += '<div class="mult" data-slug="' + s.slug + '"><p class="mname"><a href="' + s.url + '">' + s.name + '</a></p>' +
        '<div class="wbars" role="img" aria-label="' + s.name + ', weekly commits">' + bars + '</div>' +
        '<p class="mtotal"><b>' + s.c28 + '</b> commits / 28 days</p></div>';
    });
    multsEl.innerHTML = html;
  }

  function renderDays() {
    var html = '';
    var smaxShared = MAXD;
    ordered().forEach(function (s) {
      var smax = state.dayScale === 'persite' ? Math.max.apply(null, s.daily) : smaxShared;
      var cells = '';
      s.daily.forEach(function (v, i) {
        var wd = (6 + i) % 7;
        var wk = i === 0 ? 0 : Math.floor((i + 6) / 7);
        var bg = v > 0 && smax > 0
          ? 'background:var(--sanguine);opacity:' + (0.3 + 0.7 * v / smax).toFixed(2)
          : '';
        cells += '<i class="dc" data-date="' + DAY_DATES[i] + '" data-n="' + v + '" style="grid-row:' + (wd + 1) + ';grid-column:' + (wk + 1) + ';' + bg + '"></i>';
      });
      html += '<div class="drow" data-slug="' + s.slug + '"><span class="dname"><a href="' + s.url + '">' + s.name + '</a></span>' +
        '<span class="dcal" role="img" aria-label="' + s.name + ': ' + s.c28 + ' commits in 28 days, active ' + s.activeDays + ' days">' + cells + '</span>' +
        '<span class="dval">' + s.activeDays + ' of 28 days</span></div>';
    });
    daysEl.innerHTML = html;
  }

  function renderRhythm() {
    var html = '';
    var dayL = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];
    ordered().forEach(function (s) {
      var smax = state.dowScale === 'persite' ? Math.max.apply(null, s.dow) : MAXDOW;
      var bars = '', labels = '';
      s.dow.forEach(function (v, i) {
        var h = v > 0 && smax > 0 ? Math.max((v / smax) * 100, 5) : 0;
        bars += '<i style="height:' + h.toFixed(1) + '%"></i>';
        labels += '<span>' + dayL[i] + '</span>';
      });
      html += '<div class="mult" data-slug="' + s.slug + '"><p class="mname"><a href="' + s.url + '">' + s.name + '</a></p>' +
        '<div class="wbars" role="img" aria-label="' + s.name + ', commits by weekday">' + bars + '</div>' +
        '<div class="dowlabels" aria-hidden="true">' + labels + '</div>' +
        '<p class="mtotal"><b>' + s.wkdayPct + '%</b> land Mon to Fri</p></div>';
    });
    rhythmEl.innerHTML = html;
  }

  function pad2(n) { return (n < 10 ? '0' : '') + n; }

  function renderHours() {
    var html = '';
    ordered().forEach(function (s) {
      var cells = '';
      s.hourly.forEach(function (v, h) {
        var bg = v > 0
          ? 'background:var(--sanguine);opacity:' + (0.3 + 0.7 * v / MAXHR).toFixed(2)
          : '';
        cells += '<i class="hc" data-h="' + pad2(h) + '" data-n="' + v + '" style="' + bg + '"></i>';
      });
      var plabel = pad2(s.peak_hour) + ':00';
      html += '<div class="hrow" data-slug="' + s.slug + '">' +
        '<span class="hname"><a href="' + s.url + '">' + s.name + '</a></span>' +
        '<span class="hstrip" role="img" aria-label="' + s.name + ', commits by hour of day, peak ' + plabel + ' UTC">' + cells + '</span>' +
        '<span class="hpeak">peak ' + plabel + '</span></div>';
    });
    hoursEl.innerHTML = html;
  }

  function pluralUnit(s) {
    return s.content_n + ' ' + s.content_unit + (s.content_n === 1 ? '' : (s.content_unit.slice(-1) === 's' ? '' : 's'));
  }

  function renderInventory() {
    var html = '';
    ordered().forEach(function (s) {
      var pct = (s.content_n / MAXN) * 100;
      html += '<div class="crow" data-slug="' + s.slug + '"><span class="cname"><a href="' + s.url + '">' + s.name + '</a></span>' +
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
      bar += '<i data-slug="' + s.slug + '" style="width:' + Math.max(pct, 0.4).toFixed(2) + '%"></i>';
      key += '<span data-slug="' + s.slug + '"><a href="' + s.url + '">' + s.name + '</a> <b>' + pct.toFixed(1) + '%</b></span>';
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
      weekBars(s, 84, 20).replace(/var\(--sanguine\)/g, 'var(--ink-soft)') + '</svg>';
  }

  function sparkDaily(s) {
    var W = 252, H = 26, bw = W / 28, out = '';
    var mx = Math.max.apply(null, s.daily);
    s.daily.forEach(function (v, i) {
      var h = v > 0 && mx > 0 ? Math.max((v / mx) * (H - 3), 1.5) : 0;
      out += '<rect x="' + (i * bw + 0.5).toFixed(1) + '" y="' + (H - h).toFixed(1) + '" width="' + (bw - 1).toFixed(1) +
        '" height="' + h.toFixed(1) + '" fill="var(--sanguine)"/>';
    });
    return '<svg width="100%" height="26" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="none" role="img" aria-label="Daily commits, last 28 days">' + out + '</svg>';
  }

  function fmtKB(n) { return n.toLocaleString('en-US') + ' KB'; }

  function renderRegister() {
    var html = '';
    ordered().forEach(function (s) {
      html += '<article class="entry" data-slug="' + s.slug + '"><span class="entry-no">' + s.folio + '</span><div>' +
        '<h3><a href="' + s.url + '">' + s.name + '</a></h3>' +
        '<p class="entry-meta">' + spark(s) + '<span>' + s.c28 + ' commits / 28 days · pushed ' + s.pushDay + '</span></p>' +
        '<p class="entry-vitals"><b>' + s.activeDays + '</b> of 28 days active · repo ' + fmtKB(s.repo_kb) + ' · page ' + fmtKB(s.page_kb) + '</p>' +
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
        '<span class="snote">' + s.c28 + ' commits in 28 days · pushed ' + s.pushDay + '</span></div></li>';
    });
    document.getElementById('sourceList').innerHTML = html;
  }

  /* linked selection */
  var insp = document.getElementById('inspector');
  function applySelection() {
    var sel = state.selected;
    var els = document.querySelectorAll('[data-slug]');
    for (var i = 0; i < els.length; i++) {
      var on = els[i].getAttribute('data-slug') === sel;
      els[i].classList.toggle('sel', !!sel && on);
      els[i].classList.toggle('dim', !!sel && !on);
    }
    renderInspector();
    writeHash();
  }
  function toggleSelect(slug) {
    state.selected = (state.selected === slug) ? null : slug;
    applySelection();
  }
  function stepSel(dir) {
    var o = ordered().map(function (s) { return s.slug; });
    var i = o.indexOf(state.selected);
    var n = i < 0 ? (dir > 0 ? 0 : o.length - 1) : (i + dir + o.length) % o.length;
    state.selected = o[n];
    applySelection();
  }

  function renderInspector() {
    var s = state.selected ? bySlug(state.selected) : null;
    insp.classList.toggle('open', !!s);
    document.body.classList.toggle('has-inspector', !!s);
    if (!s) return;
    document.getElementById('inspName').textContent = s.folio + ' ' + s.name;
    document.getElementById('inspSum').textContent = s.c28 + ' commits · ' + s.activeDays + ' active days';
    document.getElementById('inspL1').innerHTML = '<span class="m">' + s.c28 + ' commits</span> in 28 days · active <span class="m">' + s.activeDays + '</span> of 28 days';
    document.getElementById('inspL2').innerHTML = 'Last push ' + s.pushDay + ' (' + s.hoursAgo.toFixed(1) + ' h before the measure) · <span class="m">' + s.wkdayPct + '%</span> Mon to Fri';
    document.getElementById('inspL3').innerHTML = 'Ships ' + pluralUnit(s) + ' (' + s.content_note + ') · repo ' + fmtKB(s.repo_kb) + ' · page ' + fmtKB(s.page_kb);
    document.getElementById('inspL4').innerHTML = 'Best day <span class="m">' + s.best_day_date + ': ' + s.best_day_commits + ' commits</span> · busiest hour <span class="m">' + pad2(s.peak_hour) + ':00 UTC</span>';
    document.getElementById('inspSpark').innerHTML = sparkDaily(s);
    var v = document.getElementById('inspVisit');
    v.href = s.url;
    v.textContent = 'Visit ' + s.name.toLowerCase();
  }

  function wireSelectable(container, cellClass, onCell) {
    container.addEventListener('click', function (e) {
      var t = e.target;
      if (cellClass && t.classList && t.classList.contains(cellClass)) { onCell(t); return; }
      if (t.closest && t.closest('a,summary,button')) return;
      var holder = t.closest ? t.closest('[data-slug]') : null;
      if (holder) toggleSelect(holder.getAttribute('data-slug'));
    });
  }

  function readHash() {
    var h = location.hash.replace(/^#\/?/, '');
    h.split('&').forEach(function (kv) {
      var p = kv.split('=');
      if (p[0] === 'p' && ['activity', 'recency', 'folio'].indexOf(p[1]) >= 0) state.premise = p[1];
      if (p[0] === 'm' && MEASURES[p[1]]) state.measure = p[1];
      if (p[0] === 's' && bySlug(p[1])) state.selected = p[1];
    });
  }
  function writeHash() {
    var h = '#p=' + state.premise + '&m=' + state.measure + (state.selected ? '&s=' + state.selected : '');
    try { history.replaceState(null, '', h); } catch (e) {}
  }

  function renderAll() {
    renderField();
    renderVerdict();
    renderChart();
    renderMults();
    renderDays();
    renderRhythm();
    renderHours();
    renderInventory();
    renderLedger();
    renderRegister();
  }

  function pressedIn(group, btn) {
    document.querySelectorAll(group).forEach(function (b) {
      b.setAttribute('aria-pressed', b === btn ? 'true' : 'false');
    });
  }

  document.querySelectorAll('[data-premise]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      state.premise = btn.getAttribute('data-premise');
      pressedIn('[data-premise]', btn);
      renderAll();
      applySelection();
    });
  });

  document.querySelectorAll('[data-measure]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      state.measure = btn.getAttribute('data-measure');
      pressedIn('[data-measure]', btn);
      renderChart();
      applySelection();
    });
  });

  document.querySelectorAll('[data-scale]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var key = btn.getAttribute('data-scale');
      state[key] = btn.getAttribute('data-val');
      pressedIn('[data-scale="' + key + '"]', btn);
      if (key === 'dayScale') renderDays(); else renderRhythm();
      applySelection();
    });
  });

  wireSelectable(field, null, null);
  wireSelectable(chartEl, null, null);
  wireSelectable(multsEl, null, null);
  wireSelectable(daysEl, 'dc', function (cell) {
    var holder = cell.closest('[data-slug]');
    var s = holder ? bySlug(holder.getAttribute('data-slug')) : null;
    dayReadout.textContent = cell.getAttribute('data-date') + ' · ' + (s ? s.name : '') + ' · ' + cell.getAttribute('data-n') + ' commits';
  });
  daysEl.addEventListener('mouseover', function (e) {
    var t = e.target;
    if (t.classList && t.classList.contains('dc')) {
      var holder = t.closest('[data-slug]');
      var s = holder ? bySlug(holder.getAttribute('data-slug')) : null;
      dayReadout.textContent = t.getAttribute('data-date') + ' · ' + (s ? s.name : '') + ' · ' + t.getAttribute('data-n') + ' commits';
    }
  });
  wireSelectable(rhythmEl, null, null);
  wireSelectable(hoursEl, 'hc', function (cell) {
    var holder = cell.closest('[data-slug]');
    var s = holder ? bySlug(holder.getAttribute('data-slug')) : null;
    hourReadout.textContent = cell.getAttribute('data-h') + ':00 UTC · ' + (s ? s.name : '') + ' · ' + cell.getAttribute('data-n') + ' commits';
  });
  hoursEl.addEventListener('mouseover', function (e) {
    var t = e.target;
    if (t.classList && t.classList.contains('hc')) {
      var holder = t.closest('[data-slug]');
      var s = holder ? bySlug(holder.getAttribute('data-slug')) : null;
      hourReadout.textContent = t.getAttribute('data-h') + ':00 UTC · ' + (s ? s.name : '') + ' · ' + t.getAttribute('data-n') + ' commits';
    }
  });
  wireSelectable(invEl, null, null);
  wireSelectable(lbarEl, null, null);
  wireSelectable(lkeyEl, null, null);
  wireSelectable(registerEl, null, null);

  document.getElementById('inspToggle').addEventListener('click', function () {
    var body = document.getElementById('inspBody');
    var open = body.hasAttribute('hidden');
    if (open) body.removeAttribute('hidden'); else body.setAttribute('hidden', '');
    this.setAttribute('aria-expanded', open ? 'true' : 'false');
    document.querySelector('.insp-chev').textContent = open ? '−' : '+';
  });
  document.getElementById('inspClose').addEventListener('click', function (e) {
    e.stopPropagation();
    state.selected = null;
    applySelection();
  });
  document.getElementById('inspPrev').addEventListener('click', function (e) { e.stopPropagation(); stepSel(-1); });
  document.getElementById('inspNext').addEventListener('click', function (e) { e.stopPropagation(); stepSel(1); });

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') { state.selected = null; applySelection(); }
    else if (e.key === 'ArrowRight') { stepSel(1); e.preventDefault(); }
    else if (e.key === 'ArrowLeft') { stepSel(-1); e.preventDefault(); }
  });

  readHash();
  pressedIn('[data-premise]', document.querySelector('[data-premise="' + state.premise + '"]'));
  pressedIn('[data-measure]', document.querySelector('[data-measure="' + state.measure + '"]'));
  renderSources();
  renderAll();
  applySelection();
})();
"""

NEW_CSS = """
    /* linked selection */
    [data-slug] { transition: opacity .18s ease; }
    .dim { opacity: .28; }
    .crow.sel { box-shadow: inset 2px 0 0 var(--sanguine); }
    .mult.sel { outline: 1px solid var(--sanguine); outline-offset: 3px; }
    .entry.sel { border-left: 2px solid var(--sanguine); padding-left: 18px; }
    .lbar i.sel { outline: 2px solid var(--sanguine); outline-offset: -2px; }
    .lkey span.sel b { color: var(--sanguine); }
    .node { cursor: pointer; }
    .node.sel circle { stroke: var(--sanguine); stroke-width: 2.5; }
    .crow, .mult, .drow, .hrow, .lbar i, .lkey span { cursor: pointer; }
    .entry { cursor: pointer; }
    @media (prefers-reduced-motion: reduce) { [data-slug], #inspector { transition: none; } }
    .readout { font: 11px/1.6 var(--font-technical); letter-spacing: .02em; color: var(--ink-soft); margin: 10px 0 0; min-height: 17px; }
    .dc, .hc { cursor: pointer; }
    /* hour-of-day section */
    .hours { margin-top: 26px; display: flex; flex-direction: column; gap: 12px; }
    .hrow { display: grid; grid-template-columns: 1fr; gap: 6px; align-items: center; }
    .hname { font: 500 11px/1.3 var(--font-technical); text-transform: uppercase; letter-spacing: .05em; }
    .hname a { text-decoration: none; }
    .hstrip { display: grid; grid-template-columns: repeat(24, minmax(0, 1fr)); gap: 2px; }
    .hstrip i { aspect-ratio: 1 / 1; min-width: 0; background: var(--ghost); display: block; }
    .hpeak { font: 11px/1.3 var(--font-technical); color: var(--ink-soft); }
    .hticks-wrap { display: grid; grid-template-columns: 1fr; margin-top: 8px; }
    .hticks { display: grid; grid-template-columns: repeat(24, minmax(0, 1fr)); gap: 2px; font: 9px/1 var(--font-technical); color: var(--ink-soft); }
    @media (min-width: 760px) {
      .hrow { grid-template-columns: 150px minmax(0, 1fr) 92px; }
      .hpeak { text-align: right; }
      .hticks-wrap { grid-template-columns: 150px minmax(0, 1fr) 92px; }
      .hticks { grid-column: 2; }
    }
    /* inspector */
    #inspector { position: fixed; left: 0; right: 0; bottom: 0; z-index: 60; background: var(--paper);
      border-top: 1px solid var(--hairline); transform: translateY(103%); transition: transform .22s ease;
      padding-bottom: env(safe-area-inset-bottom); }
    #inspector.open { transform: none; box-shadow: 0 -8px 24px rgba(0, 0, 0, .08); }
    .insp-bar { display: flex; align-items: stretch; }
    .insp-toggle { flex: 1; min-width: 0; display: flex; align-items: baseline; gap: 10px; background: none;
      border: 0; color: var(--ink); font: inherit; padding: 14px 16px; cursor: pointer; text-align: left; }
    .insp-name { font: 500 12px/1.3 var(--font-technical); text-transform: uppercase; letter-spacing: .06em; white-space: nowrap; }
    .insp-sum { font: 11px/1.3 var(--font-technical); color: var(--ink-soft); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
    .insp-chev { margin-left: auto; color: var(--sanguine); font: 500 14px/1 var(--font-technical); }
    .insp-nav { display: flex; }
    .insp-nav button, .insp-x { background: none; border: 0; color: var(--ink-soft); font: 14px/1 var(--font-technical); padding: 14px 12px; cursor: pointer; }
    .insp-nav button:hover, .insp-x:hover { color: var(--sanguine); }
    .insp-body { border-top: 1px solid var(--hairline); padding: 14px 16px 18px; max-height: 62vh; overflow-y: auto; }
    .insp-line { font: 11px/1.7 var(--font-technical); letter-spacing: .02em; color: var(--ink-soft); margin: 0; }
    .insp-line .m { color: var(--sanguine); font-weight: 500; }
    .insp-spark { margin: 12px 0 4px; }
    .insp-foot { display: flex; justify-content: space-between; align-items: baseline; margin: 10px 0 0; }
    .insp-hint { font: 10px/1.4 var(--font-technical); color: var(--ink-soft); }
    body.has-inspector .folio { padding-bottom: 64px; }
    @media (min-width: 760px) {
      #inspector { left: auto; right: 24px; bottom: 24px; width: 400px; border: 1px solid var(--hairline); padding-bottom: 0; }
      body.has-inspector .folio { padding-bottom: 0; }
    }
"""

INSPECTOR_HTML = """
<div id="inspector" aria-live="polite">
  <div class="insp-bar">
    <button class="insp-toggle" id="inspToggle" aria-expanded="false" aria-controls="inspBody">
      <span class="insp-name" id="inspName"></span>
      <span class="insp-sum" id="inspSum"></span>
      <span class="insp-chev" aria-hidden="true">+</span>
    </button>
    <span class="insp-nav" role="group" aria-label="Walk sites">
      <button id="inspPrev" aria-label="Previous site">&larr;</button>
      <button id="inspNext" aria-label="Next site">&rarr;</button>
    </span>
    <button class="insp-x" id="inspClose" aria-label="Clear selection">&times;</button>
  </div>
  <div class="insp-body" id="inspBody" hidden>
    <p class="insp-line" id="inspL1"></p>
    <p class="insp-line" id="inspL2"></p>
    <p class="insp-line" id="inspL3"></p>
    <p class="insp-line" id="inspL4"></p>
    <div class="insp-spark" id="inspSpark"></div>
    <p class="insp-foot"><a id="inspVisit" href="#">Visit</a><span class="insp-hint">&larr; &rarr; walk &middot; esc clears</span></p>
  </div>
</div>
"""

HOURS_SECTION = """
  <section class="section" id="hours-s">
    <p class="kicker">06 · The hours</p>
    <h2>All hours, no office.</h2>
    <p class="key-line">Hour of day, UTC. Darker means more commits.</p>
    <div class="hours" id="hours"></div>
    <div class="hticks-wrap"><div class="hticks" aria-hidden="true">__HOUR_TICKS__</div></div>
    <p class="readout" id="hourReadout" aria-live="polite">Tap an hour for its exact count.</p>
    <p class="verdict-line">__HOURS_VERDICT__</p>
  </section>
"""

ticks = ''.join(
    '<span style="grid-column:%d">%s</span>' % (c, lab)
    for c, lab in ((1, '00'), (7, '06'), (13, '12'), (19, '18')))
HOURS_SECTION = HOURS_SECTION.replace('__HOUR_TICKS__', ticks)
HOURS_SECTION = HOURS_SECTION.replace('__HOURS_VERDICT__', hours_verdict)

# ---- 2. replace the inline script ----
start = html.find('(function () {')
end = html.find('})();', start) + len('})();')
new_js = NEW_JS.replace('__DATA_JSON__', data_js)
html = html[:start] + new_js + html[end:]

# ---- 3. section markup patches ----
html = html.replace(
    '<h2 id="measureH">Commits, last 28 days.</h2>',
    '<h2 id="measureH">Commits, last 28 days.</h2>\n'
    '    <p class="control-label">Quantity</p>\n'
    '    <div class="control-row" role="group" aria-label="Measured quantity">\n'
    '      <button class="control" data-measure="commits" aria-pressed="true">Commits</button>\n'
    '      <button class="control" data-measure="days" aria-pressed="false">Active days</button>\n'
    '      <button class="control" data-measure="weight" aria-pressed="false">Page weight</button>\n'
    '      <button class="control" data-measure="push" aria-pressed="false">Last push</button>\n'
    '    </div>')

html = html.replace(
    '<p class="key-line">Columns run week by week, rows Sunday to Saturday. Darker means more commits.</p>\n    <div class="days" id="days"></div>',
    '<p class="key-line">Columns run week by week, rows Sunday to Saturday. Darker means more commits.</p>\n'
    '    <p class="control-label">Cell scale</p>\n'
    '    <div class="control-row" role="group" aria-label="Day cell scale">\n'
    '      <button class="control" data-scale="dayScale" data-val="shared" aria-pressed="true">Shared</button>\n'
    '      <button class="control" data-scale="dayScale" data-val="persite" aria-pressed="false">Per site</button>\n'
    '    </div>\n'
    '    <div class="days" id="days"></div>\n'
    '    <p class="readout" id="dayReadout" aria-live="polite">Tap a day for its exact count.</p>')

html = html.replace(
    '<h2>When the work lands.</h2>\n    <div class="mults" id="rhythm"></div>',
    '<h2>When the work lands.</h2>\n'
    '    <p class="control-label">Bar scale</p>\n'
    '    <div class="control-row" role="group" aria-label="Weekday bar scale">\n'
    '      <button class="control" data-scale="dowScale" data-val="shared" aria-pressed="true">Shared</button>\n'
    '      <button class="control" data-scale="dowScale" data-val="persite" aria-pressed="false">Per site</button>\n'
    '    </div>\n'
    '    <div class="mults" id="rhythm"></div>')

# renumber kickers after the new section
for old, new in [('06 · The inventory', '07 · The inventory'),
                 ('07 · The ledger', '08 · The ledger'),
                 ('08 · The register', '09 · The register'),
                 ('09 · Revision', '10 · Revision'),
                 ('10 · Provenance', '11 · Provenance')]:
    assert old in html, old
    html = html.replace(old, new)

anchor = '<section class="section" id="inventory-s">'
assert anchor in html
html = html.replace(anchor, HOURS_SECTION + '\n' + anchor)

# revision ledger: newest entry first
rev_anchor = '<h2>Revision.</h2>'
assert rev_anchor in html
html = html.replace(
    rev_anchor,
    rev_anchor + '\n'
    '    <p class="rev"><span class="rev-date">2026-09-18</span>Interactivity pass: every display is now linked. '
    'Tap any site to highlight it across every display and open its inspector; the measure takes four quantities; '
    'day, weekday, and hour cells answer with exact counts; a new hour-of-day section shows when the work actually lands.</p>')

html = html.replace(
    'Push times UTC.',
    'Push times UTC. Hour-of-day totals come from each repository\u2019s punch-card endpoint; hours are UTC.')

# ---- 4. css + inspector ----
html = html.replace('</style>', NEW_CSS + '\n  </style>')
html = html.replace('<script>\n(function () {', INSPECTOR_HTML + '\n<script>\n(function () {')

open(P, 'w').write(html)
print('patched', len(html), 'bytes')

# ---- 5. js syntax check ----
import subprocess, tempfile
m2 = re.search(r"\(function \(\) \{(.*?)\}\)\(\);\n</script>", html, re.S)
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False) as f:
    f.write(m2.group(0))
    path = f.name
r = subprocess.run(['node', '--check', path], capture_output=True, text=True)
print('node --check:', 'OK' if r.returncode == 0 else r.stderr[:500])
assert r.returncode == 0, 'JS syntax failed'
print('data sites:', len(sites), '| peak hour:', '%02d:00 UTC' % peak_h)
