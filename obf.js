'use strict';
const fs = require('fs');
const path = require('path');

const RV = new Set([
  'break','case','catch','class','const','continue','debugger','default','delete',
  'do','else','enum','export','extends','false','finally','for','function','if',
  'import','in','instanceof','let','new','null','return','static','super','switch',
  'this','throw','true','try','typeof','var','void','while','with','yield',
  'async','await','of','as','from','get','set','target','arguments','eval',
  'undefined','NaN','Infinity','Object','Array','String','Number','Boolean',
  'Symbol','BigInt','Map','Set','WeakMap','WeakSet','Promise','Proxy','Reflect',
  'Error','TypeError','RangeError','RegExp','Date','Math','JSON','console',
  'process','parseInt','parseFloat','isNaN','isFinite','global','require',
  'module','exports','__dirname','__filename','FinalizationRegistry','WeakRef',
  'SharedArrayBuffer','ArrayBuffer','Atomics','DataView','WebAssembly',
  'performance','globalThis','Buffer','Uint8Array','Uint8ClampedArray',
  'Int8Array','Uint16Array','Int16Array','Uint32Array','Int32Array',
  'Float16Array','Float32Array','Float64Array','BigInt64Array','BigUint64Array',
  'TextEncoder','TextDecoder','URL','URLSearchParams','SyntaxError'
]);

function tok(s) {
  var a = [], i = 0, n = s.length, l = 1;
  var tm = 'none', ts = [], td = 0, lv = false;

  function em(t, v, b, e) {
    if (e === undefined) e = b + v.length;
    a.push({ t: t, v: v, s: b, e: e, l: l });
  }

  function sw() {
    while (i < n && (s[i] === ' ' || s[i] === '\t' || s[i] === '\n' || s[i] === '\r')) {
      if (s[i] === '\n') l++;
      i++;
    }
  }

  function sc() {
    if (s[i] === '/' && s[i + 1] === '/') {
      while (i < n && s[i] !== '\n') i++;
      return true;
    }
    if (s[i] === '/' && s[i + 1] === '*') {
      i += 2;
      while (i < n && !(s[i] === '*' && s[i + 1] === '/')) {
        if (s[i] === '\n') l++;
        i++;
      }
      i += 2;
      return true;
    }
    return false;
  }

  function sstr(q) {
    var b = i;
    i++;
    while (i < n && s[i] !== q) {
      if (s[i] === '\\') { if (s[i + 1] === '\n') l++; i += 2; }
      else i++;
    }
    if (i < n) i++;
    em('str', s.slice(b, i), b, i);
    lv = true;
  }

  function sreg() {
    var b = i, d = 0;
    i++;
    while (i < n) {
      if (s[i] === '\\') { i += 2; continue; }
      if (s[i] === '[') { d++; i++; continue; }
      if (s[i] === ']') { if (d > 0) d--; i++; continue; }
      if (s[i] === '/' && d === 0) { i++; break; }
      i++;
    }
    while (i < n && /[gimsuy]/.test(s[i])) i++;
    em('reg', s.slice(b, i), b, i);
    lv = true;
  }

  function snum() {
    var b = i;
    if (s[i] === '0' && (s[i + 1] === 'x' || s[i + 1] === 'X')) {
      i += 2;
      while (i < n && /[0-9a-fA-F_]/.test(s[i])) i++;
    } else if (s[i] === '0' && (s[i + 1] === 'o' || s[i + 1] === 'O')) {
      i += 2;
      while (i < n && /[0-7_]/.test(s[i])) i++;
    } else if (s[i] === '0' && (s[i + 1] === 'b' || s[i + 1] === 'B')) {
      i += 2;
      while (i < n && /[01_]/.test(s[i])) i++;
    } else {
      while (i < n && /[0-9_]/.test(s[i])) i++;
      if (i < n && s[i] === '.') { i++; while (i < n && /[0-9_]/.test(s[i])) i++; }
      if (i < n && (s[i] === 'e' || s[i] === 'E')) {
        i++;
        if (i < n && (s[i] === '+' || s[i] === '-')) i++;
        while (i < n && /[0-9_]/.test(s[i])) i++;
      }
    }
    if (i < n && s[i] === 'n') { i++; em('big', s.slice(b, i), b, i); }
    else em('num', s.slice(b, i), b, i);
    lv = true;
  }

  function stpl() {
    var b = i;
    while (i < n) {
      if (s[i] === '\\') { i += 2; continue; }
      if (s[i] === '$' && i + 1 < n && s[i + 1] === '{') {
        if (i > b) em('tpl', s.slice(b, i), b, i);
        em('tpl', '${', i, i + 2);
        i += 2;
        tm = 'expr';
        td = 0;
        return;
      }
      if (s[i] === '`') {
        if (i > b) em('tpl', s.slice(b, i), b, i);
        em('tpl', '`', i, i + 1);
        i++;
        var p = ts.pop();
        tm = p.m;
        td = p.d;
        if (tm === 'text') stpl();
        return;
      }
      if (s[i] === '\n') l++;
      i++;
    }
  }

  while (i < n) {
    if (tm === 'text') { stpl(); continue; }
    if (tm === 'expr') {
      if (s[i] === '{') { td++; em('p', '{', i, i + 1); i++; lv = false; continue; }
      if (s[i] === '}') {
        if (td === 0) {
          em('tpl', '}', i, i + 1);
          i++;
          tm = 'text';
          lv = true;
          continue;
        }
        td--;
        em('p', '}', i, i + 1);
        i++;
        lv = false;
        continue;
      }
      if (s[i] === '`') {
        ts.push({ m: tm, d: td });
        em('tpl', '`', i, i + 1);
        tm = 'text';
        i++;
        stpl();
        lv = true;
        continue;
      }
    }

    sw();
    if (i >= n) break;
    if (sc()) continue;
    if (i >= n) break;

    var c = s[i], b = i;

    if (c === '`') {
      ts.push({ m: tm, d: td });
      em('tpl', '`', i, i + 1);
      tm = 'text';
      i++;
      stpl();
      lv = true;
      continue;
    }
    if (c === '"' || c === "'") { sstr(c); continue; }
    if (/[0-9]/.test(c) || (c === '.' && i + 1 < n && /[0-9]/.test(s[i + 1]))) { snum(); continue; }
    if (c === '/' && !lv) { sreg(); continue; }

    if (c === '#') {
      i++;
      if (i < n && /[a-zA-Z_$]/.test(s[i])) {
        while (i < n && /[a-zA-Z0-9_$]/.test(s[i])) i++;
        em('id', s.slice(b, i), b, i);
        lv = true;
      } else {
        em('op', '#', b, i);
        lv = false;
      }
      continue;
    }

    if (/[a-zA-Z_$]/.test(c)) {
      while (i < n && /[a-zA-Z0-9_$]/.test(s[i])) i++;
      em('id', s.slice(b, i), b, i);
      lv = true;
      continue;
    }

    if (c === '.' && i + 1 < n && /[0-9]/.test(s[i + 1])) { snum(); continue; }
    if (c === '.' && i + 1 < n && s[i + 1] === '.') {
      if (i + 2 < n && s[i + 2] === '.') { em('op', '...', i, i + 3); i += 3; lv = false; continue; }
      em('op', '..', i, i + 2); i += 2; lv = false; continue;
    }

    var o2 = s.slice(i, i + 2), o3 = s.slice(i, i + 3);
    if (o3 === '===') { em('op', '===', i, i + 3); i += 3; lv = false; continue; }
    if (o3 === '!==') { em('op', '!==', i, i + 3); i += 3; lv = false; continue; }
    if (o3 === '>>>') { em('op', '>>>', i, i + 3); i += 3; lv = false; continue; }
    if (o2 === '?.') { em('op', '?.', i, i + 2); i += 2; lv = false; continue; }
    if (o2 === '==' || o2 === '!=' || o2 === '<=' || o2 === '>=' ||
        o2 === '&&' || o2 === '||' || o2 === '??' || o2 === '**' ||
        o2 === '<<' || o2 === '>>' || o2 === '=>') {
      em('op', o2, i, i + 2); i += 2; lv = false; continue;
    }
    if (o2 === '+=' || o2 === '-=' || o2 === '*=' || o2 === '/=' || o2 === '%=' ||
        o2 === '&=' || o2 === '|=' || o2 === '^=' || o2 === '**=' ||
        o2 === '<<=' || o2 === '>>=' || o2 === '&&=' || o2 === '||=' ||
        o2 === '??=' || o2 === '++' || o2 === '--') {
      em('op', o2, i, i + 2); i += 2; lv = (o2 === '++' || o2 === '--'); continue;
    }

    if ('(){}[].,;:'.indexOf(c) !== -1) {
      em('p', c, i, i + 1);
      i++;
      lv = (c === ')' || c === ']' || c === '}');
      continue;
    }
    if (c === '?' || c === '~' || c === '!' || c === '@') {
      em('op', c, i, i + 1); i++; lv = false; continue;
    }
    em('op', c, i, i + 1); i++; lv = false;
  }
  return a;
}

function dec(lt) {
  try { return (0, eval)(lt); } catch (e) { return lt.slice(1, -1); }
}

function emt(t, src) {
  var pm = new Map(), pi = 0;
  var directives = new Set(['"use strict"', "'use strict'"]);

  function isProp(tk) {
    return (tk.t === 'p' && tk.v === '.') || (tk.t === 'op' && tk.v === '?.');
  }

  var i;
  for (i = 0; i < t.length; i++) {
    var tk = t[i];
    if (tk.t === 'str') {
      if (i + 1 < t.length && t[i + 1].t === 'p' && t[i + 1].v === ':') continue;
      var unesc = dec(tk.v);
      if (directives.has(tk.v)) continue;
      if (!pm.has(unesc)) { pm.set(unesc, pi); pi++; }
    }
    if (isProp(tk) && i + 1 < t.length) {
      var nk = t[i + 1];
      if (nk.t === 'id' && !nk.v.startsWith('#')) {
        if (!pm.has(nk.v)) { pm.set(nk.v, pi); pi++; }
      }
    }
  }

  var blocked = new Set();
  for (i = 1; i < t.length; i++) {
    if (isProp(t[i - 1]) && t[i].t === 'id' && !t[i].v.startsWith('#')) {
      blocked.add(t[i].v);
    }
  }
  for (i = 0; i < t.length - 1; i++) {
    if (t[i].t === 'id' && t[i + 1].t === 'p' && t[i + 1].v === ':') blocked.add(t[i].v);
  }
  for (i = 0; i < t.length; i++) {
    if (t[i].t === 'id') {
      var pb = i > 0 ? t[i - 1] : null;
      var nx = i + 1 < t.length ? t[i + 1] : null;
      if (pb && pb.t === 'p' && (pb.v === '{' || pb.v === ',')) {
        if (nx && nx.t === 'p' && (nx.v === ',' || nx.v === '}')) blocked.add(t[i].v);
        if (nx && nx.t === 'op' && nx.v === '=') blocked.add(t[i].v);
      }
    }
  }
  for (i = 1; i < t.length; i++) {
    if (t[i - 1].t === 'id' && (t[i - 1].v === 'break' || t[i - 1].v === 'continue') && t[i].t === 'id') {
      blocked.add(t[i].v);
    }
  }
  for (i = 0; i < t.length; i++) {
    if (t[i].t === 'id' && t[i].v === 'class') {
      var j = i + 1;
      if (j < t.length && t[j].t === 'id') j++;
      if (j < t.length && t[j].t === 'id' && t[j].v === 'extends') {
        j++;
        var d = 0;
        while (j < t.length) {
          var te = t[j];
          if (te.t === 'p' && (te.v === '(' || te.v === '[' || te.v === '{')) d++;
          if (te.t === 'p' && (te.v === ')' || te.v === ']' || te.v === '}')) d--;
          if (d < 0) d = 0;
          if (te.t === 'p' && te.v === '{' && d === 0) break;
          j++;
        }
      }
      if (j < t.length && t[j].t === 'p' && t[j].v === '{') {
        var bd = 1, k = j + 1;
        while (k < t.length && bd > 0) {
          var tk2 = t[k];
          if (tk2.t === 'p' && tk2.v === '{') bd++;
          if (tk2.t === 'p' && tk2.v === '}') { bd--; k++; continue; }
          if (bd === 1 && tk2.t === 'id') {
            var mk = t[k - 1];
            if (mk.t === 'p' && (mk.v === '{' || mk.v === ';')) blocked.add(tk2.v);
            if (mk.t === 'id' && (mk.v === 'static' || mk.v === 'get' || mk.v === 'set' || mk.v === 'async')) blocked.add(tk2.v);
            if (mk.t === 'op' && mk.v === '*') blocked.add(tk2.v);
          }
          k++;
        }
      }
    }
  }

  var ngC = 0;
  var ngUsed = new Set();
  for (i = 0; i < t.length; i++) if (t[i].t === 'id') ngUsed.add(t[i].v);
  function ng() {
    var nm;
    do {
      var r = '', c = ngC;
      do {
        r = String.fromCharCode(97 + (c % 26)) + r;
        c = Math.floor(c / 26) - 1;
      } while (c >= 0);
      ngC++;
      nm = r;
    } while (ngUsed.has(nm) || RV.has(nm));
    ngUsed.add(nm);
    return nm;
  }

  var declared = new Set();
  var KD = new Set(['const', 'let', 'var']);
  for (i = 0; i < t.length; i++) {
    var tk0 = t[i];
    if (tk0.t !== 'id') continue;
    if (KD.has(tk0.v) || tk0.v === 'class' || tk0.v === 'catch') {
      if (i + 1 < t.length && t[i + 1].t === 'id') declared.add(t[i + 1].v);
    }
    if (tk0.v === 'function') {
      var j2 = i + 1;
      if (j2 < t.length && t[j2].t === 'op' && t[j2].v === '*') j2++;
      if (j2 < t.length && t[j2].t === 'id') declared.add(t[j2].v);
    }
    if (tk0.v === '=>') {
      if (i > 0 && t[i - 1].t === 'id') declared.add(t[i - 1].v);
    }
  }
  for (i = 0; i < t.length; i++) {
    if (t[i].t !== 'p' || t[i].v !== '(') continue;
    var isFunc = false;
    if (i > 0) {
      var lf = i > 0 ? t[i - 1] : null;
      var lf2 = i > 1 ? t[i - 2] : null;
      if (lf && lf.t === 'id' && lf.v === 'function') isFunc = true;
      if (lf && lf.t === 'op' && lf.v === '*' && lf2 && lf2.t === 'id' && lf2.v === 'function') isFunc = true;
      if (lf && lf.t === 'id' && lf2 && lf2.t === 'id' && lf2.v === 'function') isFunc = true;
    }
    var d0 = 0, j3 = i;
    while (j3 < t.length) {
      if (t[j3].t === 'p' && t[j3].v === '(') d0++;
      if (t[j3].t === 'p' && t[j3].v === ')') { d0--; if (d0 === 0) break; }
      j3++;
    }
    if (j3 >= t.length) continue;
    var post = j3 + 1 < t.length ? t[j3 + 1] : null;
    if (isFunc || (post && post.t === 'op' && post.v === '=>')) {
      var dd = 0;
      for (var q = i + 1; q < j3; q++) {
        var tq = t[q];
        if (tq.t === 'p' && (tq.v === '(' || tq.v === '[' || tq.v === '{')) dd++;
        if (tq.t === 'p' && (tq.v === ')' || tq.v === ']' || tq.v === '}')) dd--;
        if (dd === 0 && tq.t === 'id') declared.add(tq.v);
      }
    }
  }

  var rnMap = new Map();
  var seen = new Set();
  for (i = 0; i < t.length; i++) {
    var tk0 = t[i];
    if (tk0.t !== 'id') continue;
    if (tk0.v.startsWith('#')) continue;
    if (RV.has(tk0.v)) continue;
    if (blocked.has(tk0.v)) continue;
    if (!declared.has(tk0.v)) continue;
    if (seen.has(tk0.v)) continue;
    seen.add(tk0.v);
    rnMap.set(tk0.v, ng());
  }

  var poolArrN = ng();
  var poolFnN = ng();

  var pmArr = [];
  for (var kv of pm) {
    var k = kv[0];
    var h = "'";
    for (var j = 0; j < k.length; j++) {
      var cc = k.charCodeAt(j);
      if (cc < 128) h += '\\x' + cc.toString(16).padStart(2, '0');
      else h += '\\u' + cc.toString(16).padStart(4, '0');
    }
    h += "'";
    pmArr.push(h);
  }
  var helper = 'var ' + poolArrN + '=[' + pmArr.join(',') + '];var ' + poolFnN + '={v:function(z){return ' + poolArrN + '[z]}};';

  var xm = new Map();
  for (i = 0; i < t.length; i++) {
    var ntk = t[i];
    if (ntk.t !== 'num') continue;
    if (ntk.v.indexOf('n') !== -1) continue;
    var vv;
    try { vv = eval(ntk.v); } catch (e) { continue; }
    if (!Number.isFinite(vv)) continue;
    if (!Number.isInteger(vv)) continue;
    if (vv > 2147483647 || vv < -2147483648) continue;
    var aa = ((vv * 2654435761) >>> 0) || 1;
    var bb = (aa ^ (vv >>> 0)) >>> 0;
    if (aa === bb) aa = (aa ^ 0x9E3779B9) >>> 0;
    bb = (aa ^ (vv >>> 0)) >>> 0;
    if (aa === bb) aa = (aa ^ 0x5DEE66D) >>> 0;
    bb = (aa ^ (vv >>> 0)) >>> 0;
    xm.set(i, aa + '^' + bb);
  }

  var injectIdx = -1;
  for (i = 0; i < t.length; i++) {
    if (t[i].t === 'str' && (t[i].v === '"use strict"' || t[i].v === "'use strict'")) {
      injectIdx = i + 1;
      if (injectIdx < t.length && t[injectIdx].t === 'p' && t[injectIdx].v === ';') injectIdx++;
      break;
    }
    if (t[i].t !== 'tpl' && t[i].t !== 'str') { injectIdx = i; break; }
  }
  if (injectIdx === -1) injectIdx = 0;

  var o = '', ll = 1, injected = false, lastWord = false;
  function wd(ch) { return (ch >= 'a' && ch <= 'z') || (ch >= 'A' && ch <= 'Z') || (ch >= '0' && ch <= '9') || ch === '_' || ch === '$'; }
  function app(s) {
    if (s.length === 0) return;
    if (lastWord && wd(s[0])) o += ' ';
    o += s;
    lastWord = wd(s[s.length - 1]);
  }

  for (i = 0; i < t.length; i++) {
    var tk = t[i];

    if (!injected && i === injectIdx) {
      app(helper);
      injected = true;
    }

    if (tk.l > ll) {
      var gaps = tk.l - ll;
      for (var g = 0; g < gaps; g++) { o += '\n'; lastWord = false; }
      ll = tk.l;
    }

    if (xm.has(i)) {
      app('(' + xm.get(i) + ')');
      continue;
    }

    if (tk.t === 'id' && rnMap.has(tk.v)) {
      app(rnMap.get(tk.v));
      continue;
    }

    if (isProp(tk) && i + 1 < t.length) {
      var nk = t[i + 1];
      var prev = i > 0 ? t[i - 1] : null;
      var newMeta = prev && prev.t === 'id' && prev.v === 'new' && tk.v === '.';
      if (!newMeta && nk.t === 'id' && !nk.v.startsWith('#') && pm.has(nk.v)) {
        var useDot = tk.v === '.';
        var prefix = useDot ? '[' : '?.[';
        app(prefix + poolFnN + '.v(' + pm.get(nk.v) + ')]');
        i++;
        continue;
      }
    }

    if (tk.t === 'tpl') {
      if (tk.v === '${') { o += tk.v; lastWord = false; continue; }
      o += src.slice(tk.s, tk.e);
      lastWord = false;
      continue;
    }

    if (tk.t === 'str') {
      if (i + 1 < t.length && t[i + 1].t === 'p' && t[i + 1].v === ':') {
        app(src.slice(tk.s, tk.e));
        continue;
      }
      if (directives.has(tk.v)) {
        app(src.slice(tk.s, tk.e));
        continue;
      }
      var unesc = dec(tk.v);
      if (pm.has(unesc)) {
        app(poolFnN + '.v(' + pm.get(unesc) + ')');
        continue;
      }
    }

    app(src.slice(tk.s, tk.e));
  }

  if (!injected) o = helper + o;
  return o;
}

function run() {
  var args = process.argv.slice(2);
  if (args.length < 1) {
    console.error('su dung: node obf.js <file>');
    process.exit(1);
  }
  var fp = path.resolve(args[0]);
  if (!fs.existsSync(fp)) {
    console.error('file khong ton tai: ' + fp);
    process.exit(1);
  }
  var src = fs.readFileSync(fp, 'utf8');
  src = src.replace(/^\uFEFF/, '');
  var t = tok(src);
  var out = emt(t, src);
  var bn = path.basename(fp, path.extname(fp));
  var op = path.join(path.dirname(fp), bn + '_obf.js');
  fs.writeFileSync(op, out, 'utf8');
  console.log('da obfuscate: ' + op);
}

run();
