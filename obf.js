const filesystem = require('fs');

const ops = new Set(['{', '}', '(', ')', '[', ']', ';', ',', '<', '>', '+', '-', '*', '/', '%', '&', '|', '^', '~', '!', '?', ':', '=', '.', '@', '#', '==', '!=', '<=', '>=', '&&', '||', '??', '?.', '++', '--', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^=', '**', '<<', '>>', '=>', '===', '!==', '**=', '<<=', '>>=', '>>>', '...', '&&=', '||=', '??=', '>>>=']);
const opens = new Set(['if', 'for', 'while', 'switch', 'catch', 'with', 'do', 'else', 'try', 'finally']);
const terms = new Set(['return', 'typeof', 'instanceof', 'in', 'of', 'new', 'delete', 'void', 'throw', 'case', 'do', 'else', 'yield', 'await', 'default', 'break', 'continue']);
const reserved = new Set(['if', 'for', 'while', 'switch', 'catch', 'with', 'do', 'else', 'try', 'finally', 'return', 'typeof', 'instanceof', 'in', 'of', 'new', 'delete', 'void', 'throw', 'case', 'yield', 'await', 'break', 'continue', 'this', 'super', 'class', 'function', 'var', 'let', 'const', 'true', 'false', 'null', 'undefined', 'default', 'extends', 'static', 'get', 'set', 'async', 'debugger', 'import', 'export']);
const clip = new Set(['(', '[', '.', '?.', ',', ':', '?', '=>', '...', '=', '+=', '-=', '*=', '/=', '%=', '**=', '&=', '|=', '^=', '<<=', '>>=', '>>>=', '&&=', '||=', '??=', '+', '-', '*', '/', '%', '**', '&', '|', '^', '<<', '>>', '>>>', '<', '>', '<=', '>=', '==', '!=', '===', '!==', '&&', '||', '??']);
const tails = new Set([';', ',', ')', ']', '}', ':', '?', '=>']);
const bound = new Set(['(', '[', '{', ',', ';', ':', '?', '=', '&&', '||', '??', '=>']);
const flip = { '<': '>', '>': '<', '<=': '>=', '>=': '<=' };
const maths = new Set(['+', '-', '*', '/', '%', '**', '&', '|', '^', '<<', '>>', '>>>', '&&', '||', '??']);
const hard = new Set(['return', 'throw', 'break', 'continue', 'yield']);
const unary = new Set(['typeof', 'void', 'delete', 'await', 'yield', 'new']);
const cantend = new Set([...opens, ...terms, ...hard, 'var', 'let', 'const', 'function', 'class', 'import', 'export', 'debugger', 'extends', 'get', 'set', 'static', 'async', 'super']);
const stops = new Set(['case', 'default', 'else', 'in', 'of']);
const builtins = ['Object', 'Array', 'Math', 'JSON', 'console', 'Promise', 'Date', 'Symbol', 'Map', 'Set', 'WeakMap', 'WeakSet', 'Proxy', 'Reflect', 'BigInt', 'Number', 'String', 'Boolean', 'RegExp', 'Error', 'TypeError', 'RangeError', 'SyntaxError', 'EvalError', 'URIError', 'parseInt', 'parseFloat', 'isNaN', 'isFinite', 'encodeURIComponent', 'decodeURIComponent', 'atob', 'btoa', 'TextEncoder', 'TextDecoder', 'URL', 'URLSearchParams', 'Buffer', 'Uint8Array', 'Uint16Array', 'Uint32Array', 'Int8Array', 'Int16Array', 'Int32Array', 'Float32Array', 'Float64Array', 'Uint8ClampedArray', 'BigInt64Array', 'BigUint64Array', 'ArrayBuffer', 'DataView', 'globalThis', 'setTimeout', 'clearTimeout', 'setInterval', 'clearInterval', 'queueMicrotask', 'structuredClone', 'fetch', 'Headers', 'Request', 'Response', 'FormData', 'AbortController', 'crypto', 'performance', 'setImmediate', 'clearImmediate', 'escape', 'unescape', 'require', 'module', 'exports', 'process'];
const pool = ['αβγδεζηθικλμνξοπρστυφχψω' + 'ΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ' + 'абвгдежзиклмнопрстуфхцчшщ' + 'άέήίόύώϊϋ', '◈◇▣◊○●◻▬▮', '░▒▓█▄▀▌▐▁', '∅∮∲∳∢', '⌘⌥⇧⌃⎋⏏', '♩♪♫♬♭♮♯', '☀☁☂☃☄★', '✁✂✃✄✆✇✈'];
const truthy = '(!0&&!![]&&(0x1<0x2))';
const falsy = '(!1||![]||(0x1>0x2))';
const frozen = new Set([...reserved, 'as', 'from']);
let seed = [90, 55, 195, 17, 158, 43, 116, 232, 37, 201, 88, 141, 9, 250, 63, 177];
const names = ['queue', 'letters', 'ord', 'decode', 'slot', 'cipher', 'mid', 'buffer', 'bits', 'pos', 'digit', 'keys', 'i', 'j', 'k', 'l', 'swap', 'out', 'checked', 'plaintext', 'cursor', 'byte', 'high', 'sbox', 'ring', 'turns', 'roll', 'steps', 'probe', 'tally', 'vale', 'stem', 'cell', 'mold'];
const piles = [
  [
    { k: 'name', v: 'void', newline: false }, { k: 'punc', v: '(', newline: false }, { k: 'num', v: '0x0', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ';', newline: false },
    { k: 'punc', v: '(', newline: false }, { k: 'punc', v: '!', newline: false }, { k: 'punc', v: '(', newline: false }, { k: 'num', v: '0x1', newline: false }, { k: 'punc', v: '===', newline: false }, { k: 'num', v: '0x2', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ';', newline: false },
    { k: 'punc', v: '(', newline: false }, { k: 'num', v: '0x1', newline: false }, { k: 'punc', v: '<<', newline: false }, { k: 'num', v: '0x0', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ';', newline: false },
    { k: 'name', v: 'void', newline: false }, { k: 'punc', v: '(', newline: false }, { k: 'punc', v: '+', newline: false }, { k: 'num', v: '0x0', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ';', newline: false }
  ],
  [
    { k: 'punc', v: '(', newline: false }, { k: 'punc', v: '!', newline: false }, { k: 'punc', v: '(', newline: false }, { k: 'name', v: 'typeof', newline: false }, { k: 'name', v: 'undefined', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ';', newline: false },
    { k: 'name', v: 'void', newline: false }, { k: 'punc', v: '(', newline: false }, { k: 'punc', v: '{', newline: false }, { k: 'punc', v: '}', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ';', newline: false },
    { k: 'punc', v: '(', newline: false }, { k: 'num', v: '0x2', newline: false }, { k: 'punc', v: '^', newline: false }, { k: 'num', v: '0x2', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ';', newline: false }
  ],
  [
    { k: 'punc', v: '(', newline: false }, { k: 'punc', v: '!', newline: false }, { k: 'punc', v: '(', newline: false }, { k: 'num', v: '0x5', newline: false }, { k: 'punc', v: '===', newline: false }, { k: 'num', v: '0x3', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ';', newline: false },
    { k: 'punc', v: '(', newline: false }, { k: 'num', v: '0x1', newline: false }, { k: 'punc', v: '&', newline: false }, { k: 'num', v: '0x3', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ';', newline: false },
    { k: 'name', v: 'void', newline: false }, { k: 'punc', v: '(', newline: false }, { k: 'punc', v: '~', newline: false }, { k: 'num', v: '0x0', newline: false }, { k: 'punc', v: ')', newline: false }, { k: 'punc', v: ';', newline: false }
  ]
];

let counter = 0;
const taken = new Set();
const have = new Set();

function mint() {
  let n = '$' + sig(counter);
  while (taken.has(n)) {
    counter++;
    n = '$' + sig(counter);
  }
  counter++;
  taken.add(n);
  return n;
}

function sig(n) {
  let s = '';
  const base = pool[0];
  do {
    const q = Math.floor(n / base.length);
    s = base[n - q * base.length] + s;
    n = q;
  } while (n > 0);
  return s;
}

function isw(c) {
  return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9') || c === '_' || c === '$' || c.charCodeAt(0) > 0x7f;
}

function hval(s) {
  return parseInt(s, 16);
}

function diag(source, pos) {
  let line = 1;
  let col = 1;
  for (let i = 0; i < pos && i < source.length; i++) {
    if (source[i] === '\n' || source[i] === '\u2028' || source[i] === '\u2029') {
      line++;
      col = 1;
    } else col++;
  }
  return 'dòng ' + line + ', cột ' + col;
}

function fault(source, pos, msg) {
  throw new Error(msg + ' tại ' + diag(source, pos));
}

function graft(tokens, guarded, at, span, rep) {
  const tail = tokens.slice(at + span);
  const wing = guarded.slice(at + span);
  tokens.length = at;
  guarded.length = at;
  for (let i = 0; i < rep.length; i++) {
    tokens.push(rep[i]);
    guarded.push(0);
  }
  for (let i = 0; i < tail.length; i++) {
    tokens.push(tail[i]);
    guarded.push(wing[i]);
  }
}

function pile(n) {
  const src = piles[n];
  const out = new Array(src.length);
  for (let i = 0; i < src.length; i++) out[i] = { k: src[i].k, v: src[i].v, newline: false };
  return out;
}

function esc(source, i) {
  const e = source[i + 1];
  if (e === 'n') return ['\n', i + 2];
  if (e === 't') return ['\t', i + 2];
  if (e === 'r') return ['\r', i + 2];
  if (e === 'b') return ['\b', i + 2];
  if (e === 'v') return ['\v', i + 2];
  if (e === 'f') return ['\f', i + 2];
  if (e === 'x') {
    const hx = source.substr(i + 2, 2);
    if (!/^[0-9a-fA-F]{2}$/.test(hx) || !Number.isInteger(hval(hx))) return [e, i + 2];
    return [String.fromCharCode(hval(hx)), i + 4];
  }
  if (e === 'u') {
    if (source[i + 2] === '{') {
      const cl = source.indexOf('}', i + 3);
      if (cl < 0 || cl > i + 12) return [e, i + 2];
      const cp = hval(source.slice(i + 3, cl));
      if (!Number.isInteger(cp) || cp < 0 || cp > 0x10ffff) return [e, i + 2];
      return [String.fromCodePoint(cp), cl + 1];
    }
    const hx = source.substr(i + 2, 4);
    if (!/^[0-9a-fA-F]{4}$/.test(hx) || !Number.isInteger(hval(hx))) return [e, i + 2];
    return [String.fromCharCode(hval(hx)), i + 6];
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
    let closed = false;
    while (i < size) {
      const c = source[i];
      if (c === q) {
        i++;
        closed = true;
        break;
      }
      if (c === '\\') {
        const r = esc(source, i);
        cooked += r[0];
        i = r[1];
        continue;
      }
      if (c === '\n') fault(source, i, 'Chuỗi chưa đóng');
      cooked += c;
      i++;
    }
    if (!closed) fault(source, size, 'Chuỗi chưa đóng');
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
    fault(source, i, 'Template chưa đóng');
  }
  function whole() {
    let octal = false;
    const start = i;
    if (source[i] === '0' && 'xXbBoO'.indexOf(source[i + 1]) >= 0) {
      i += 2;
      const from = i;
      while (i < size && (isw(source[i]) || source[i] === '_')) i++;
      if (i === from) fault(source, i, 'Số thiếu chữ số');
    } else {
      if (source[i] === '0' && source[i + 1] >= '0' && source[i + 1] <= '7') {
        let j = i + 1;
        while (j < size && source[j] >= '0' && source[j] <= '7') j++;
        if (j < size && source[j] >= '0' && source[j] <= '9') {
          while (i < size && ((source[i] >= '0' && source[i] <= '9') || source[i] === '_')) i++;
          if (source[i] === '.' && source[i + 1] >= '0' && source[i + 1] <= '9') {
            i++;
            while (i < size && ((source[i] >= '0' && source[i] <= '9') || source[i] === '_')) i++;
          }
        } else {
          i = j;
          octal = true;
        }
      } else {
        while (i < size && ((source[i] >= '0' && source[i] <= '9') || source[i] === '_')) i++;
        if (source[i] === '.' && source[i + 1] >= '0' && source[i + 1] <= '9') {
          i++;
          while (i < size && ((source[i] >= '0' && source[i] <= '9') || source[i] === '_')) i++;
        }
      }
      if (!octal && (source[i] === 'e' || source[i] === 'E')) {
        i++;
        if (source[i] === '+' || source[i] === '-') i++;
        const from = i;
        while (i < size && source[i] >= '0' && source[i] <= '9') i++;
        if (i === from) fault(source, i, 'Số thiếu số mũ');
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
    let val = Number(raw.replace(/_/g, ''));
    if (octal) val = parseInt(raw, 8);
    if (!Number.isNaN(val)) tail().n = val;
    if (!big && Number.isNaN(val)) throw new Error('Số không hợp lệ');
  }
  function ident() {
    const start = i;
    while (i < size && isw(source[i])) i++;
    record('name', source.slice(start, i));
  }
  function escident() {
    const start = i;
    let name = '';
    let any = false;
    while (i < size) {
      const c = source[i];
      if (c === '\\' && source[i + 1] === 'u') {
        if (source[i + 2] === '{') {
          const cl = source.indexOf('}', i + 3);
          if (cl < 0 || cl > i + 14) throw new Error('Mã hóa \\u{ chưa đóng');
          const cp = hval(source.slice(i + 3, cl));
          if (!Number.isInteger(cp) || cp < 0) throw new Error('Mã hóa \\u{ không hợp lệ');
          name += String.fromCodePoint(cp);
          i = cl + 1;
        } else if (/^[0-9a-fA-F]{4}$/.test(source.substr(i + 2, 4))) {
          name += String.fromCharCode(hval(source.substr(i + 2, 4)));
          i += 6;
        } else {
          break;
        }
        any = true;
        continue;
      }
      if (isw(c)) {
        name += c;
        i++;
        continue;
      }
      break;
    }
    if (!any || !name.length) {
      i = start;
      return;
    }
    for (const ch of name) {
      if (!isw(ch)) throw new Error('Tên mã hóa chứa ký tự lạ');
    }
    if (name[0] >= '0' && name[0] <= '9') {
      i = start;
      return;
    }
    record('name', source.slice(start, i));
    tail().v = name;
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
    let closed = false;
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
        closed = true;
        break;
      } else if (c === '\n') fault(source, i, 'Regex chưa đóng');
      raw += c;
      i++;
    }
    if (!closed) fault(source, size, 'Regex chưa đóng');
    while (i < size && source[i] >= 'a' && source[i] <= 'z') {
      raw += source[i];
      i++;
    }
    record('regex', raw);
  }
  function sym() {
    for (const l of [4, 3, 2, 1]) {
      const t = source.substr(i, l);
      const ok = ops.has(t);
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
    throw new Error('Ký tự lạ tại ' + diag(source, i) + ': ' + JSON.stringify(source[i]));
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
    if (i === 0 && c === '#' && source[i + 1] === '!') {
      while (i < size && source[i] !== '\n') i++;
      continue;
    }
    if (c === '<' && source[i + 1] === '!' && source[i + 2] === '-' && source[i + 3] === '-') {
      while (i < size && source[i] !== '\n') i++;
      continue;
    }
    if (c === '-' && source[i + 1] === '-' && source[i + 2] === '>' && (i === 0 || newline || source[i - 1] === '\n' || source[i - 1] === '\r' || source[i - 1] === '\u2028' || source[i - 1] === '\u2029')) {
      while (i < size && source[i] !== '\n') i++;
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
    if (c === '\\' && source[i + 1] === 'u') {
      escident();
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
      if (!stack.length) throw new Error('Dấu ngoặc đóng thừa');
      const o = stack.pop();
      const want = v === ')' ? '(' : v === ']' ? '[' : '{';
      if (tokens[o].v !== want) throw new Error('Dấu ngoặc không khớp');
      m[o] = i;
      m[i] = o;
    }
  }
  if (stack.length) throw new Error('Dấu ngoặc chưa đóng');
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
    const loop = (open, close) => {
      const obj = tokens[open].v === '{';
      for (let j = open + 1; j < close; j++) {
        const t = tokens[j];
        if (t.k === 'punc') {
          const v = t.v;
          if (v === '{') {
            const cl = links[j];
            loop(j, cl);
            j = cl;
            continue;
          }
          if (v === '[') {
            const cl = links[j];
            if (obj && tokens[cl + 1] && tokens[cl + 1].k === 'punc' && tokens[cl + 1].v === ':') {
              j = cl + 1;
              continue;
            }
            loop(j, cl);
            j = cl;
            continue;
          }
          if (v === '=') {
            const stop = delim(tokens, j + 1, close - 1, ',');
            j = stop < 0 ? close - 1 : stop;
            continue;
          }
          continue;
        }
        if (t.k !== 'name') continue;
        const next = tokens[j + 1];
        if (next && next.k === 'punc' && next.v === ':') continue;
        enter(scope, t.v, j, 'pat', false);
      }
    };
    loop(a, b);
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
    if (prev && prev.k === 'name' && (prev.v === 'break' || prev.v === 'continue')) continue;
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
      graft(tokens, info.guarded, i + 1, 0, [{ k: 'punc', v: ':', newline: false }, { k: 'name', v: entry.fresh, newline: false }]);
      continue;
    }
    t.v = entry.fresh;
  }
}

function rename(tokens, info, links, mode) {
  shield(tokens, info, mode);
  apply(tokens, info, links, mode);
}

function frac(n) {
  if (!Number.isFinite(n) || Number.isInteger(n)) return null;
  let scale = n;
  let tall = 0;
  while (tall < 0x40 && Math.floor(scale) !== scale) {
    scale *= 2;
    tall++;
  }
  if (tall >= 0x40) return null;
  const top = Math.floor(scale);
  if (!Number.isSafeInteger(top) || Math.abs(top) > 0x7fffffff) return null;
  const half = Math.pow(2, tall);
  if (!Number.isSafeInteger(half)) return null;
  return '(' + hex(top) + '/' + hex(half) + ')';
}

function numbers(tokens) {
  const encode = (n, d) => {
    if (n < 16) return '0x' + n.toString(16);
    if (n >= 0x10000 && n < 0x80000000) {
      const hi = Math.floor(n / 0x10000);
      const lo = n % 0x10000;
      if (lo !== 0x0) return '((' + encode(hi, d + 1) + '<<0x10)|' + encode(lo, d + 1) + ')';
    }
    if (d > 12) {
      const hi = Math.floor(n / 0x80000000);
      const lo = n % 0x80000000;
      return '((' + encode(hi, 0) + '*0x80000000)+' + encode(lo, 0) + ')';
    }
    if (n < 256) {
      const hi = Math.floor(n / 16);
      const lo = n % 16;
      return '((0x' + hi.toString(16) + '*0x10)+0x' + lo.toString(16) + ')';
    }
    const p = 3;
    const q = Math.floor(n / p);
    const r = n % p;
    return '((' + encode(q, d + 1) + '*0x3)+' + encode(r, d + 1) + ')';
  };
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'num' || t.big) continue;
    const prev = tokens[i - 1];
    if (prev && prev.k === 'punc' && (prev.v === '.' || prev.v === '#')) continue;
    const next = tokens[i + 1];
    if (next && next.k === 'punc' && next.v === ':') continue;
    if (!Number.isInteger(t.n)) {
      const cut = frac(t.n);
      if (cut) {
        t.v = cut;
        continue;
      }
    }
    if (!Number.isSafeInteger(t.n)) continue;
    t.v = encode(t.n, 0);
  }
}

function bools(tokens, info) {
  let shadow = false;
  let nan = false;
  let inf = false;
  for (const entry of info.entries) {
    if (entry.name === 'undefined') shadow = true;
    if (entry.name === 'NaN') nan = true;
    if (entry.name === 'Infinity') inf = true;
  }
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'name') continue;
    if (t.v !== 'true' && t.v !== 'false' && t.v !== 'undefined' && t.v !== 'NaN' && t.v !== 'Infinity') continue;
    const prev = tokens[i - 1];
    if (prev && prev.k === 'punc' && (prev.v === '.' || prev.v === '?.' || prev.v === '#')) continue;
    const next = tokens[i + 1];
    if (next && next.k === 'punc' && next.v === ':') continue;
    if (info.guarded[i]) continue;
    if (t.v === 'true') {
      t.v = truthy;
    } else if (t.v === 'false') {
      t.v = falsy;
    } else if (t.v === 'undefined' && !shadow) {
      t.v = 'void 0';
    } else if (t.v === 'NaN' && !nan) {
      t.v = '(0x0/0x0)';
    } else if (t.v === 'Infinity' && !inf) {
      t.v = '(0x1/0x0)';
    }
  }
}

function pack(s) {
  return "'" + s.replace(/\\/g, '\\\\').replace(/'/g, "\\'").replace(/\n/g, '\\n').replace(/\r/g, '\\r') + "'";
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
      graft(tokens, guarded, i, 2, [{ k: 'punc', v: '?.', newline: false }, { k: 'punc', v: '[', newline: false }, { k: 'str', v: pack(name), c: name, newline: false }, { k: 'punc', v: ']', newline: false }]);
    } else {
      graft(tokens, guarded, i, 2, [{ k: 'punc', v: '[', newline: false }, { k: 'str', v: pack(name), c: name, newline: false }, { k: 'punc', v: ']', newline: false }]);
    }
  }
}

function dispatch(segs, step, tick) {
  const ord = [];
  for (let j = 0; j < segs.length; j++) ord.push(String(j));
  const rev = ord.slice().reverse();
  let txt = 'var ' + step + "='" + rev.join('|') + "'.split('|').reverse()," + tick + '=0x0;while(!![]){switch(' + step + '[' + tick + '++]){';
  for (let j = 0; j < segs.length; j++) txt += "case '" + j + "':'\u0001" + j + "\u0001';continue;";
  txt += "case 'x':0x0;continue;";
  txt += "case 'y':(0x1>0x2);continue;";
  txt += "case 'z':void (0x2^0x2);continue;";
  txt += "case 'w':(''==![]);continue;";
  txt += "case 'v':(0x3<<0x0);continue;";
  txt += "case 'u':(0x4^0x0);continue;";
  txt += "case 't':(0x5&0x3);continue;";
  txt += "case 's':(0x6+-0x0);continue;";
  txt += '}break;}';
  return txt;
}

function chunk(tokens, a, b) {
  let dep = 0;
  let segs = [];
  let cursor = [];
  for (let j = a; j < b; j++) {
    const t = tokens[j];
    if (t.k === 'name' && (t.v === 'break' || t.v === 'continue')) return null;
    if (t.k === 'punc') {
      if (t.v === '(' || t.v === '[' || t.v === '{') dep++;
      else if (t.v === ')' || t.v === ']' || t.v === '}') dep--;
      else if (t.v === ';' && dep === 0) {
        const next = tokens[j + 1];
        if (next && next.k === 'name' && next.v === 'else') return null;
        cursor.push(t);
        segs.push(cursor);
        cursor = [];
        continue;
      }
    }
    if (dep === 0 && t.k === 'name' && (t.v === 'function' || t.v === 'class' || t.v === 'let' || t.v === 'const')) return null;
    if (dep === 0 && t.k === 'punc' && t.v === ':' && tokens[j - 1] && tokens[j - 1].k === 'name' && tokens[j - 2] && tokens[j - 2].k === 'punc' && (tokens[j - 2].v === ';' || tokens[j - 2].v === '{' || tokens[j - 2].v === '}')) return null;
    cursor.push(t);
  }
  if (cursor.length) segs.push(cursor);
  segs = segs.filter((s) => s.length > 0);
  if (segs.length < 2) return null;
  return segs;
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
    const first = tokens[o + 1];
    if (first && first.k === 'str' && first.c === 'use strict') continue;
    const segs = chunk(tokens, o + 1, c);
    if (!segs) continue;
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
    graft(tokens, guarded, o + 1, c - o - 1, fresh);
    adj.push({ p: o + 1, d: fresh.length - (c - o - 1) });
  }
  torch(tokens, guarded);
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
    graft(tokens, guarded, i, 1, [{ k: 'punc', v: '[', newline: false }, { k: 'str', v: pack(t.v), c: t.v, newline: false }, { k: 'punc', v: ']', newline: false }]);
  }
  pelt(tokens, guarded);
}

function pieces(tokens, guarded) {
  const cuts = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'str') continue;
    if (t.c === 'use strict' || t.c === 'use asm') continue;
    if (guarded[i]) continue;
    if (hold(tokens, i)) continue;
    if (t.c && t.c.length > 8) cuts.push(i);
  }
  for (let x = cuts.length - 1; x >= 0; x--) {
    const i = cuts[x];
    const t = tokens[i];
    const rep = [{ k: 'punc', v: '(', newline: t.newline }];
    const w = t.c;
    for (let p = 0; p < w.length; p += 8) {
      const bit = w.slice(p, p + 8);
      if (p) rep.push({ k: 'punc', v: '+', newline: false });
      rep.push({ k: 'str', v: pack(bit), c: bit, newline: false });
    }
    rep.push({ k: 'punc', v: ')', newline: false });
    graft(tokens, guarded, i, 1, rep);
  }
}

function junk(tokens, guarded) {
  const links = pairs(tokens);
  const shapes = kinds(tokens, links);
  const stack = [];
  const spots = [];
  let d = 0;
  let marked = -1;
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'punc') {
      if (t.k === 'name' && t.v === 'do') marked = d;
      continue;
    }
    const v = t.v;
    if (v === '{') {
      stack.push(shapes[i]);
      d++;
      continue;
    }
    if (v === '}') {
      stack.pop();
      d--;
      continue;
    }
    if (v === '(' || v === '[') {
      d++;
      continue;
    }
    if (v === ')' || v === ']') {
      d--;
      continue;
    }
    if (v !== ';') continue;
    if (d !== 0 && d !== 1) continue;
    if (marked === d) {
      marked = -1;
      continue;
    }
    if (d === 1) {
      const top = stack[stack.length - 1];
      if (!top || (top !== 'function' && top !== 'block')) continue;
    } else {
      let cls = false;
      for (const s of stack) {
        if (s === 'class') cls = true;
      }
      if (cls) continue;
    }
    const nx = tokens[i + 1];
    if (nx && nx.k === 'name' && nx.v === 'else') continue;
    spots.push(i);
  }
  for (let x = spots.length - 1; x >= 0; x--) {
    const pick = x % piles.length;
    const bits = pile(pick);
    graft(tokens, guarded, spots[x] + 1, 0, bits);
  }
  recast(tokens, guarded);
}

function between(tokens, guarded) {
  const cut = [];
  for (let i = 0; i < tokens.length - 2; i++) {
    const a = tokens[i];
    const p = tokens[i + 1];
    const b = tokens[i + 2];
    if (a.k !== 'str' || b.k !== 'str') continue;
    if (p.k !== 'punc' || p.v !== '+') continue;
    if (p.newline || a.newline || b.newline) continue;
    if (guarded[i] || guarded[i + 2]) continue;
    if (a.c === 'use strict' || a.c === 'use asm' || b.c === 'use strict' || b.c === 'use asm') continue;
    cut.push(i);
    i += 2;
  }
  for (let x = cut.length - 1; x >= 0; x--) {
    const i = cut[x];
    const a = tokens[i];
    const b = tokens[i + 2];
    a.c += b.c;
    a.v = pack(a.c);
    graft(tokens, guarded, i + 1, 2, []);
  }
  burn(tokens, guarded);
}

function sprawl(tokens, guarded) {
  const cut = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'name') continue;
    if (t.v !== 'var' && t.v !== 'let' && t.v !== 'const') continue;
    const prev = tokens[i - 1];
    if (prev && prev.k === 'punc' && prev.v !== ';' && prev.v !== '{' && prev.v !== '}' && prev.v !== ':') continue;
    const commas = [];
    let depth = 0;
    let c = i + 1;
    let found = false;
    while (c < tokens.length) {
      const q = tokens[c];
      if (q.k === 'punc') {
        if (q.v === '(' || q.v === '[' || q.v === '{') depth++;
        else if (q.v === ')' || q.v === ']' || q.v === '}') depth--;
        else if (q.v === ';' && depth === 0) {
          found = true;
          break;
        } else if (q.v === ',' && depth === 0) commas.push(c);
      }
      c++;
    }
    if (!found || !commas.length) continue;
    const kw = t.v;
    const grabs = [];
    let from = i + 1;
    let k = 0;
    while (k < commas.length) {
      grabs.push(tokens.slice(from, commas[k]));
      from = commas[k] + 1;
      k++;
    }
    grabs.push(tokens.slice(from, c));
    const base = [];
    base.push({ k: 'name', v: kw, newline: t.newline });
    for (k = 0; k < grabs.length; k++) {
      if (k) {
        base.push({ k: 'punc', v: ';', newline: true });
        base.push({ k: 'name', v: kw, newline: false });
      }
      base.push(...grabs[k]);
    }
    base.push({ k: 'punc', v: ';', newline: t.newline });
    graft(tokens, guarded, i, c - i + 1, base);
    i = i + base.length - 1;
  }
  belt(tokens, guarded);
}

function ret(tokens, guarded) {
  const cut = [];
  for (let i = 0; i < tokens.length - 1; i++) {
    const t = tokens[i];
    if (t.k !== 'name' || t.v !== 'return') continue;
    const n = tokens[i + 1];
    if (!n || n.k !== 'punc' || n.v !== ';') continue;
    cut.push(i);
  }
  for (let x = cut.length - 1; x >= 0; x--) {
    const i = cut[x];
    graft(tokens, guarded, i + 1, 0, [{ k: 'name', v: 'void', newline: false }, { k: 'num', v: '0x0', newline: false }]);
  }
  labels(tokens, guarded);
}

function belt(tokens, guarded) {
  const cut = [];
  const loops = [];
  let depth = 0;
  let i = 0;
  while (i < tokens.length) {
    const t = tokens[i];
    if (t.k === 'punc') {
      if (t.v === '{') depth++;
      else if (t.v === '}') depth--;
      i++;
      continue;
    }
    if (t.k === 'name' && t.v === 'do') {
      loops.push({ d: depth });
      i++;
      continue;
    }
    if (t.k === 'name' && t.v === 'while') {
      const top = loops[loops.length - 1];
      if (!(top && top.d === depth)) {
        const n = tokens[i + 1];
        if (n && n.k === 'punc' && n.v === '(') cut.push(i);
      } else {
        loops.pop();
      }
      i++;
      continue;
    }
    i++;
  }
  for (let x = cut.length - 1; x >= 0; x--) {
    const i = cut[x];
    tokens[i] = { k: 'name', v: 'for', newline: false };
    graft(tokens, guarded, i + 2, 0, [{ k: 'punc', v: ';', newline: false }]);
    let d = 0;
    let j = i + 1;
    for (; j < tokens.length; j++) {
      if (tokens[j].k !== 'punc') continue;
      if (tokens[j].v === '(') d++;
      else if (tokens[j].v === ')') {
        d--;
        if (!d) break;
      }
    }
    if (j < tokens.length) {
      graft(tokens, guarded, j, 0, [{ k: 'punc', v: ';', newline: false }]);
    }
  }
  flatten(tokens, guarded);
}

function recast(tokens, guarded) {
  const links = pairs(tokens);
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'name' || t.v !== 'for') continue;
    const nt = tokens[i + 1];
    if (!nt || nt.k !== 'punc' || nt.v !== '(') continue;
    const cl = links[i + 1];
    if (cl === undefined || !tokens[cl + 1] || tokens[cl + 1].k !== 'punc' || tokens[cl + 1].v !== '{') continue;
    let open = true;
    for (let j = i + 2; j < cl; j++) {
      if (tokens[j].k !== 'punc' || tokens[j].v !== ';') {
        open = false;
        break;
      }
    }
    if (!open) continue;
    graft(tokens, guarded, i, cl - i + 1,
      [
        { k: 'name', v: 'while', newline: t.newline },
        { k: 'punc', v: '(', newline: false },
        { k: 'punc', v: '!', newline: false },
        { k: 'punc', v: '!', newline: false },
        { k: 'punc', v: '[', newline: false },
        { k: 'punc', v: ']', newline: false },
        { k: 'punc', v: ')', newline: false }
      ]);
    i += 6;
  }
  forge(tokens, guarded);
}

function lit(tokens, i) {
  const prev = tokens[i - 1];
  if (!prev) return true;
  if (prev.k !== 'punc') return false;
  if (prev.v === ')' || prev.v === ']' || prev.v === '}' || prev.v === '++' || prev.v === '--') return false;
  return true;
}

function flat(tokens, a, b) {
  let seen = false;
  for (let j = a + 1; j < b; j++) {
    const q = tokens[j];
    if (q.k === 'punc') {
      if (q.v === ',') {
        if (!seen) return false;
        seen = false;
        continue;
      }
      return false;
    }
    if (q.k === 'name') {
      if (q.v !== 'true' && q.v !== 'false' && q.v !== 'null' && q.v !== 'undefined') return false;
    } else if (q.k !== 'num' && q.k !== 'str' && q.k !== 'regex') return false;
    if (seen) return false;
    seen = true;
  }
  return true;
}

function hold(tokens, i) {
  const pa = tokens[i - 1];
  const nx = tokens[i + 1];
  if (pa && pa.k === 'punc' && (pa.v === '{' || pa.v === ',') && nx && nx.k === 'punc' && nx.v === ':') return true;
  return !!(pa && pa.k === 'name' && (pa.v === 'import' || pa.v === 'export' || pa.v === 'from' || pa.v === 'as'));
}

function pelt(tokens, guarded) {
  const links = pairs(tokens);
  const spots = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'punc' || t.v !== '[') continue;
    if (guarded[i]) continue;
    const cl = links[i];
    if (cl === undefined) continue;
    if (!lit(tokens, i)) continue;
    if (!flat(tokens, i, cl)) continue;
    let n = 0;
    for (let j = i + 1; j < cl; j++) {
      if (tokens[j].k === 'punc' && tokens[j].v === ',') n++;
    }
    if (n < 0x3) continue;
    spots.push([i, cl]);
    i = cl;
  }
  for (let x = spots.length - 1; x >= 0; x--) {
    const [a, b] = spots[x];
    const elems = [];
    let cur = [];
    for (let j = a + 1; j < b; j++) {
      const q = tokens[j];
      if (q.k === 'punc' && q.v === ',') {
        if (cur.length) elems.push(cur);
        cur = [];
        continue;
      }
      cur.push(q);
    }
    if (cur.length) elems.push(cur);
    if (elems.length < 0x4) continue;
    const rep = [];
    const take = elems.length % 0x2 === 0x1 ? 0x3 : 0x2;
    rep.push({ k: 'punc', v: '[', newline: tokens[a].newline });
    for (let e = 0; e < take; e++) {
      if (e) rep.push({ k: 'punc', v: ',', newline: false });
      rep.push(...elems[e]);
    }
    rep.push({ k: 'punc', v: ']', newline: false });
    let e = take;
    while (e < elems.length) {
      rep.push({ k: 'punc', v: '.', newline: false }, { k: 'name', v: 'concat', newline: false }, { k: 'punc', v: '(', newline: false }, { k: 'punc', v: '[', newline: false });
      rep.push(...elems[e]);
      if (e + 1 < elems.length) {
        rep.push({ k: 'punc', v: ',', newline: false });
        rep.push(...elems[e + 1]);
      }
      rep.push({ k: 'punc', v: ']', newline: false }, { k: 'punc', v: ')', newline: false });
      e += 2;
    }
    graft(tokens, guarded, a, b - a + 1, rep);
  }
  mote(tokens, guarded);
}

function mote(tokens, guarded) {
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'str') continue;
    if (guarded[i]) continue;
    if (t.c === 'use strict' || t.c === 'use asm') continue;
    const c = t.c;
    if (!c) continue;
    if (c.length < 0x1 || c.length > 0x10) continue;
    if (!/^-?[0-9]+$/.test(c)) continue;
    if (c.length > 1 && c[0] === '0') continue;
    const n = Number(c);
    if (!Number.isSafeInteger(n)) continue;
    if (String(n) !== c) continue;
    if (hold(tokens, i)) continue;
    const rep = [{ k: 'punc', v: '(', newline: t.newline }, { k: 'str', v: "''", c: '', newline: false }, { k: 'punc', v: '+', newline: false }];
    if (n < 0) {
      rep.push({ k: 'punc', v: '(', newline: false }, { k: 'punc', v: '-', newline: false }, { k: 'num', v: hex(-n), n: -n, newline: false }, { k: 'punc', v: ')', newline: false });
    } else {
      rep.push({ k: 'num', v: hex(n), n: n, newline: false });
    }
    rep.push({ k: 'punc', v: ')', newline: false });
    graft(tokens, guarded, i, 1, rep);
    i += rep.length - 1;
  }
}

function jolt(tokens, guarded) {
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'str') continue;
    if (guarded[i]) continue;
    if (t.c === 'use strict' || t.c === 'use asm') continue;
    const c = t.c;
    if (!c || c.length < 0x4) continue;
    if (c.length % 0xd !== 0x0) continue;
    if (/[\uD800-\uDFFF]/.test(c)) continue;
    if (hold(tokens, i)) continue;
    const back = c.split('').reverse().join('');
    const rep = [
      { k: 'str', v: pack(back), c: back, newline: t.newline },
      { k: 'punc', v: '.', newline: false }, { k: 'name', v: 'split', newline: false }, { k: 'punc', v: '(', newline: false }, { k: 'str', v: "''", c: '', newline: false }, { k: 'punc', v: ')', newline: false },
      { k: 'punc', v: '.', newline: false }, { k: 'name', v: 'reverse', newline: false }, { k: 'punc', v: '(', newline: false }, { k: 'punc', v: ')', newline: false },
      { k: 'punc', v: '.', newline: false }, { k: 'name', v: 'join', newline: false }, { k: 'punc', v: '(', newline: false }, { k: 'str', v: "''", c: '', newline: false }, { k: 'punc', v: ')', newline: false }
    ];
    graft(tokens, guarded, i, 1, rep);
    i += rep.length - 1;
  }
  pieces(tokens, guarded);
}

function burn(tokens, guarded) {
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'regex') continue;
    if (guarded[i]) continue;
    const s = t.v;
    const last = s.lastIndexOf('/');
    if (last <= 0) continue;
    let flags = s.slice(last + 1);
    if (!/^[a-z]*$/.test(flags)) continue;
    const body = s.slice(1, last);
    let rep = [
      { k: 'name', v: 'new', newline: t.newline },
      { k: 'name', v: 'RegExp', newline: false },
      { k: 'punc', v: '(', newline: false },
      { k: 'str', v: pack(body), c: body, newline: false }
    ];
    if (flags) {
      rep.push({ k: 'punc', v: ',', newline: false }, { k: 'str', v: pack(flags), c: flags, newline: false });
    }
    rep.push({ k: 'punc', v: ')', newline: false });
    graft(tokens, guarded, i, 1, rep);
    i += rep.length - 1;
  }
  jolt(tokens, guarded);
}

function damp(tokens) {
  for (let i = 0; i < tokens.length - 1; i++) {
    const t = tokens[i];
    if (t.k !== 'punc') continue;
    if (!(t.v === '===' || t.v === '!==' || t.v === '==' || t.v === '!=') && !(t.v in flip)) continue;
    const a = tokens[i - 1];
    const b = tokens[i + 1];
    if (!a || !b) continue;
    if (a.k === 'punc' || b.k === 'punc') continue;
    if (a.k === 'name' && terms.has(a.v)) continue;
    if (b.k === 'name' && terms.has(b.v)) continue;
    const pre = tokens[i - 2];
    if (!pre) continue;
    if (pre.k === 'punc' && !bound.has(pre.v)) continue;
    if (pre.k === 'name' && (unary.has(pre.v) || !terms.has(pre.v))) continue;
    const follow = tokens[i + 2];
    if (follow && follow.k === 'punc' && (follow.v === '(' || follow.v === '[' || follow.v === '.' || follow.v === '?.' || maths.has(follow.v))) continue;
    tokens[i - 1] = b;
    tokens[i + 1] = a;
    if (t.v in flip) t.v = flip[t.v];
    i += 2;
  }
}

function wale(tokens, guarded) {
  const links = pairs(tokens);
  const spots = [];
  const clean = (x, y) => {
    let d = 0;
    for (let j = x; j < y; j++) {
      const q = tokens[j];
      if (q.k === 'punc') {
        if (q.v === '{' || q.v === '(' || q.v === '[') d++;
        else if (q.v === '}' || q.v === ')' || q.v === ']') d--;
      }
      if (d === 0 && q.k === 'name' && (q.v === 'var' || q.v === 'let' || q.v === 'const' || q.v === 'function' || q.v === 'class')) return false;
    }
    return true;
  };
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'name' || t.v !== 'if') continue;
    const op = tokens[i + 1];
    if (!op || op.k !== 'punc' || op.v !== '(') continue;
    const cp = links[i + 1];
    if (cp === undefined) continue;
    const ob = tokens[cp + 1];
    if (!ob || ob.k !== 'punc' || ob.v !== '{') continue;
    const cb = links[cp + 1];
    if (cb === undefined) continue;
    const el = tokens[cb + 1];
    if (!el || el.k !== 'name' || el.v !== 'else') continue;
    const eye = tokens[cb + 2];
    if (!eye || eye.k !== 'punc' || eye.v !== '{') continue;
    const fin = links[cb + 2];
    if (fin === undefined) continue;
    const cond = tokens.slice(i + 2, cp);
    if (!cond.length) continue;
    if (!clean(cp + 1, cb)) continue;
    if (!clean(cb + 2, fin)) continue;
    spots.push([i, cp, cp + 1, cb, cb + 2, fin]);
    i = fin;
  }
  for (let x = spots.length - 1; x >= 0; x--) {
    const [s, cp, ob, cb, alt, end] = spots[x];
    const cond = tokens.slice(s + 2, cp);
    const a = tokens.slice(ob + 1, cb);
    const b = tokens.slice(alt + 1, end);
    const rep = [
      { k: 'name', v: 'if', newline: tokens[s].newline },
      { k: 'punc', v: '(', newline: false },
      { k: 'punc', v: '!', newline: false },
      { k: 'punc', v: '(', newline: false },
      ...cond,
      { k: 'punc', v: ')', newline: false },
      { k: 'punc', v: ')', newline: false },
      { k: 'punc', v: '{', newline: false },
      ...b,
      { k: 'punc', v: '}', newline: false },
      { k: 'name', v: 'else', newline: false },
      { k: 'punc', v: '{', newline: false },
      ...a,
      { k: 'punc', v: '}', newline: false }
    ];
    graft(tokens, guarded, s, end - s + 1, rep);
  }
  mane(tokens, guarded);
}

function mane(tokens, guarded) {
  const links = pairs(tokens);
  const spots = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'name' || t.v !== 'do') continue;
    const ob = tokens[i + 1];
    if (!ob || ob.k !== 'punc' || ob.v !== '{') continue;
    const cb = links[i + 1];
    if (cb === undefined) continue;
    const wt = tokens[cb + 1];
    if (!wt || wt.k !== 'name' || wt.v !== 'while') continue;
    const op = tokens[cb + 2];
    if (!op || op.k !== 'punc' || op.v !== '(') continue;
    const cp = links[cb + 2];
    if (cp === undefined) continue;
    const semi = tokens[cp + 1];
    if (!semi || semi.k !== 'punc' || semi.v !== ';') continue;
    const cond = tokens.slice(cb + 3, cp);
    if (!cond.length) continue;
    let bad = false;
    for (let j = i; j < cp; j++) {
      if (tokens[j].k === 'name' && (tokens[j].v === 'continue' || tokens[j].v === 'break')) {
        bad = true;
        break;
      }
    }
    if (bad) continue;
    let d = 0;
    let wrong = false;
    for (let j = i + 2; j < cb; j++) {
      const q = tokens[j];
      if (q.k === 'punc') {
        if (q.v === '{' || q.v === '(' || q.v === '[') d++;
        else if (q.v === '}' || q.v === ')' || q.v === ']') d--;
      }
      if (d === 0 && q.k === 'name' && (q.v === 'var' || q.v === 'let' || q.v === 'const' || q.v === 'function' || q.v === 'class')) {
        wrong = true;
        break;
      }
    }
    if (wrong) continue;
    spots.push([i, i + 1, cb, cp + 1, cond]);
    i = cp;
  }
  for (let x = spots.length - 1; x >= 0; x--) {
    const [s, ob, cb, semi, cond] = spots[x];
    const inner = tokens.slice(ob + 1, cb);
    const rep = [
      { k: 'name', v: 'while', newline: tokens[s].newline },
      { k: 'punc', v: '(', newline: false },
      { k: 'punc', v: '!', newline: false },
      { k: 'punc', v: '!', newline: false },
      { k: 'punc', v: '[', newline: false },
      { k: 'punc', v: ']', newline: false },
      { k: 'punc', v: ')', newline: false },
      { k: 'punc', v: '{', newline: false },
      ...inner,
      { k: 'punc', v: ';', newline: false },
      { k: 'name', v: 'if', newline: false },
      { k: 'punc', v: '(', newline: false },
      { k: 'punc', v: '!', newline: false },
      { k: 'punc', v: '(', newline: false },
      ...cond,
      { k: 'punc', v: ')', newline: false },
      { k: 'punc', v: ')', newline: false },
      { k: 'name', v: 'break', newline: false },
      { k: 'punc', v: ';', newline: false },
      { k: 'punc', v: '}', newline: false }
    ];
    graft(tokens, guarded, s, semi - s + 1, rep);
  }
  ret(tokens, guarded);
}

function forge(tokens, guarded) {
  const links = pairs(tokens);
  const spots = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'name' || t.v !== 'for') continue;
    const op = tokens[i + 1];
    if (!op || op.k !== 'punc' || op.v !== '(') continue;
    const cp = links[i + 1];
    if (cp === undefined) continue;
    const ob = tokens[cp + 1];
    if (!ob || ob.k !== 'punc' || ob.v !== '{') continue;
    const cb = links[cp + 1];
    if (cb === undefined) continue;
    const semis = [];
    let d = 0;
    for (let j = i + 2; j < cp; j++) {
      const q = tokens[j];
      if (q.k === 'punc') {
        if (q.v === '(' || q.v === '[' || q.v === '{') d++;
        else if (q.v === ')' || q.v === ']' || q.v === '}') d--;
        else if (q.v === ';' && d === 0) semis.push(j);
      }
    }
    if (semis.length !== 0x2) continue;
    const init = tokens.slice(i + 2, semis[0]);
    const cond = tokens.slice(semis[0] + 1, semis[1]);
    const inc = tokens.slice(semis[1] + 1, cp);
    if (!cond.length) continue;
    let bad = false;
    for (let j = semis[0] + 1; j < semis[1]; j++) {
      if (tokens[j].k === 'name' && (tokens[j].v === 'let' || tokens[j].v === 'const')) {
        bad = true;
        break;
      }
    }
    if (bad) continue;
    const pre = tokens[i - 1];
    const far = tokens[i - 2];
    if (pre && pre.k === 'punc' && pre.v === ':' && far && far.k === 'name' && !reserved.has(far.v)) continue;
    if (inc.length) {
      let cont = false;
      for (let j = cp + 2; j < cb; j++) {
        if (tokens[j].k === 'name' && tokens[j].v === 'continue') {
          cont = true;
          break;
        }
      }
      if (cont) continue;
    }
    spots.push([i, cp, cp + 1, cb, init, cond, inc]);
    i = cb;
  }
  for (let x = spots.length - 1; x >= 0; x--) {
    const [s, cp, ob, cb, init, cond, inc] = spots[x];
    const inner = tokens.slice(ob + 1, cb);
    const rep = [];
    rep.push({ k: 'punc', v: '{', newline: tokens[s].newline });
    rep.push(...init);
    if (init.length) rep.push({ k: 'punc', v: ';', newline: false });
    rep.push({ k: 'name', v: 'while', newline: false });
    rep.push({ k: 'punc', v: '(', newline: false });
    rep.push(...cond);
    rep.push({ k: 'punc', v: ')', newline: false });
    rep.push({ k: 'punc', v: '{', newline: false });
    rep.push(...inner);
    rep.push({ k: 'punc', v: ';', newline: false });
    rep.push(...inc);
    rep.push({ k: 'punc', v: ';', newline: false });
    rep.push({ k: 'punc', v: '}', newline: false });
    rep.push({ k: 'punc', v: '}', newline: false });
    graft(tokens, guarded, s, cb - s + 1, rep);
  }
  wale(tokens, guarded);
}

function baulk(tokens, guarded) {
  const links = pairs(tokens);
  const spots = [];
  for (let i = 0; i < tokens.length - 1; i++) {
    const t = tokens[i];
    if (t.k !== 'name' || t.v !== 'if') continue;
    const op = tokens[i + 1];
    if (!op || op.k !== 'punc' || op.v !== '(') continue;
    const cp = links[i + 1];
    if (cp === undefined) continue;
    const hope = tokens[cp + 2];
    if (!hope || hope.k !== 'name' || hope.v !== 'return') continue;
    const xa = tokens[cp + 3];
    if (!xa || xa.k === 'punc') continue;
    const sa = tokens[cp + 4];
    if (!sa || sa.k !== 'punc' || sa.v !== ';') continue;
    const cb = links[cp + 1];
    if (cb === undefined || sa !== tokens[cb - 1]) continue;
    const el = tokens[cb + 1];
    if (!el || el.k !== 'name' || el.v !== 'else') continue;
    const rb = tokens[cb + 3];
    if (!rb || rb.k !== 'name' || rb.v !== 'return') continue;
    const xb = tokens[cb + 4];
    if (!xb || xb.k === 'punc') continue;
    const sb = tokens[cb + 5];
    if (!sb || sb.k !== 'punc' || sb.v !== ';') continue;
    const ce = links[cb + 2];
    if (ce === undefined || sb !== tokens[ce - 1]) continue;
    const cond = tokens.slice(i + 2, cp);
    if (!cond.length) continue;
    spots.push([i, ce, cond, xa, xb]);
    i = ce;
  }
  for (let x = spots.length - 1; x >= 0; x--) {
    const [s, e, cond, xa, xb] = spots[x];
    const rep = [
      { k: 'name', v: 'return', newline: tokens[s].newline },
      ...cond,
      { k: 'punc', v: '?', newline: false },
      xa,
      { k: 'punc', v: ':', newline: false },
      xb,
      { k: 'punc', v: ';', newline: false }
    ];
    graft(tokens, guarded, s, e - s + 1, rep);
  }
  between(tokens, guarded);
}

function torch(tokens, guarded) {
  const links = pairs(tokens);
  const spots = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'name' || (t.v !== 'for' && t.v !== 'while' && t.v !== 'do')) continue;
    let ob = -1;
    let cb = -1;
    if (t.v === 'do') {
      const f = tokens[i + 1];
      if (!f || f.k !== 'punc' || f.v !== '{') continue;
      ob = i + 1;
      cb = links[ob];
    } else {
      const nt = tokens[i + 1];
      if (!nt || nt.k !== 'punc' || nt.v !== '(') continue;
      const cl = links[i + 1];
      if (cl === undefined) continue;
      const f = tokens[cl + 1];
      if (!f || f.k !== 'punc' || f.v !== '{') continue;
      ob = cl + 1;
      cb = links[ob];
    }
    if (cb === undefined) continue;
    const segs = chunk(tokens, ob + 1, cb);
    if (!segs) continue;
    spots.push([ob, cb, segs]);
    i = cb;
  }
  for (let x = spots.length - 1; x >= 0; x--) {
    const [o, c, segs] = spots[x];
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
    graft(tokens, guarded, o + 1, c - o - 1, fresh);
  }
  junk(tokens, guarded);
}

function collect(tokens, guarded) {
  const map = new Map();
  const list = [];
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (t.k !== 'str') continue;
    if (t.c === 'use strict' || t.c === 'use asm') continue;
    if (guarded[i]) continue;
    if (hold(tokens, i)) continue;
    let ord = map.get(t.c);
    if (ord === undefined) {
      ord = list.length;
      list.push(t.c);
      map.set(t.c, ord);
    }
    graft(tokens, guarded, i, 1, [{ k: 'name', v: '\u0002', newline: t.newline }, { k: 'punc', v: '(', newline: false }, { k: 'num', v: '\u0003' + ord, newline: false }, { k: 'punc', v: ')', newline: false }]);
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
  return seed.map((b, x) => (b ^ ((ord + x * 0x3d) & 255) ^ ((x * 0x17) & 255)) & 255);
}

function soak(bytes, ord) {
  for (let i = 0; i < bytes.length; i++) bytes[i] = ((bytes[i] ^ ((i * 0x2b + ord) & 255)) + i + ord) & 255;
  return bytes;
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
  x = 0;
  y = 0;
  for (let i = 0; i < bytes.length; i++) {
    x = (x + 1) & 255;
    y = (y + s[x]) & 255;
    const t = s[x];
    s[x] = s[y];
    s[y] = t;
    output[i] = output[i] ^ s[(s[x] + s[y]) & 255];
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
  return armor(scramble(soak(unicode(s), ord), twist(ord)));
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
  o += 'for(var ' + parts.i + '=0x0;' + parts.i + '<' + parts.keys + '.length;' + parts.i + '++)' + parts.keys + '[' + parts.i + ']=(' + parts.keys + '[' + parts.i + ']^((' + parts.slot + '+(' + parts.i + '*0x3d))&0xff)^((' + parts.i + '*0x17)&0xff))&0xff;';
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
  o += parts.k + '=0x0;' + parts.l + '=0x0;';
  o += 'for(' + parts.pos + '=0x0;' + parts.pos + '<' + parts.out + '.length;' + parts.pos + '++){';
  o += parts.k + '=(' + parts.k + '+1)&0xff;';
  o += parts.l + '=(' + parts.l + '+' + parts.sbox + '[' + parts.k + '])&0xff;';
  o += parts.swap + '=' + parts.sbox + '[' + parts.k + '];' + parts.sbox + '[' + parts.k + ']=' + parts.sbox + '[' + parts.l + '];' + parts.sbox + '[' + parts.l + ']=' + parts.swap + ';';
  o += parts.out + '=' + parts.out + '.slice(0x0,' + parts.pos + ')+String.fromCharCode(' + parts.out + '.charCodeAt(' + parts.pos + ')^' + parts.sbox + '[(' + parts.sbox + '[' + parts.k + ']+' + parts.sbox + '[' + parts.l + '])&0xff])+' + parts.out + '.slice(' + parts.pos + '+0x1);}';
  o += 'var ' + parts.vale + "='';";
  o += 'for(' + parts.pos + '=0x0;' + parts.pos + '<' + parts.out + '.length;' + parts.pos + '++)' + parts.vale + '+=String.fromCharCode((' + parts.out + '.charCodeAt(' + parts.pos + ')-' + parts.pos + '-' + parts.slot + ')&0xff);';
  o += parts.out + "='';";
  o += 'for(' + parts.pos + '=0x0;' + parts.pos + '<' + parts.vale + '.length;' + parts.pos + '++)' + parts.out + '+=String.fromCharCode(' + parts.vale + '.charCodeAt(' + parts.pos + ')^(((' + parts.pos + '*0x2b)+' + parts.slot + ')&0xff));';
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
  o += parts.roll + '(++' + parts.turns + ');' + parts.roll + '(0x4);' + parts.probe + '();';
  o += '}(' + parts.queue + ',' + hex(rot) + '));';
  return o;
}

function vigil(parts, check, back, len) {
  let o = '';
  o += 'var ' + parts.tally + '=0x0;';
  o += 'for(var ' + parts.cursor + '=0x1;' + parts.cursor + '<' + parts.queue + '.length;' + parts.cursor + '++){';
  o += 'var ' + parts.mid + '=' + parts.decode + '(' + parts.cursor + ');';
  o += 'for(var ' + parts.j + '=0x0;' + parts.j + '<' + parts.mid + '.length;' + parts.j + '++)';
  o += parts.tally + '=((' + parts.tally + '+' + parts.mid + '.charCodeAt(' + parts.j + '))&0xfffff)^' + parts.cursor + ';}';
  o += 'if(' + parts.tally + '!==0x' + check.toString(16) + '){' + parts.queue + '.splice(0x0);}';
  o += 'var ' + parts.checked + '=0x0;';
  o += 'for(' + parts.cursor + '=' + parts.queue + '.length-0x1;' + parts.cursor + '>0x0;' + parts.cursor + '--){';
  o += 'var ' + parts.mid + '=' + parts.decode + '(' + parts.cursor + ');';
  o += 'for(var ' + parts.j + '=0x0;' + parts.j + '<' + parts.mid + '.length;' + parts.j + '++)';
  o += parts.checked + '=((' + parts.checked + '+' + parts.mid + '.charCodeAt(' + parts.j + '))&0xfffff)^' + parts.cursor + ';}';
  o += 'if(' + parts.checked + '!==0x' + back.toString(16) + '){' + parts.queue + '.splice(0x0);}';
  o += 'if(' + parts.queue + '.length!==0x' + len.toString(16) + '){' + parts.queue + '.splice(0x0);}';
  o += 'if(' + parts.letters + '.length!==0x40){' + parts.queue + '.splice(0x0);}';
  return o;
}

function stem(parts) {
  let o = '';
  o += 'var ' + parts.stem + '=function(' + parts.cipher + '){';
  o += sixty(parts);
  o += 'return ' + parts.mid + ';};';
  return o;
}

function cell(parts) {
  let o = '';
  o += 'var ' + parts.cell + '=function(' + parts.mid + ',' + parts.slot + '){';
  o += 'var ' + parts.pos + '=0x0;';
  o += whirl(parts);
  o += 'return ' + parts.out + ';};';
  return o;
}

function mold(parts) {
  let o = '';
  o += 'var ' + parts.mold + '=function(' + parts.out + '){';
  o += octet(parts);
  o += 'return ' + parts.plaintext + ';};';
  return o;
}

function prelude(list, parts) {
  for (let i = 1; i < pool.length; i++) list.push(pool[i]);
  const mark = 'qw8k';
  const len = list.length + 1;
  const rot = len - 1;
  let check = 0;
  for (let s = 1; s <= list.length; s++) {
    const w = list[s - 1];
    for (let c = 0; c < w.length; c++) check = ((check + w.charCodeAt(c)) & 0xfffff) ^ s;
  }
  let back = 0;
  for (let s = list.length; s >= 1; s--) {
    const w = list[s - 1];
    for (let c = 0; c < w.length; c++) back = ((back + w.charCodeAt(c)) & 0xfffff) ^ s;
  }
  const encode = list.map((s, j) => lock(s, j + 1));
  encode.push(lock(mark, 0));
  let o = '';
  o += 'var ' + parts.queue + "=['" + encode.join("','") + "'];";
  o += alphabet(parts);
  o += stem(parts);
  o += cell(parts);
  o += mold(parts);
  o += 'var ' + parts.decode + '=function(' + parts.slot + '){return ' + parts.mold + '(' + parts.cell + '(' + parts.stem + '(' + parts.queue + '[' + parts.slot + '-0x0]),' + parts.slot + '));};';
  o += spinner(parts, mark, rot);
  o += vigil(parts, check, back, len);
  return o;
}

function gap(a, b) {
  if (!a) return '';
  const wa = /[A-Za-z0-9_$]/.test(a);
  const wb = /[A-Za-z0-9_$\\]/.test(b);
  if (wa && wb) return ' ';
  if (a === '+' && (b === '+' || b === '=')) return ' ';
  if (a === '-' && (b === '-' || b === '=')) return ' ';
  if (a === '*' && (b === '*' || b === '=')) return ' ';
  if (a === '/' && (b === '/' || b === '*' || b === '=')) return ' ';
  if (a === '%' && b === '=') return ' ';
  if (a === '<' && (b === '<' || b === '=')) return ' ';
  if (a === '>' && (b === '>' || b === '=')) return ' ';
  if ((a === '>' || a === '<' || a === '=' || a === '!') && b === '=') return ' ';
  if (a === '=' && (b === '=' || b === '>')) return ' ';
  if (a === '&' && (b === '&' || b === '=')) return ' ';
  if (a === '|' && (b === '|' || b === '=')) return ' ';
  if (a === '^' && b === '=') return ' ';
  if (a === '?' && (b === '?' || b === '.' || b === '=')) return ' ';
  if (a === '!' && (b === '=' || b === '!')) return ' ';
  if (a === '.' && b === '.') return ' ';
  if (a === ':' && b === ':') return ' ';
  return '';
}

function wordy(v) {
  if (!v.length) return false;
  for (let i = 0; i < v.length; i++) {
    const c = v[i];
    if (!isw(c) && c.charCodeAt(0) <= 0x7f) return false;
  }
  return true;
}

function mask(s) {
  let o = '';
  for (let i = 0; i < s.length; i++) o += '\\u' + s.charCodeAt(i).toString(16).padStart(4, '0');
  return o;
}

function veil(s) {
  return "'" + mask(s) + "'";
}

function emit(tokens) {
  const links = pairs(tokens);
  const shapes = kinds(tokens, links);
  const nests = [];
  const plain = new Array(tokens.length);
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    if (nests.length) {
      const top = nests[nests.length - 1];
      const soft = top.v === '(' || top.v === '[' || (top.v === '{' && shapes[top.i] === 'object');
      plain[i] = !soft;
    } else plain[i] = true;
    if (t.k !== 'punc') continue;
    const v = t.v;
    if (v === '(' || v === '[' || v === '{') nests.push({ v, i });
    else if (v === ')' || v === ']' || v === '}') nests.pop();
  }
  let s = '';
  for (let i = 0; i < tokens.length; i++) {
    const t = tokens[i];
    let sep = '';
    if (i > 0 && t.newline && plain[i]) {
      const prev = tokens[i - 1];
      const pv = prev.v;
      const op = links[i - 1];
      const pre = op !== undefined ? tokens[op - 1] : null;
      const ctrl = pv === ')' && pre && pre.k === 'name' && opens.has(pre.v);
      if (ctrl) sep = '';
      else if (pv === 'return' || pv === 'throw' || pv === 'yield') {
        const nx = t;
        const go = nx && (nx.k === 'name' ? !stops.has(nx.v) : !(nx.k === 'punc' && tails.has(nx.v)));
        sep = go || t.v === ';' ? '' : ';';
      } else if (hard.has(pv) || prev.k === 'num' || prev.k === 'str' || prev.k === 'regex') sep = ';';
      else if (clip.has(t.v)) sep = '';
      else if (prev.k === 'name' && !cantend.has(pv)) sep = ';';
      else if (prev.k === 'punc' && (pv === ')' || pv === ']' || pv === '}' || pv === '++' || pv === '--' || pv === '!' || pv === '~')) sep = ';';
      else sep = '';
    }
    let text = t.v;
    if (t.k === 'name' && wordy(text) && !frozen.has(text) && text.charCodeAt(0) !== 0x23) {
      const before = i > 0 ? tokens[i - 1] : null;
      const meta = before && before.k === 'punc' && (before.v === '.' || before.v === '?.') && i > 1 && tokens[i - 2].k === 'name' && (tokens[i - 2].v === 'new' || tokens[i - 2].v === 'import');
      if (!(before && before.k === 'punc' && (before.v === '#' || meta))) text = mask(text);
    } else if (t.k === 'str' && t.c && t.c !== 'use strict') text = veil(t.c);
    const pc = s.length ? s[s.length - 1] : '';
    s += sep + gap(pc, text[0]) + text;
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
    if (prev && prev.k === 'name' && (prev.v === 'break' || prev.v === 'continue')) continue;
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
  const mid = [];
  const inner = [];
  for (let i = 0; i < params.length; i++) {
    mid.push(mint());
    inner.push(mint());
  }
  if (!params.length) {
    return '(function(){return function(){return function(){' + body + '}.call(this);}.call(this);}).call(this);';
  }
  const p = params.map(mask);
  const q = mid.map(mask);
  const r = inner.map(mask);
  const o = orig.map(mask);
  return '(function(' + p.join(',') + '){return function(' + q.join(',') + '){return function(' + r.join(',') + '){' + body + '}.call(this,' + q.join(',') + ');}.call(this,' + p.join(',') + ');}).call(this,' + o.join(',') + ');';
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
  const block = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0];
  for (let i = 0; i < source.length; i++) {
    const c = source.charCodeAt(i);
    const b = i % 16;
    block[b] = (block[b] * 0x11 + c + ((i * 0x9e) & 0xffff) + (source.length & 0xff)) & 0xff;
    const d = (i * 7 + source.length) % 16;
    block[d] = (block[d] * 0x1d + c + ((i * 0x4b) & 0xffff)) & 0xff;
  }
  for (let j = 0; j < block.length; j++) {
    if (block[j] === 0) block[j] = 0x5a ^ ((j * 0x13) & 0xff);
    block[j] = block[j] ^ ((j + 1) * 0x2d + j * 0x1f) & 0xff;
    block[j] = (block[j] ^ ((block[(j + 5) % 16] * 0x0d) & 0xff)) & 0xff;
  }
  for (let j = 15; j >= 0; j--) {
    block[j] = (block[j] * 0x25 ^ ((block[(j + 1) % 16] + j) & 0xff)) & 0xff;
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
  sprawl(tokens, info.guarded);
  numbers(tokens);
  bools(tokens, info);
  members(tokens, info.guarded);
  damp(tokens);
  baulk(tokens, info.guarded);
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
  const skin = lex(head);
  const coat = new Array(skin.length).fill(0);
  numbers(skin);
  members(skin, coat);
  pieces(skin, coat);
  const body = shroud(emit(tokens), wrap, g.params, g.orig);
  const code = emit(skin) + body;
  const err = wrap ? syntax(code) : null;
  if (err) {
    throw new Error('Lỗi cú pháp: ' + err.message);
  }
  return { code };
}

function run(a) {
  let source = filesystem.readFileSync(a, 'utf8');
  if (source.charCodeAt(0) === 0xfeff) source = source.slice(1);
  const b = a.slice(0, -3) + '_obf.js';
  filesystem.writeFileSync(b, make(source).code);
}

const files = process.argv.slice(2);
let fail = 0;
if (!files.length) {
  process.stderr.write('Dùng: node obf.js <file.js> ...\n');
  fail = 1;
}
for (const take of files) {
  if (take.startsWith('-') || !take.endsWith('.js')) {
    process.stderr.write('Cần file .js: ' + take + '\n');
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
