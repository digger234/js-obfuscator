const filesystem = require('fs');

const solo = new Set(['{', '}', '(', ')', '[', ']', ';', ',', '<', '>', '+', '-', '*', '/', '%', '&', '|', '^', '~', '!', '?', ':', '=', '.', '@', '#']);
const pair = new Set(['==', '!=', '<=', '>=', '&&', '||', '??', '?.', '++', '--', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '**', '<<', '>>', '=>']);
const trio = new Set(['===', '!==', '**=', '<<=', '>>=', '>>>', '...', '&&=', '||=', '??=']);
const quad = new Set(['>>>=']);
const opens = new Set(['if', 'for', 'while', 'switch', 'catch', 'with', 'do', 'else', 'try', 'finally']);
const terms = new Set(['return', 'typeof', 'instanceof', 'in', 'of', 'new', 'delete', 'void', 'throw', 'case', 'do', 'else', 'yield', 'await']);
const halt = new Set(['continue', 'break']);
const reserved = new Set(['if', 'for', 'while', 'switch', 'catch', 'with', 'do', 'else', 'try', 'finally', 'return', 'typeof', 'instanceof', 'in', 'of', 'new', 'delete', 'void', 'throw', 'case', 'yield', 'await', 'break', 'continue', 'this', 'super', 'class', 'function', 'var', 'let', 'const', 'true', 'false', 'null', 'undefined', 'default', 'extends', 'static', 'get', 'set', 'async', 'debugger', 'import', 'export']);
const clip = new Set(['(', '[', '.', '?.', ',', ':', '?', '=>', '...', '=', '+=', '-=', '*=', '/=', '%=', '**=', '&=', '|=', '^=', '<<=', '>>=', '>>>=', '&&=', '||=', '??=', '+', '-', '*', '/', '%', '**', '&', '|', '^', '<<', '>>', '>>>', '<', '>', '<=', '>=', '==', '!=', '===', '!==', '&&', '||', '??']);
const hard = new Set(['return', 'throw', 'break', 'continue', 'yield']);
const cantend = new Set(['if', 'for', 'while', 'switch', 'catch', 'with', 'do', 'else', 'try', 'finally', 'return', 'throw', 'break', 'continue', 'case', 'default', 'var', 'let', 'const', 'function', 'class', 'import', 'export', 'debugger', 'extends', 'new', 'in', 'of', 'get', 'set', 'static', 'async', 'super']);
const pick = [3, 5, 7, 11, 13];
const builtins = ['Object', 'Array', 'Math', 'JSON', 'console', 'Promise', 'Date', 'Symbol', 'Map', 'Set', 'WeakMap', 'WeakSet', 'Proxy', 'Reflect', 'BigInt', 'Number', 'String', 'Boolean', 'RegExp', 'Error', 'TypeError', 'RangeError', 'SyntaxError', 'EvalError', 'URIError', 'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'encodeURIComponent', 'decodeURIComponent', 'atob', 'btoa', 'TextEncoder', 'TextDecoder', 'URL', 'URLSearchParams', 'Buffer', 'Uint8Array', 'Uint16Array', 'Uint32Array', 'Int8Array', 'Int16Array', 'Int32Array', 'Float32Array', 'Float64Array', 'Uint8ClampedArray', 'BigInt64Array', 'BigUint64Array', 'ArrayBuffer', 'DataView'];
let seed = [90, 55, 195, 17, 158, 43, 116, 232];
const names = ['queue', 'letters', 'ord', 'decode', 'slot', 'cipher', 'mid', 'buffer', 'bits', 'pos', 'digit', 'keys', 'i', 'j', 'k', 'l', 'swap', 'out', 'checked', 'plaintext', 'cursor', 'byte', 'high', 'sbox', 'ring', 'turns', 'roll', 'steps', 'probe', 'tally'];

let counter = 0;
let quirk = 0;
const taken = new Set();
const have = new Set();
const truthy = ['!0', '!![]', '(0x1<0x2)'];
const falsy = ['!1', '![]', '(0x1>0x2)'];

function mint() {
  let n = '$' + counter.toString(16);
  while (taken.has(n)) {
    counter++;
    n = '$' + counter.toString(16);
  }
  counter++;
  taken.add(n);
  return n;
}

function isw(c) {
  return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c === '_' || c === '$';
}

function hval(s) {
  return parseInt(s, 16);
}

function esc(source, i) {
  const e = source[i + 1];
  if (e === 'n') return ['\n', i + 2];
  if (e === 't') return ['\t', i + 2];
  if (e === 'r') return ['\r', i + 2];
  if (e === 'b') return ['\b', i + 2];
  if (e === 'v') return ['\v', i + 2];
  if (e === 'f') return ['\f', i + 2];
  if (e === 'x') return [String.fromCharCode(hval(source.substr(i + 2, 2))), i + 4];
  if (e === 'u') {
    if (source[i + 2] === '{') {
      const cl = source.indexOf('}', i + 3);
      return [String.fromCodePoint(hval(source.slice(i + 3, cl))), cl + 1];
    }
    return [String.fromCharCode(hval(source.substr(i + 2, 4))), i + 6];
  }
  if (e === '\n') return ['', i + 2];
  if (e === '0') {
    if (source[i + 2] >= '0' && source[i + 2] <= '7') {
      let j = i + 2;
      let cnt = 1;
      let val = 0;
      while (cnt < 3 && source[j] >= '0' && source[j] <= '7') {
        val = val * 8 + (source.charCodeAt(j) - 48);
        j++;
        cnt++;
      }
      return [String.fromCharCode(val), j];
    }
    return ['\0', i + 2];
  }
  return [e, i + 2];
}

function lex(source) {
  const output = [];
  const frames = [];
  let i = 0;
  let newline = false;
  const size = source.length;
  const record = (k, v) => {
    output.push({ k, v, newline });
    newline = false;
  };
  const tail = () => output[output.length - 1];
  function quote(q) {
    const start = i;
    i++;
    let cooked = '';
    while (i < size) {
      const c = source[i];
      if (c === q) {
        i++;
        break;
      }
      if (c === '\\') {
        const r = esc(source, i);
        cooked += r[0];
        i = r[1];
        continue;
      }
      if (c === '\n') throw new Error('Chuỗi chưa đóng trong file đầu vào');
      cooked += c;
      i++;
    }
    record('str', source.slice(start, i));
    tail().c = cooked;
  }
  function temp(head) {
    const pre = head ? '`' : '}';
    if (head) {
      frames.push({ d: 0 });
      i++;
    }
    let raw = '';
    while (i < size) {
      const c = source[i];
      if (c === '\\') {
        raw += source[i] + source[i + 1];
        i += 2;
        continue;
      }
      if (c === '`') {
        i++;
        record('ttail', pre + raw + '`');
        frames.pop();
        return;
      }
      if (c === '$' && source[i + 1] === '{') {
        i += 2;
        record(head ? 'thead' : 'tmid', pre + raw + '${');
        return;
      }
      raw += c;
      i++;
    }
    throw new Error('Template chưa đóng trong file đầu vào');
  }
  function whole() {
    const start = i;
    if (source[i] === '0' && 'xXbBoO'.indexOf(source[i + 1]) >= 0) {
      i += 2;
      while (i < size && (isw(source[i]) || source[i] === '_')) i++;
    } else {
      while (i < size && ((source[i] >= '0' && source[i] <= '9') || source[i] === '_')) i++;
      if (source[i] === '.' && source[i + 1] >= '0' && source[i + 1] <= '9') {
        i++;
        while (i < size && ((source[i] >= '0' && source[i] <= '9') || source[i] === '_')) i++;
      }
      if (source[i] === 'e' || source[i] === 'E') {
        i++;
        if (source[i] === '+' || source[i] === '-') i++;
        while (i < size && source[i] >= '0' && source[i] <= '9') i++;
      }
    }
    let big = false;
    if (source[i] === 'n' && isw(source[i - 1]) && !isw(source[i + 1])) {
      big = true;
      i++;
    }
    const raw = source.slice(start, i);
    record('num', raw);
    tail().big = big;
    tail().n = big ? null : Number(raw.replace(/_/g, ''));
  }
  function ident() {
    const start = i;
    while (i < size && isw(source[i])) i++;
    record('name', source.slice(start, i));
  }
  function quest() {
    const p = tail();
    if (!p) return true;
    if (p.k === 'name') return terms.has(p.v);
    if (p.k === 'num' || p.k === 'str' || p.k === 'ttail' || p.k === 'regex') return false;
    if (p.k === 'punc') return !(p.v === ')' || p.v === ']' || p.v === '++' || p.v === '--');
    return true;
  }
  function rx() {
    i++;
    let raw = '/';
    let cls = false;
    while (i < size) {
      const c = source[i];
      if (c === '\\') {
        raw += source[i] + source[i + 1];
        i += 2;
        continue;
      }
      if (c === '[') cls = true;
      else if (c === ']') cls = false;
      else if (c === '/' && !cls) {
        raw += '/';
        i++;
        break;
      } else if (c === '\n') throw new Error('Regex chưa đóng trong file đầu vào');
      raw += c;
      i++;
    }
    while (i < size && source[i] >= 'a' && source[i] <= 'z') {
      raw += source[i];
      i++;
    }
    record('regex', raw);
  }
  function sym() {
    for (const l of [4, 3, 2, 1]) {
      const t = source.substr(i, l);
      const ok = l === 4 ? quad.has(t) : l === 3 ? trio.has(t) : l === 2 ? pair.has(t) : solo.has(t);
      if (!ok) continue;
      if (t === '{' && frames.length) frames[frames.length - 1].d++;
      else if (t === '}') {
        if (frames.length && frames[frames.length - 1].d === 0) {
          i += 1;
          temp(false);
          return;
        }
        if (frames.length) frames[frames.length - 1].d--;
      }
      i += l;
      record('punc', t);
      return;
    }
    const lt = output[output.length - 1];
    throw new Error('Ký tự lạ tại ' + i + ': ' + JSON.stringify(source.slice(i - 20, i + 10)) + ' sau token ' + JSON.stringify(lt));
  }
  while (i < size) {
    const c = source[i];
    if (c === '\n' || c === '\u2028' || c === '\u2029') {
      newline = true;
      i++;
      continue;
    }
    if (c === ' ' || c === '\t' || c === '\r' || c === '\uFEFF' || c === '\u00A0' || c === '\u000B' || c === '\u000C') {
      i++;
      continue;
    }
    if (c === '/' && source[i + 1] === '/') {
      while (i < size && source[i] !== '\n') i++;
      continue;
    }
    if (c === '/' && source[i + 1] === '*') {
      i += 2;
      while (i < size && !(source[i] === '*' && source[i + 1] === '/')) {
        if (source[i] === '\n') newline = true;
        i++;
      }
      i += 2;
      continue;
    }
    if (c === '"' || c === "'") {
      quote(c);
      continue;
    }
    if (c === '`') {
      temp(true);
      continue;
    }
    if (c >= '0' && c <= '9') {
      whole();
      continue;
    }
    if (c === '.' && source[i + 1] >= '0' && source[i + 1] <= '9') {
      whole();
      continue;
    }
    if (isw(c)) {
      ident();
      continue;
    }
    if (c === '/') {
      if (quest()) rx();
      else sym();
      continue;
    }
    sym();
  }
  return output;
}

function pairs(tokens) {
  const m = {};
  const stack = [];
  for (let i = 0; i < tokens.length; i++) {
    if (tokens[i].k !== 'punc') continue;
    const v = tokens[i].v;
    if (v === '(' || v === '[' || v === '{') stack.push(i);
    else if (v === ')' || v === ']' || v === '}') {
      const o = stack.pop();
      m[o] = i;
      m[i] = o;
    }
  }
  return m;
}

function adjacent(tokens, i) {
  for (let d = i - 1; d >= 0 && d > i - 6; d--) {
    if (tokens[d].v === 'class' && tokens[d].k === 'name') return true;
  }
  return false;
}

function kinds(tokens, links) {
  const r = {};
  const stack = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'punc') continue;
    if (t.v === '}') {
      stack.pop();
      continue;
    }
    if (t.v !== '{') continue;
    const p = tokens[i - 1];
    let kind = 'block';
    if (p && p.k === 'punc' && p.v === ')') {
      const q = links[i - 1];
      const b = q !== undefined ? tokens[q - 1] : null;
      if (b && b.k === 'name' && opens.has(b.v)) kind = 'block';
      else if (b && b.k === 'name') kind = 'function';
      else if (b && (b.v === 'function' || b.v === ']' || b.v === '*')) kind = 'function';
      else kind = 'block';
    } else if (p && p.k === 'punc' && p.v === '=>') kind = 'function';
    else if (p && p.k === 'name') {
      if (adjacent(tokens, i)) kind = 'class';
      else if (opens.has(p.v)) kind = 'block';
      else if (terms.has(p.v)) kind = 'object';
      else kind = 'block';
    } else if (p && p.k === 'punc') {
      if (p.v === ':') {
        const top = stack[stack.length - 1];
        kind = top !== undefined && r[top] === 'object' ? 'object' : 'block';
      } else if (p.v === '}' || p.v === ';' || p.v === '{') kind = 'block';
      else kind = 'object';
    } else kind = 'block';
    r[i] = kind;
    stack.push(i);
  }
  return r;
}

function delim(tokens, a, b, stop) {
  let d = 0;
  for (let j = a; j <= b; j++) {
    const v = tokens[j].v;
    if (tokens[j].k !== 'punc') continue;
    if (v === '(' || v === '[' || v === '{') d++;
    else if (v === ')' || v === ']' || v === '}') {
      if (d === 0) return j;
      d--;
    } else if (v === stop && d === 0) return j;
  }
  return -1;
}

function closure(tokens, i, len) {
  let d = 0;
  for (let j = i + 1; j < len; j++) {
    const v = tokens[j].v;
    if (tokens[j].k !== 'punc') continue;
    if (v === '(' || v === '[' || v === '{') d++;
    else if (v === ')' || v === ']' || v === '}') {
      if (d === 0) return j;
      d--;
    } else if ((v === ',' || v === ';') && d === 0) return j;
  }
  return len - 1;
}

function grip(tokens, i, links, len) {
  const prev = tokens[i - 1];
  let s;
  let params = [];
  if (prev && prev.k === 'punc' && prev.v === ')') {
    const q = links[i - 1];
    s = q + 1;
    let d = 0;
    for (let j = q + 1; j < i - 1; j++) {
      const v = tokens[j].v;
      if (tokens[j].k === 'punc') {
        if (v === '(' || v === '[' || v === '{') d++;
        else if (v === ')' || v === ']' || v === '}') d--;
      }
      if (d !== 0 || tokens[j].k !== 'name') continue;
      const next = tokens[j + 1];
      if (next && next.k === 'punc' && (next.v === ',' || next.v === ')')) params.push({ name: tokens[j].v, pos: j });
      else if (next && next.k === 'punc' && next.v === '=') {
        const stop = delim(tokens, j + 2, i - 2, ',');
        params.push({ name: tokens[j].v, pos: j });
        j = stop < 0 ? i - 1 : stop;
      }
    }
  } else if (prev && prev.k === 'name' && !opens.has(prev.v) && !terms.has(prev.v)) {
    s = i - 1;
    params = [{ name: prev.v, pos: i - 1 }];
  } else return null;
  let e;
  const next = tokens[i + 1];
  if (next && next.k === 'punc' && next.v === '{') e = links[i + 1];
  else e = closure(tokens, i, len);
  return { s, e, params };
}

function edge(tokens, i, links, len) {
  const o = i + 1;
  const cl = links[o];
  let has = false;
  let dep = 1;
  for (let j = o + 1; j < cl; j++) {
    const v = tokens[j].v;
    if (tokens[j].k === 'punc') {
      if (v === '(' || v === '[' || v === '{') dep++;
      else if (v === ')' || v === ']' || v === '}') dep--;
    }
    if (dep === 1 && tokens[j].k === 'name' && (tokens[j].v === 'let' || tokens[j].v === 'const')) has = true;
  }
  if (!has) return null;
  let e;
  const next = tokens[cl + 1];
  if (next && next.k === 'punc' && next.v === '{') e = links[cl + 1];
  else if (next && next.k === 'punc' && next.v === ';') e = cl + 1;
  else {
    let d = 0;
    e = len - 1;
    for (let j = cl + 1; j < len; j++) {
      const v = tokens[j].v;
      if (tokens[j].k !== 'punc') continue;
      if (v === '(' || v === '[' || v === '{') d++;
      else if (v === ')' || v === ']' || v === '}') d--;
      else if (v === ';' && d === 0) {
        e = j;
        break;
      }
    }
  }
  return { s: o, e };
}

function scopes(tokens, links, shapes, wrap) {
  const len = tokens.length;
  const owner = new Array(len);
  const guarded = new Array(len).fill(0);
  const entries = [];
  const global = { s: -1, e: len + 99, k: wrap ? 'fun' : 'blk', parent: null, d: new Map(), tainted: false };
  const stack = [global];
  const ranges = [];
  for (let i = 0; i < len; i++) {
    if (tokens[i].k === 'name' && tokens[i].v === 'for' && tokens[i + 1] && tokens[i + 1].k === 'punc' && tokens[i + 1].v === '(') {
      const loop = edge(tokens, i, links, len);
      if (loop) ranges.push({ s: loop.s, e: loop.e, scope: { s: loop.s, e: loop.e, k: 'blk', parent: null, d: new Map(), tainted: false } });
    }
    if (tokens[i].k === 'punc' && tokens[i].v === '=>') {
      const dart = grip(tokens, i, links, len);
      if (!dart) continue;
      const scope = { s: dart.s, e: dart.e, k: 'blk', parent: null, d: new Map(), tainted: false };
      for (const p of dart.params) {
        const entry = { name: p.name, pos: p.pos, kind: 'par', rename: true, fresh: null };
        if (!scope.d.has(p.name)) scope.d.set(p.name, []);
        scope.d.get(p.name).push(entry);
        entries.push(entry);
      }
      ranges.push({ s: dart.s, e: dart.e, scope });
    }
  }
  ranges.sort((a, b) => a.s - b.s);
  const enter = (scope, name, pos, kind, rename) => {
    let soar = scope;
    while (soar) {
      if (soar.tainted) rename = false;
      soar = soar.parent;
    }
    const entry = { name, pos, kind, rename, fresh: null };
    if (!scope.d.has(name)) scope.d.set(name, []);
    scope.d.get(name).push(entry);
    entries.push(entry);
    return entry;
  };
  const bindings = (scope, a, b) => {
    let d = 0;
    for (let j = a; j <= b; j++) {
      const t = tokens[j];
      if (t.k === 'punc') {
        if (t.v === '(' || t.v === '[' || t.v === '{') d++;
        else if (t.v === ')' || t.v === ']' || t.v === '}') d--;
        continue;
      }
      if (d < 1 || t.k !== 'name') continue;
      const next = tokens[j + 1];
      if (next && next.k === 'punc' && next.v === ':') continue;
      enter(scope, t.v, j, 'pat', false);
    }
  };
  const formals = (scope, q, close) => {
    let d = 0;
    for (let j = q + 1; j < close; j++) {
      const w = tokens[j];
      if (w.k === 'punc') {
        if (w.v === '(' || w.v === '[' || w.v === '{') {
          d++;
          if (w.v === '{' || w.v === '[') {
            const cl = links[j];
            bindings(scope, j, cl);
            j = cl;
            d--;
          }
          continue;
        }
        if (w.v === ')' || w.v === ']' || w.v === '}') {
          if (d === 0) continue;
          d--;
        }
        continue;
      }
      if (d === 0 && w.k === 'name') {
        const next = tokens[j + 1];
        const prev = tokens[j - 1];
        if (prev && prev.v === '...') {
          enter(scope, w.v, j, 'par', false);
          continue;
        }
        if (next && next.k === 'punc' && (next.v === ',' || next.v === ')')) enter(scope, w.v, j, 'par', true);
        else if (next && next.k === 'punc' && next.v === '=') {
          enter(scope, w.v, j, 'par', true);
          const stop = delim(tokens, j + 2, close - 1, ',');
          j = stop < 0 ? close - 1 : stop;
        }
      }
    }
  };
  const dub = (scope, q) => {
    const b = tokens[q - 1];
    if (b && b.v === 'catch') {
      const c = tokens[q + 1];
      if (c && c.k === 'name') enter(scope, c.v, q + 1, 'par', true);
      return null;
    }
if (b && b.k === 'name' && b.v !== 'get' && b.v !== 'set' && b.v !== 'static') {
    let ki = q - 2;
    if (tokens[ki] && tokens[ki].k === 'punc' && tokens[ki].v === '*') ki--;
    if (tokens[ki] && tokens[ki].k === 'name' && tokens[ki].v === 'async') ki--;
    if (!tokens[ki] || tokens[ki].k !== 'name' || tokens[ki].v !== 'function') return b;
    const p = tokens[ki - 1];
    if (!p || (p.k === 'punc' && (p.v === ';' || p.v === '{' || p.v === '}')) || (p.k === 'name' && (p.v === 'else' || p.v === 'do'))) return b;
    enter(scope, b.v, q - 1, 'expr', false);
  }
    return b;
  };
  const declarations = (i, top, glob) => {
    const v = tokens[i].v;
    let tgt = top;
    if (v === 'var') {
      let soar = top;
      while (soar && soar.k !== 'fun') soar = soar.parent;
      tgt = soar || glob;
    }
    const next = tokens[i + 1];
    if (next && next.k === 'punc' && (next.v === '{' || next.v === '[')) {
      const cl = links[i + 1];
      guarded.fill(1, i, cl + 1);
      bindings(tgt, i + 1, cl);
      return cl;
    }
    let d = 0;
    for (let j = i + 1; j < tokens.length; j++) {
      const w = tokens[j];
      if (w.k === 'punc') {
        const wv = w.v;
        if (wv === '(' || wv === '[' || wv === '{') d++;
        else if (wv === ')' || wv === ']' || wv === '}') {
          if (d === 0) break;
          d--;
        } else if (wv === ';' && d === 0) break;
        continue;
      }
      if (d !== 0 || w.k !== 'name') continue;
      const next = tokens[j + 1];
      if (!next) break;
      if (next.k === 'punc' && (next.v === '=' || next.v === ',' || next.v === ';')) {
        enter(tgt, w.v, j, v === 'var' ? 'var' : 'let', true);
        if (next.v === ';') break;
        if (next.v === '=') {
          const stop = delim(tokens, j + 2, tokens.length - 1, ',');
          const semi = delim(tokens, j + 2, tokens.length - 1, ';');
          j = Math.min(stop < 0 ? tokens.length : stop, semi < 0 ? tokens.length : semi) - 1;
        }
      } else if (next.k === 'name' && (next.v === 'of' || next.v === 'in')) {
        enter(tgt, w.v, j, v === 'var' ? 'var' : 'let', true);
        break;
      } else if (next.k === 'punc' && next.v === ')') {
        enter(tgt, w.v, j, v === 'var' ? 'var' : 'let', true);
        break;
      }
    }
    return -1;
  };
  let ri = 0;
  for (let i = 0; i < len; i++) {
    while (stack.length > 1 && stack[stack.length - 1].e === i) stack.pop();
    while (ri < ranges.length && ranges[ri].s === i) {
      ranges[ri].scope.parent = stack[stack.length - 1];
      stack.push(ranges[ri].scope);
      ri++;
    }
    const t = tokens[i];
    const top = stack[stack.length - 1];
    owner[i] = top;
    if (t.k === 'punc') {
      const v = t.v;
      if (v === '(') {
        const cl = links[i];
        const cs = tokens[cl + 1];
        if (cs && cs.k === 'punc' && cs.v === '{' && shapes[cl + 1] === 'function') {
          const scope = { s: i, e: links[cl + 1], k: 'function', parent: top, d: new Map(), tainted: false };
          stack.push(scope);
        }
        continue;
      }
      if (v === '{') {
      const p = tokens[i - 1];
      if (shapes[i] === 'function' && p && p.v === ')') {
        const q = links[i - 1];
        const scope = stack.length > 1 ? stack[stack.length - 1] : null;
        if (scope && scope.s === q && scope.k === 'function') {
          dub(scope, q);
          formals(scope, q, i - 1);
        } else {
          stack.push({ s: i, e: links[i], k: 'function', parent: top, d: new Map(), tainted: false });
          dub(stack[stack.length - 1], q);
          formals(stack[stack.length - 1], q, i - 1);
        }
        continue;
      }
      const scope = { s: i, e: links[i], k: shapes[i], parent: top, d: new Map(), tainted: false };
      stack.push(scope);
      continue;
    }
    if (v === '}') continue;
    }
    const v = t.v;
    if (v === 'let' || v === 'const' || v === 'var') {
      const stop = declarations(i, top, global);
      if (stop >= 0) i = stop;
      continue;
    }
    if (v === 'function') {
      let p = tokens[i - 1];
      if (p && p.k === 'name' && p.v === 'async') p = tokens[i - 2];
      const decl = !p || (p.k === 'punc' && (p.v === ';' || p.v === '{' || p.v === '}')) || (p.k === 'name' && (p.v === 'else' || p.v === 'do'));
      if (!decl) continue;
      let ni = i + 1;
      if (tokens[ni] && tokens[ni].v === '*' && tokens[ni].k === 'punc') ni++;
      const n = tokens[ni];
      if (n && n.k === 'name' && !terms.has(n.v) && !opens.has(n.v)) enter(top, n.v, ni, top.k === 'fun' ? 'fun' : 'fnb', true);
      continue;
    }
    if (v === 'class') {
      const n = tokens[i + 1];
      if (n && n.k === 'name' && n.v !== 'extends') enter(top, n.v, i + 1, 'cls', false);
      continue;
    }
  }
  return { owner, guarded, entries };
}

function state(tokens, shapes) {
  const r = new Array(tokens.length).fill('top');
  const stack = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k === 'punc') {
      if (t.v === '(') {
        stack.push('p');
        continue;
      }
      if (t.v === '[') {
        stack.push('a');
        continue;
      }
      if (t.v === '{') {
        stack.push(shapes[i] === 'object' ? 'obj' : 'o');
        continue;
      }
      if (t.v === ')' || t.v === ']' || t.v === '}') {
        stack.pop();
        continue;
      }
    }
    r[i] = stack.length ? stack[stack.length - 1] : 'top';
  }
  return r;
}

function resolve(info, tokens, i) {
  const t = tokens[i];
  if (t.k !== 'name') return null;
  let scope = info.owner[i];
  while (scope) {
    const list = scope.d.get(t.v);
    if (list && list.length) {
      let pick = null;
      for (const entry of list) {
        if (entry.pos <= i && (!pick || entry.pos > pick.pos)) pick = entry;
      }
      if (!pick) {
        for (const entry of list) {
          if (entry.kind === 'var' || entry.kind === 'fun') {
            pick = entry;
            break;
          }
        }
      }
      if (!pick) pick = list[0];
      return pick;
    }
    scope = scope.parent;
  }
  return null;
}

function shield(tokens, info, mode) {
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'name') continue;
    const pva = tokens[i - 1];
    if (!pva || pva.k !== 'punc' || (pva.v !== '{' && pva.v !== ',')) continue;
    const nxa = tokens[i + 1];
    if (!nxa || nxa.k !== 'punc' || (nxa.v !== ',' && nxa.v !== '}')) continue;
    if (mode[i] === 'obj' || mode[i] === 'top') continue;
    const entry = resolve(info, tokens, i);
    if (entry && entry.rename) entry.rename = false;
  }
}

function apply(tokens, info, links, mode) {
  for (const entry of info.entries) {
    if (entry.rename) entry.fresh = mint();
  }
  for (let i = tokens.length - 1; i >= 0; i--) {
    const t = tokens[i];
    if (t.k !== 'name') continue;
    if (reserved.has(t.v)) continue;
    if (info.guarded[i]) continue;
    const prev = tokens[i - 1];
    if (prev && prev.k === 'punc' && (prev.v === '.' || prev.v === '?.' || prev.v === '#')) continue;
    if (prev && prev.k === 'name' && halt.has(prev.v)) continue;
    const next = tokens[i + 1];
    if (next && next.k === 'punc' && next.v === ':') {
      if (mode[i] === 'obj') continue;
      if (i === 0 || (prev && ((prev.k === 'punc' && (prev.v === ';' || prev.v === '{' || prev.v === '}')) || (prev.k === 'name' && (prev.v === 'do' || prev.v === 'else'))))) continue;
    }
    if (next && next.k === 'punc' && next.v === '(' && mode[i] === 'obj') {
      const cl = links[i + 1];
      if (cl !== undefined && tokens[cl + 1] && tokens[cl + 1].v === '{') continue;
    }
    let entry = info.entries.find((e) => e.pos === i);
    if (!entry) entry = resolve(info, tokens, i);
    if (!entry || !entry.fresh) continue;
    const mb = prev && prev.k === 'punc' && (prev.v === '{' || prev.v === ',');
    if (mb && next && next.k === 'punc' && (next.v === ',' || next.v === '}') && mode[i] === 'obj') {
      tokens.splice(i + 1, 0, { k: 'punc', v: ':', newline: false }, { k: 'name', v: entry.fresh, newline: false });
      info.guarded.splice(i + 1, 0, 0, 0);
      continue;
    }
    t.v = entry.fresh;
  }
}

function rename(tokens, info, links, mode) {
  shield(tokens, info, mode);
  apply(tokens, info, links, mode);
}

function numbers(tokens) {
  const encode = (n, d) => {
    if (n < 16) return '0x' + n.toString(16);
    if (d > 12) {
      const hi = Math.floor(n / 0x80000000);
      const lo = n % 0x80000000;
      return '((' + encode(hi, 0) + '*0x80000000)+' + encode(lo, 0) + ')';
    }
    const p = pick[n % 5];
    const q = Math.floor(n / p);
    const r = n % p;
    return '((' + encode(q, d + 1) + '*0x' + p.toString(16) + ')+' + encode(r, d + 1) + ')';
  };
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'num' || t.big) continue;
    if (!Number.isSafeInteger(t.n)) continue;
    const prev = tokens[i - 1];
    if (prev && prev.k === 'punc' && (prev.v === '.' || prev.v === '#')) continue;
    const next = tokens[i + 1];
    if (next && next.k === 'punc' && next.v === ':') continue;
    t.v = encode(t.n, 0);
  }
}

function bools(tokens, info) {
  let shadow = false;
  for (const entry of info.entries) {
    if (entry.name === 'undefined') shadow = true;
  }
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'name') continue;
    if (t.v !== 'true' && t.v !== 'false' && t.v !== 'undefined') continue;
    const prev = tokens[i - 1];
    if (prev && prev.k === 'punc' && (prev.v === '.' || prev.v === '?.' || prev.v === '#')) continue;
    const next = tokens[i + 1];
    if (next && next.k === 'punc' && next.v === ':') continue;
    if (info.guarded[i]) continue;
    if (t.v === 'true') {
      t.v = truthy[quirk % truthy.length];
      quirk++;
    } else if (t.v === 'false') {
      t.v = falsy[quirk % falsy.length];
      quirk++;
    } else if (!shadow) t.v = 'void 0';
  }
}

function members(tokens, guarded) {
  const cut = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'punc') continue;
    if (t.v !== '.' && t.v !== '?.') continue;
    const next = tokens[i + 1];
    if (!next || next.k !== 'name') continue;
    const prev = tokens[i - 1];
    if (prev && prev.k === 'name' && (prev.v === 'new' || prev.v === 'import')) continue;
    cut.push([i, t.v, next.v]);
  }
  for (let c = cut.length - 1; c >= 0; c--) {
    const [i, dt, name] = cut[c];
    if (dt === '?.') {
      tokens.splice(i, 2, { k: 'punc', v: '?.', newline: false }, { k: 'punc', v: '[', newline: false }, { k: 'str', v: "'" + name + "'", c: name, newline: false }, { k: 'punc', v: ']', newline: false });
      guarded.splice(i, 2, 0, 0, 0, 0);
    } else {
      tokens.splice(i, 2, { k: 'punc', v: '[', newline: false }, { k: 'str', v: "'" + name + "'", c: name, newline: false }, { k: 'punc', v: ']', newline: false });
      guarded.splice(i, 2, 0, 0, 0);
    }
  }
}

function dispatch(segs, step, tick) {
  const ord = [];
  for (let j = 0; j < segs.length; j++) ord.push(String(j));
  let txt = 'var ' + step + "='" + ord.join('|') + "'.split('|')," + tick + '=0x0;while(!![]){switch(' + step + '[' + tick + '++]){';
  for (let j = 0; j < segs.length; j++) txt += "case '" + j + "':'\u0001" + j + "\u0001';continue;";
  txt += "case 'x':0x0;continue;";
  txt += '}break;}';
  return txt;
}

function flatten(tokens, guarded) {
  const links = pairs(tokens);
  const shapes = kinds(tokens, links);
  const bodies = [];
  for (const k of Object.keys(shapes)) {
    const o = Number(k);
    if (shapes[o] === 'function') bodies.push([o, links[o]]);
  }
  bodies.sort((a, b) => b[0] - a[0]);
  const adj = [];
  const shift = (x) => {
    let t = 0;
    for (const a of adj) if (a.p < x) t += a.d;
    return t;
  };
  for (const [from, til] of bodies) {
    const o = from + shift(from);
    const c = til + shift(til);
    let bad = false;
    let dep = 0;
    let segs = [];
    let cursor = [];
    const first = tokens[o + 1];
    if (first && first.k === 'str' && first.c === 'use strict') continue;
    for (let j = o + 1; j < c; j++) {
      const t = tokens[j];
      if (t.k === 'name' && (t.v === 'break' || t.v === 'continue')) {
        bad = true;
        break;
      }
      if (t.k === 'punc') {
        if (t.v === '(' || t.v === '[' || t.v === '{') dep++;
        else if (t.v === ')' || t.v === ']' || t.v === '}') dep--;
        else if (t.v === ';' && dep === 0) {
          const next = tokens[j + 1];
          if (next && next.k === 'name' && next.v === 'else') continue;
          segs.push(cursor);
          cursor = [];
          continue;
        }
      }
      if (dep === 0 && t.k === 'name' && (t.v === 'function' || t.v === 'class' || t.v === 'let' || t.v === 'const')) {
        bad = true;
        break;
      }
      if (dep === 0 && t.k === 'punc' && t.v === ':' && tokens[j - 1] && tokens[j - 1].k === 'name' && tokens[j - 2] && tokens[j - 2].k === 'punc' && (tokens[j - 2].v === ';' || tokens[j - 2].v === '{' || tokens[j - 2].v === '}')) {
        bad = true;
        break;
      }
      cursor.push(t);
    }
    if (bad) continue;
    segs.push(cursor);
    segs = segs.filter((s) => s.length > 0);
    if (segs.length < 2) continue;
    const step = mint();
    const tick = mint();
    const parts = lex(dispatch(segs, step, tick));
    const fresh = [];
    for (const t of parts) {
      if (t.k === 'str' && t.v.length >= 3 && t.v[1] === '\u0001') {
        const si = Number(t.v.slice(2, -2));
        for (const tk of segs[si]) fresh.push(tk);
        fresh.push({ k: 'punc', v: ';', newline: false });
      } else fresh.push(t);
    }
    const zeros = new Array(fresh.length).fill(0);
    tokens.splice(o + 1, c - o - 1, ...fresh);
    guarded.splice(o + 1, c - o - 1, ...zeros);
    adj.push({ p: o + 1, d: fresh.length - (c - o - 1) });
  }
}

function labels(tokens, guarded) {
  const links = pairs(tokens);
  const shapes = kinds(tokens, links);
  const mode = state(tokens, shapes);
  for (let i = tokens.length - 1; i >= 0; i--) {
    const t = tokens[i];
    if (t.k !== 'name' || mode[i] !== 'obj') continue;
    if (t.v === '__proto__') continue;
    const b = tokens[i - 1];
    if (!b || b.k !== 'punc' || (b.v !== '{' && b.v !== ',')) continue;
    const nxa = tokens[i + 1];
    if (!nxa || nxa.k !== 'punc' || (nxa.v !== ':' && nxa.v !== '(')) continue;
    tokens.splice(i, 1, { k: 'punc', v: '[', newline: false }, { k: 'str', v: "'" + t.v + "'", c: t.v, newline: false }, { k: 'punc', v: ']', newline: false });
    guarded.splice(i, 1, 0, 0, 0);
  }
}

function collect(tokens, guarded) {
  const map = new Map();
  const list = [];
  const q = (s) => "'" + s.replace(/\\/g, '\\\\').replace(/'/g, "\\'") + "'";
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'str') continue;
    if (t.c === 'use strict' || t.c === 'use asm') continue;
    if (guarded[i]) continue;
const pa = tokens[i - 1];
  const fn = tokens[i + 1];
  if (pa && pa.k === 'punc' && (pa.v === '{' || pa.v === ',') && fn && fn.k === 'punc' && fn.v === ':') continue;
  if (pa && pa.k === 'name' && (pa.v === 'import' || pa.v === 'export' || pa.v === 'from' || pa.v === 'as')) continue;
    if (t.c.length > 24) {
      const half = (t.c.length + 1) >> 1;
      const lo = t.c.slice(0, half);
      const hi = t.c.slice(half);
      tokens.splice(i, 1,
        { k: 'str', v: q(lo), c: lo, newline: false },
        { k: 'punc', v: '+', newline: false },
        { k: 'str', v: q(hi), c: hi, newline: false });
      guarded.splice(i, 1, 0, 0, 0);
      continue;
    }
    let ord = map.get(t.c);
    if (ord === undefined) {
      ord = list.length;
      list.push(t.c);
      map.set(t.c, ord);
    }
    tokens.splice(i, 1, { k: 'name', v: '\u0002', newline: t.newline }, { k: 'punc', v: '(', newline: false }, { k: 'num', v: '\u0003' + ord, newline: false }, { k: 'punc', v: ')', newline: false });
    guarded.splice(i, 1, 0, 0, 0, 0);
    i += 3;
  }
  return list;
}

function unicode(s) {
  const output = [];
  for (let i = 0; i < s.length; i++) {
    let c = s.charCodeAt(i);
    if (c >= 0xd800 && c <= 0xdbff && i + 1 < s.length) {
      const d = s.charCodeAt(i + 1);
      if (d >= 0xdc00 && d <= 0xdfff) {
        c = 0x10000 + ((c - 0xd800) << 10) + (d - 0xdc00);
        i++;
      }
    }
    if (c < 0x80) output.push(c);
    else if (c < 0x800) output.push(0xc0 | (c >> 6), 0x80 | (c & 63));
    else if (c < 0x10000) output.push(0xe0 | (c >> 12), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
    else output.push(0xf0 | (c >> 18), 0x80 | ((c >> 12) & 63), 0x80 | ((c >> 6) & 63), 0x80 | (c & 63));
  }
  return output;
}

function twist(ord) {
  return seed.map((b) => (b ^ (ord & 255)) & 255);
}

function scramble(bytes, keys) {
  const s = [];
  for (let i = 0; i < 256; i++) s[i] = i;
  let x = 0;
  let y = 0;
  for (x = 0; x < 256; x++) {
    y = (y + s[x] + keys[x % keys.length]) & 255;
    const t = s[x];
    s[x] = s[y];
    s[y] = t;
  }
  const output = new Array(bytes.length);
  x = 0;
  y = 0;
  for (let i = 0; i < bytes.length; i++) {
    x = (x + 1) & 255;
    y = (y + s[x]) & 255;
    const t = s[x];
    s[x] = s[y];
    s[y] = t;
    output[i] = bytes[i] ^ s[(s[x] + s[y]) & 255];
  }
  return output;
}

function armor(bytes) {
  const tab = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
  let output = '';
  for (let i = 0; i < bytes.length; i += 3) {
    const p = bytes[i];
    const q = i + 1 < bytes.length ? bytes[i + 1] : 0;
    const r = i + 2 < bytes.length ? bytes[i + 2] : 0;
    output += tab[p >> 2];
    output += tab[((p & 3) << 4) | (q >> 4)];
    output += i + 1 < bytes.length ? tab[((q & 15) << 2) | (r >> 6)] : '=';
    output += i + 2 < bytes.length ? tab[r & 63] : '=';
  }
  return output;
}

function lock(s, ord) {
  return armor(scramble(unicode(s), twist(ord)));
}

function hex(n) {
  return '0x' + n.toString(16);
}

function codes(s) {
  const a = [];
  for (let i = 0; i < s.length; i++) a.push(hex(s.charCodeAt(i)));
  return a.join(',');
}

function alphabet(parts) {
  let o = '';
  o += 'var ' + parts.letters + "='';var " + parts.ord + '=0x0;';
  o += 'for(' + parts.ord + '=0x41;' + parts.ord + '<0x5b;' + parts.ord + '++)' + parts.letters + '+=String.fromCharCode(' + parts.ord + ');';
  o += 'for(' + parts.ord + '=0x61;' + parts.ord + '<0x7b;' + parts.ord + '++)' + parts.letters + '+=String.fromCharCode(' + parts.ord + ');';
  o += 'for(' + parts.ord + '=0x30;' + parts.ord + '<0x3a;' + parts.ord + '++)' + parts.letters + '+=String.fromCharCode(' + parts.ord + ');';
  o += parts.letters + "+='+/';";
  return o;
}

function sixty(parts) {
  let o = '';
  o += 'var ' + parts.mid + "='';var " + parts.buffer + '=0x0;var ' + parts.bits + '=0x0;var ' + parts.pos + '=0x0;';
  o += 'for(' + parts.pos + '=0x0;' + parts.pos + '<' + parts.cipher + '.length;' + parts.pos + '++){var ' + parts.digit + '=' + parts.letters + '.indexOf(' + parts.cipher + '.charAt(' + parts.pos + '));';
  o += 'if(' + parts.digit + '<0x0)continue;';
  o += parts.buffer + '=(' + parts.buffer + '<<0x6)|' + parts.digit + ';';
  o += parts.bits + '+=0x6;';
  o += 'if(' + parts.bits + '>=0x8){' + parts.bits + '-=0x8;' + parts.mid + '+=String.fromCharCode((' + parts.buffer + '>>' + parts.bits + ')&0xff);}}';
  return o;
}

function whirl(parts) {
  let o = '';
  o += 'var ' + parts.keys + '=[' + seed.map(hex).join(',') + '];';
  o += 'for(var ' + parts.i + '=0x0;' + parts.i + '<' + parts.keys + '.length;' + parts.i + '++)' + parts.keys + '[' + parts.i + ']=(' + parts.keys + '[' + parts.i + ']^' + parts.slot + ')&0xff;';
  o += 'var ' + parts.sbox + '=[];for(var ' + parts.j + '=0x0;' + parts.j + '<0x100;' + parts.j + '++)' + parts.sbox + '[' + parts.j + ']=' + parts.j + ';';
  o += 'var ' + parts.k + '=0x0;var ' + parts.l + '=0x0;var ' + parts.swap + '=0x0;';
  o += 'for(' + parts.k + '=0x0;' + parts.k + '<0x100;' + parts.k + '++){';
  o += parts.l + '=(' + parts.l + '+' + parts.sbox + '[' + parts.k + ']+' + parts.keys + '[' + parts.k + '%' + parts.keys + '.length])&0xff;';
  o += parts.swap + '=' + parts.sbox + '[' + parts.k + '];' + parts.sbox + '[' + parts.k + ']=' + parts.sbox + '[' + parts.l + '];' + parts.sbox + '[' + parts.l + ']=' + parts.swap + ';}';
  o += parts.k + '=0x0;' + parts.l + '=0x0;';
  o += 'var ' + parts.out + "='';";
  o += 'for(' + parts.pos + '=0x0;' + parts.pos + '<' + parts.mid + '.length;' + parts.pos + '++){';
  o += parts.k + '=(' + parts.k + '+1)&0xff;';
  o += parts.l + '=(' + parts.l + '+' + parts.sbox + '[' + parts.k + '])&0xff;';
  o += parts.swap + '=' + parts.sbox + '[' + parts.k + '];' + parts.sbox + '[' + parts.k + ']=' + parts.sbox + '[' + parts.l + '];' + parts.sbox + '[' + parts.l + ']=' + parts.swap + ';';
  o += 'var ' + parts.cursor + '=' + parts.sbox + '[(' + parts.sbox + '[' + parts.k + ']+' + parts.sbox + '[' + parts.l + '])&0xff];';
  o += parts.out + '+=String.fromCharCode(' + parts.mid + '.charCodeAt(' + parts.pos + ')^' + parts.cursor + ');}';
  return o;
}

function octet(parts) {
  let o = '';
  o += 'var ' + parts.plaintext + "='';var " + parts.cursor + '=0x0;var ' + parts.byte + '=0x0;';
  o += 'while(' + parts.cursor + '<' + parts.out + '.length){';
  o += parts.byte + '=' + parts.out + '.charCodeAt(' + parts.cursor + ');';
  o += 'if(' + parts.byte + '<0x80){' + parts.plaintext + '+=String.fromCharCode(' + parts.byte + ');' + parts.cursor + '+=0x1;}';
  o += 'else if((' + parts.byte + '&0xe0)===0xc0){' + parts.plaintext + '+=String.fromCharCode(((' + parts.byte + '&0x1f)<<0x6)|(' + parts.out + '.charCodeAt(' + parts.cursor + '+1)&0x3f));' + parts.cursor + '+=0x2;}';
  o += 'else if((' + parts.byte + '&0xf0)===0xe0){' + parts.plaintext + '+=String.fromCharCode(((' + parts.byte + '&0x0f)<<0xc)|((' + parts.out + '.charCodeAt(' + parts.cursor + '+1)&0x3f)<<0x6)|(' + parts.out + '.charCodeAt(' + parts.cursor + '+2)&0x3f));' + parts.cursor + '+=0x3;}';
  o += 'else{var ' + parts.high + '=(((' + parts.byte + '&0x07)<<0x12)|((' + parts.out + '.charCodeAt(' + parts.cursor + '+1)&0x3f)<<0xc)|((' + parts.out + '.charCodeAt(' + parts.cursor + '+2)&0x3f)<<0x6)|(' + parts.out + '.charCodeAt(' + parts.cursor + '+3)&0x3f))-0x10000;';
  o += parts.plaintext + '+=String.fromCharCode(0xd800+(' + parts.high + '>>0xa),0xdc00+(' + parts.high + '&0x3ff));' + parts.cursor + '+=0x4;}}';
  return o;
}

function spinner(parts, mark, rot) {
  let o = '';
  o += '(function(' + parts.ring + ',' + parts.turns + '){';
  o += 'var ' + parts.roll + '=function(' + parts.steps + '){while(--' + parts.steps + '){' + parts.ring + '.push(' + parts.ring + '.shift());}};';
  o += 'var ' + parts.probe + '=function(){var ' + parts.checked + '=' + parts.decode + '(0x0);';
  o += 'if(' + parts.checked + '!==String.fromCharCode(' + codes(mark) + ')){' + parts.roll + '(0x2);' + parts.probe + '();}};';
  o += parts.roll + '(++' + parts.turns + ');' + parts.probe + '();';
  o += '}(' + parts.queue + ',' + hex(rot) + '));';
  return o;
}

function vigil(parts, check) {
  let o = '';
  o += 'var ' + parts.tally + '=0x0;';
  o += 'for(var ' + parts.cursor + '=0x1;' + parts.cursor + '<' + parts.queue + '.length;' + parts.cursor + '++){';
  o += 'var ' + parts.mid + '=' + parts.decode + '(' + parts.cursor + ');';
  o += 'for(var ' + parts.j + '=0x0;' + parts.j + '<' + parts.mid + '.length;' + parts.j + '++)';
  o += parts.tally + '=((' + parts.tally + '+' + parts.mid + '.charCodeAt(' + parts.j + '))&0xfffff)^' + parts.cursor + ';}';
  o += 'if(' + parts.tally + '!==0x' + check.toString(16) + '){' + parts.queue + '.splice(0x0);}';
  return o;
}

function prelude(list, parts) {
  const mark = 'q' + (list.length % 10) + 'w8k';
  const len = list.length + 1;
  const rot = len - 1;
  let check = 0;
  for (let s = 1; s <= list.length; s++) {
    const w = list[s - 1];
    for (let c = 0; c < w.length; c++) check = ((check + w.charCodeAt(c)) & 0xfffff) ^ s;
  }
  const encode = list.map((s, j) => lock(s, (j + 1) % len));
  encode.push(lock(mark, 0));
  let o = '';
  o += 'var ' + parts.queue + "=['" + encode.join("','") + "'];";
  o += alphabet(parts);
  o += 'var ' + parts.decode + '=function(' + parts.slot + '){';
  o += 'var ' + parts.cipher + '=' + parts.queue + '[' + parts.slot + '-0x0];';
  o += sixty(parts);
  o += whirl(parts);
  o += octet(parts);
  o += 'return ' + parts.plaintext + ';};';
  o += spinner(parts, mark, rot);
  o += vigil(parts, check);
  return o;
}

function gap(a, b) {
  if (!a) return '';
  const wa = /[A-Za-z0-9_$]/.test(a);
  const wb = /[A-Za-z0-9_$]/.test(b);
  if (wa && wb) return ' ';
  if (a === '+' && b === '+') return ' ';
  if (a === '-' && b === '-') return ' ';
  if (a === '/' && (b === '/' || b === '*')) return ' ';
  return '';
}

function emit(tokens) {
  const links = pairs(tokens);
  let s = '';
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    let sep = '';
    if (i > 0 && t.newline) {
      const prev = tokens[i - 1];
      const pv = prev.v;
      const op = links[i - 1];
      const pre = op !== undefined ? tokens[op - 1] : null;
      const ctrl = pv === ')' && pre && pre.k === 'name' && opens.has(pre.v);
      if (ctrl) sep = '';
      else if (hard.has(pv) || prev.k === 'num' || prev.k === 'str' || prev.k === 'regex') sep = ';';
      else if (clip.has(t.v)) sep = '';
      else if (prev.k === 'name' && !cantend.has(pv)) sep = ';';
      else if (prev.k === 'punc' && (pv === ')' || pv === ']' || pv === '}' || pv === '++' || pv === '--' || pv === '!' || pv === '~')) sep = ';';
      else sep = '';
    }
    const pc = s.length ? s[s.length - 1] : '';
    s += sep + gap(pc, t.v[0]) + t.v;
  }
  return s;
}

function globals(tokens, info) {
  have.clear();
  for (const entry of info.entries) have.add(entry.name);
  const links = pairs(tokens);
  const shapes = kinds(tokens, links);
  const mode = state(tokens, shapes);
  const spots = [];
  const cand = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'name') continue;
    if (!builtins.includes(t.v)) continue;
    if (have.has(t.v)) continue;
    if (info.guarded[i]) continue;
    const prev = tokens[i - 1];
    if (prev && prev.k === 'punc' && (prev.v === '.' || prev.v === '?.' || prev.v === '#')) continue;
    if (prev && prev.k === 'name' && halt.has(prev.v)) continue;
    const next = tokens[i + 1];
    if (next && next.k === 'punc' && next.v === ':' && mode[i] === 'obj') continue;
    spots.push(i);
    if (!cand.includes(t.v)) cand.push(t.v);
  }
  const map = new Map();
  for (const c of cand) map.set(c, mint());
  for (const i of spots) tokens[i].v = map.get(tokens[i].v);
  return { params: [...map.values()], orig: cand };
}

function shroud(body, on, params, orig) {
  if (!on) return body;
  if (!params.length) return '(function(){' + body + '}).call(this);';
  return '(function(' + params.join(',') + '){' + body + '}).call(this,' + orig.join(',') + ');';
}

function syntax(code) {
  try {
    new Function(code);
    return null;
  } catch (e) {
    return e;
  }
}

function fuse(source) {
  const block = [0, 0, 0, 0, 0, 0, 0, 0];
  for (let i = 0; i < source.length; i++) {
    const c = source.charCodeAt(i);
    const b = i % 8;
    block[b] = (block[b] * 0x11 + c + ((i * 0x9e) & 0xffff)) & 0xff;
  }
  for (let j = 0; j < block.length; j++) {
    if (block[j] === 0) block[j] = 0x5a ^ ((j * 0x13) & 0xff);
    block[j] = block[j] ^ ((j + 1) * 0x2d) & 0xff;
  }
  return block;
}

function make(source) {
  seed = fuse(source);
  const tokens = lex(source);
  let wrap = true;
  for (const t of tokens) {
    if (t.k === 'name' && (t.v === 'import' || t.v === 'export')) wrap = false;
    if (t.k === 'name') taken.add(t.v);
  }
  const links = pairs(tokens);
  const shapes = kinds(tokens, links);
  const mode = state(tokens, shapes);
  const info = scopes(tokens, links, shapes, wrap);
  rename(tokens, info, links, mode);
  numbers(tokens);
  bools(tokens, info);
  members(tokens, info.guarded);
  flatten(tokens, info.guarded);
  labels(tokens, info.guarded);
  const list = collect(tokens, info.guarded);
  let head = '';
  let len = 1;
  if (list.length) {
    const parts = {};
    for (const p of names) parts[p] = mint();
    head = prelude(list, parts);
    len = list.length + 1;
    for (const t of tokens) {
      if (t.k === 'name' && t.v === '\u0002') t.v = parts.decode;
      else if (t.k === 'num' && t.v[0] === '\u0003') t.v = hex((Number(t.v.slice(1)) + 1) % len);
    }
  }
  const g = globals(tokens, info);
  const code = head + shroud(emit(tokens), wrap, g.params, g.orig);
  const err = wrap ? syntax(code) : null;
  if (err) {
    throw new Error('Kết quả sinh ra lỗi cú pháp: ' + err.message);
  }
  return { code };
}

function run(a) {
  let source = filesystem.readFileSync(a, 'utf8');
  if (source.charCodeAt(0) === 0xfeff) source = source.slice(1);
  const b = a.slice(0, -3) + '_obf.js';
  filesystem.writeFileSync(b, make(source).code);
  process.stdout.write('Đã ghi ' + b + '\n');
}

const files = process.argv.slice(2);
let fail = 0;
if (!files.length) {
  process.stderr.write('Cách dùng: node obf.js <file1.js> <file2.js> ...\n');
  fail = 1;
}
for (const take of files) {
  if (take.startsWith('-') || !take.endsWith('.js')) {
    process.stderr.write('Chỉ nhận file .js: ' + take + '\n');
    fail = 1;
    continue;
  }
  try {
    run(take);
  } catch (e) {
    process.stderr.write('Lỗi ' + take + ': ' + e.message + '\n');
    fail = 1;
  }
}
process.exit(fail);
