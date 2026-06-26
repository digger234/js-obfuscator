import re, random, sys, os
from itertools import cycle

def tok(t, v): return {'t': t, 'v': v}
def alpha(c): return c.isalpha() or c in '_$' or ord(c) > 127

kwds = {'var','let','const','function','return','if','else','for','while','do','switch','case','break','continue','default','try','catch','finally','throw','new','this','typeof','instanceof','delete','void','in','of','class','extends','import','export','debugger','true','false','null','undefined','async','await','yield','with','super','static','get','set','from','as','target','arguments','eval'}
safe = {'document','window','globalThis','console','Math','JSON','Date','Object','Array','String','Number','Boolean','Function','Promise','Error','Symbol','TypeError','ReferenceError','SyntaxError','RangeError','EvalError','setTimeout','setInterval','clearTimeout','clearInterval','requestAnimationFrame','cancelAnimationFrame','queueMicrotask','location','navigator','localStorage','sessionStorage','history','screen','XMLHttpRequest','fetch','URL','FormData','Blob','FileReader','Headers','Request','Response','WebSocket','Worker','Event','CustomEvent','MouseEvent','KeyboardEvent','HTMLElement','Element','Node','NodeList','MutationObserver','IntersectionObserver','ResizeObserver','Map','Set','WeakMap','WeakSet','Proxy','Reflect','Uint8Array','Int8Array','Uint16Array','Int16Array','Uint32Array','Int32Array','Float32Array','Float64Array','DataView','ArrayBuffer','TextDecoder','TextEncoder','encodeURIComponent','decodeURIComponent','encodeURI','decodeURI','escape','unescape','parseInt','parseFloat','isNaN','isFinite','atob','btoa','alert','confirm','prompt','performance','crypto','Notification','Audio','Image','RegExp','WeakRef','BigInt','Infinity','NaN','GM_xmlhttpRequest','GM_setValue','GM_getValue','GM_deleteValue','GM_listValues','GM_addStyle','GM_getResourceText','GM_info','GM_notification','GM_setClipboard','GM_openInTab','GM_registerMenuCommand','unsafeWindow','GM','GM_cookie'}
base = {'x': '0123456789abcdefABCDEF', 'b': '01', 'o': '01234567'}
b = {'true': '(!![])','false': '(![])','null': '(void 0x0,null)','undefined': '(void 0x0)'}
skip = {'}','break','continue','return','case','default','else',';'}

def scan(src):
    i = 0; n = len(src); out = []; prev = None
    while i < n:
        c = src[i]
        if c in ' \t\r\n': i += 1; continue
        if src[i:i+2] == '//':
            while i < n and src[i] != '\n': i += 1
            continue
        if src[i:i+2] == '/*':
            j = src.find('*/', i+2); i = (j+2) if j >= 0 else n; continue
        if c in ('"', "'"):
            q = c; j = i+1
            while j < n:
                if src[j] == '\\': j += 2
                else:
                    if src[j] == q: j += 1; break
                    else: j += 1
            t = tok('str', src[i:j]); out.append(t); prev = t; i = j; continue
        if c == '`':
            j = i+1
            while j < n:
                if src[j] == '\\': j += 2
                else:
                    if src[j] == '`': j += 1; break
                    else:
                        if src[j:j+2] == '${':
                            d = 1; j += 2
                            while j < n and d > 0:
                                if src[j] == '{': d += 1
                                else:
                                    if src[j] == '}': d -= 1
                                    else:
                                        if src[j] in ('"', "'", '`'):
                                            q = src[j]; j += 1
                                            while j < n:
                                                if src[j] == '\\': j += 2
                                                else:
                                                    if src[j] == q: j += 1; break
                                                    else: j += 1
                                            continue
                                j += 1
                        else: j += 1
            t = tok('tpl', src[i:j]); out.append(t); prev = t; i = j; continue
        if c.isdigit() or (c == '.' and i+1 < n and src[i+1].isdigit()):
            j = i
            if src[j:j+2].lower() in ('0x','0b','0o'):
                r = src[j+1].lower(); j += 2
                z = base.get(r, '01234567')
                while j < n and src[j] in z: j += 1
            else:
                while j < n and (src[j].isdigit() or src[j] == '.'): j += 1
                if j < n and src[j] in ('e','E'):
                    j += 1
                    if j < n and src[j] in '+-': j += 1
                    while j < n and src[j].isdigit(): j += 1
            if j < n and src[j] == 'n': j += 1
            t = tok('num', src[i:j]); out.append(t); prev = t; i = j; continue
        if alpha(c):
            j = i
            while j < n and (alpha(src[j]) or src[j].isdigit()): j += 1
            t = tok('id', src[i:j]); out.append(t); prev = t; i = j; continue
        g = prev and (prev['t'] in ('num','str','tpl','id') or prev['v'] in (')',']','++','--'))
        if c == '/' and not g:
            j = i+1; b = False
            while j < n:
                if src[j] == '\\': j += 2; continue
                if src[j] == '[': b = True
                else:
                    if src[j] == ']': b = False
                    else:
                        if src[j] == '/' and not b: j += 1; break
                j += 1
            while j < n and src[j].isalpha(): j += 1
            t = tok('reg', src[i:j]); out.append(t); prev = t; i = j; continue
        matched = False
        for op in ('>>>=','**=','&&=','||=','??=','<<=','>>=','===','!==','...','++','--','==','!=','+=','-=','*=','/=','%=','&=','|=','^=','&&','||','??','<<','>>','**','<=','>=','=>','?.'):
            if src[i:i+len(op)] == op:
                t = tok('op', op); out.append(t); prev = t; i += len(op); matched = True; break
        if not matched:
            t = tok('op' if c in '+-*/%=<>!&|^~?:.' else 'pun', c)
            out.append(t); prev = t; i += 1
    return out

def fresh(used):
    while True:
        v = '_0x' + hex(random.randint(0x10000, 0xffffff))[2:]
        if v not in used: used.add(v); return v

def splice(s):
    inner = s[1:-1]; result = []; i = 0; cur = ''
    while i < len(inner):
        if inner[i:i+2] == '${':
            result.append(('s', cur)); cur = ''; i += 2; d = 1; w = ''
            while i < len(inner) and d > 0:
                c = inner[i]
                if c == '{': d += 1
                else:
                    if c == '}':
                        d -= 1
                        if d == 0: i += 1; break
                w += c; i += 1
            result.append(('d', w))
        else:
            if inner[i] == '\\': cur += inner[i:i+2]; i += 2
            else: cur += inner[i]; i += 1
    result.append(('s', cur))
    return [p for p in result if p[1] != '' or p[0] == 'd']

def safer(s):
    return s.replace('\\','\\\\').replace('"','\\"').replace('\n','\\n').replace('\r','\\r').replace('\t','\\t').replace('\0','\\0')

def tpl(toks):
    out = []
    for t in toks:
        if t['t'] != 'tpl': out.append(t); continue
        v = t['v']
        if '${' not in v:
            out.append(tok('str', '"' + safer(v[1:-1]) + '"')); continue
        r = splice(v)
        if not r: out.append(tok('str', '""')); continue
        first = True
        for kind, val in r:
            if not first: out.append(tok('op', '+'))
            if kind == 's': out.append(tok('str', '"' + safer(val) + '"'))
            else:
                sub = scan(val)
                if sub:
                    out.append(tok('pun','('))
                    out.extend(sub)
                    out.append(tok('pun',')'))
                else: out.append(tok('str', '""'))
            first = False
    return out

def name(toks, used=None):
    if used is None: used = set()
    skip = set()
    for i, t in enumerate(toks):
        if t['v'] in ('.','?.') and i+1 < len(toks) and toks[i+1]['t'] == 'id': skip.add(i+1)
        if t['v'] == ':' and i > 0 and toks[i-1]['t'] == 'id' and i >= 2 and toks[i-2]['v'] in ('{',','): skip.add(i-1)
        if t['v'] == '(' and i > 0 and toks[i-1]['t'] == 'id' and i >= 2 and toks[i-2]['v'] in ('{',',','}'):
            depth = 1; j = i+1
            while j < len(toks) and depth > 0:
                if toks[j]['v'] == '(': depth += 1
                if toks[j]['v'] == ')': depth -= 1
                j += 1
            if j < len(toks) and toks[j]['v'] == '{': skip.add(i-1)
    mapping = {}
    for i, t in enumerate(toks):
        if i in skip: continue
        if t['t'] == 'id' and t['v'] not in kwds and t['v'] not in safe:
            if t['v'] not in mapping: mapping[t['v']] = fresh(used)
    out = []
    for i, t in enumerate(toks):
        if t['t'] == 'id' and t['v'] in mapping and i not in skip: out.append(tok('id', mapping[t['v']]))
        else: out.append(t)
    return out

def raw(s):
    try:
        q = s[0]
        if q not in ('"', "'"): return None
        r = s[1:-1].encode('raw_unicode_escape').decode('unicode_escape')
        return r if all(ord(c) < 128 for c in r) else None
    except: return None

def enc(s, k):
    q = (k * 31 + 7) & 0x7f
    return ''.join(chr(ord(c) ^ ((k+i)&0x7f) ^ ((q+i*3)&0x7f)) for i,c in enumerate(s))

def roll(s, k):
    r = (k ^ 0x5a) & 0x7f; q = (k * 17 + 3) & 0x7f; out = []
    for i,c in enumerate(s):
        r = (r * 31 + q + i) & 0x7f; q = (q ^ r ^ i) & 0x7f
        out.append(chr(ord(c) ^ r ^ q))
    return ''.join(out)

def cipher(toks):
    pool = []; keys = []; idx = {}
    d = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    a = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    k = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    def push(val):
        if not val or val in idx: return
        if not all(ord(c) < 128 for c in val): return
        n = random.randint(1, 62)
        e = enc(val, n)
        idx[val] = len(pool)
        pool.append(''.join('\\x{:02x}'.format(ord(c)) for c in e))
        keys.append(n)
    for t in toks:
        if t['t'] == 'str': push(raw(t['v']))
    def sub(t, pos):
        if t['t'] == 'str':
            val = raw(t['v'])
            if val and val in idx:
                n = idx[val]
                x = toks[pos+1]['v'] if pos+1 < len(toks) else ''
                if x == ':':
                    return [tok('pun','['), tok('id',d), tok('pun','('), tok('num',str(n)), tok('pun',')'), tok('pun',']')]
                return [tok('id',d), tok('pun','('), tok('num',str(n)), tok('pun',')')]
        return [t]
    out = []
    for i, t in enumerate(toks): out.extend(sub(t, i))
    return out, pool, keys, d, a, k, idx

def h(s):
    return ''.join(chr(int(s[j+2:j+4], 16)) for j in range(0, len(s), 4))

def rot(pool, keys):
    rolled = []; keep = []
    for s, k in zip(pool, keys):
        mid = h(s); orig = enc(mid, k)
        seed = random.randint(1, 62); e = roll(orig, seed)
        rolled.append(''.join('\\x{:02x}'.format(ord(c)) for c in e)); keep.append(seed)
    return rolled, keep

def rolling(d, a, k):
    v = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    w = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    x = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    y = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    j = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    r = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    q = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    e = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    c = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('var ' + c + '={};'
            'function ' + d + '(' + v + '){'
            'if(' + v + ' in ' + c + ')return ' + c + '[' + v + '];'
            'var ' + w + '=' + a + '[' + v + '],' + x + '=' + k + '[' + v + '],' + y + '=\'\',' + j + '=0;'
            'var ' + r + '=(' + x + '^0x5a)&0x7f,' + q + '=(' + x + '*0x11+0x3)&0x7f;'
            'for(;' + j + '<' + w + '.length;' + j + '++){' +
            r + '=(' + r + '*0x1f+' + q + '+' + j + ')&0x7f;' +
            q + '=(' + q + '^' + r + '^' + j + ')&0x7f;' +
            'var ' + e + '=' + r + '^' + q + ';' +
            y + '+=String.fromCharCode(' + w + '.charCodeAt(' + j + ')^' + e + ');' +
            '}'
            'return(' + c + '[' + v + ']=' + y + ');}')

def arrays(pool, keys, a, k):
    return ('var ' + a + '=[' + ','.join('"' + s + '"' for s in pool) + '];'
            + 'var ' + k + '=[' + ','.join(str(v) for v in keys) + '];')

def dec(d, a, k):
    v = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    w = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    x = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    y = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    j = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    e = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    f = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    c = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    return ('var ' + c + '={};'
            'function ' + d + '(' + v + '){'
            'if(' + v + ' in ' + c + ')return ' + c + '[' + v + '];'
            'var ' + w + '=' + a + '[' + v + '],' + x + '=' + k + '[' + v + '],' + y + '=\'\',' + j + '=0;'
            'for(;' + j + '<' + w + '.length;' + j + '++){'
            'var ' + e + '=(' + x + '+' + j + ')&0x7f,'
            + f + '=((' + x + '*0x1f+0x7+' + j + '*0x3)&0x7f);'
            + y + '+=String.fromCharCode((' + w + '.charCodeAt(' + j + ')^' + e + '^' + f + ')>>>0x0);'
            '}'
            'return(' + c + '[' + v + ']=' + y + ');}' )

def flake(s):
    codes = ','.join(str(ord(c)) for c in s)
    v = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return '(function(){var ' + v + '=String.fromCharCode(' + codes + ');return ' + v + ';}())'

def props(toks, d, idx):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('.', '?.') and i+1 < len(toks) and toks[i+1]['t'] == 'id' and toks[i+1]['v'] not in kwds:
            p = toks[i+1]['v']
            if t['v'] == '?.': out.append(tok('op', '?.'))
            if p in idx:
                n = idx[p]
                out.extend([tok('pun','['), tok('id',d), tok('pun','('), tok('num',str(n)), tok('pun',')'), tok('pun',']')])
            else:
                out.extend(scan('[' + flake(p) + ']'))
            i += 2; continue
        out.append(t); i += 1
    return out

def fuse(n):
    k = random.randint(1, 0x7e); j = random.randint(1, 0xff)
    return '(((' + hex(n^k) + '+0x2*' + hex(n&k) + '-' + hex(k) + ')^' + hex(j) + ')^' + hex(j) + ')'

def mba(n):
    m = random.randint(1,0xff); a = random.randint(0,max(0,n)); b = n-a
    k = random.randint(1,0xff); j = random.randint(1,0xff)
    p = random.randint(1,0xff); q = random.randint(1,0xff)
    core = '((' + hex(a^m) + '^' + hex(m) + ')+' + hex(b) + ')'
    level = '((' + core + '^' + hex(k) + ')^' + hex(k) + ')'
    layer = '((' + level + '^' + hex(j) + ')^' + hex(j) + ')'
    depth = '((' + layer + '^' + hex(p) + ')^' + hex(p) + ')'
    return '((' + depth + '^' + hex(q) + ')^' + hex(q) + ')'

def nums(toks):
    out = []
    for t in toks:
        if t['t'] != 'num': out.append(t); continue
        try:
            v = t['v']
            if v.endswith('n') or '.' in v or 'e' in v.lower(): out.append(t); continue
            n = int(v, 0)
            if n > 255: out.extend(scan(bury(n))); continue
            if n >= 50: out.extend(scan(fuse(n))); continue
            out.extend(scan(mba(n))); continue
        except: pass
        out.append(t)
    return out

def bools(toks):
    out = []
    for t in toks:
        if t['t'] == 'id' and t['v'] in b: out.extend(scan(b[t['v']]))
        else: out.append(t)
    return out

def chop(toks):
    parts = []; cur = []; d = 0; i = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('{','(','['):
            d += 1; cur.append(t)
        else:
            if t['v'] in ('}',')',']'):
                if d > 0:
                    d -= 1; cur.append(t)
                else:
                    if cur: parts.append(cur[:]); cur = []
                    parts.append([t]); i += 1; continue
            else:
                if t['v'] == ';' and d == 0:
                    if cur: parts.append(cur[:]); cur = []
                else:
                    cur.append(t)
        i += 1
    if cur: parts.append(cur)
    return [s for s in parts if s and not (len(s)==1 and s[0]['v']=='}')]

def machine(stmts, used):
    if not stmts: return []
    key = random.randint(0x1000, 0x9fff)
    states = []
    while len(states) < len(stmts)+2:
        v = random.randint(0x10000, 0x9ffff)
        if v not in states: states.append(v)
    s = fresh(used); t = fresh(used)
    result = [tok('id','var'), tok('id',s), tok('op','='), tok('num',hex(states[0]^key)), tok('pun',','), tok('id',t), tok('op','='), tok('num',hex(key)), tok('pun',';')]
    cases = []
    for idx, x in enumerate(stmts):
        z = states[idx+1]; q = random.randint(0x1000, 0x9fff)
        step = [tok('id',s), tok('op','='), tok('num',hex(z^q)), tok('pun',','), tok('id',t), tok('op','='), tok('num',hex(q)), tok('pun',';')]
        block = [tok('id','case'), tok('num',str(states[idx])), tok('pun',':'), tok('pun','{')]
        block.extend(x)
        if not (x and x[-1]['v'] in (';','}')):
            block.append(tok('pun',';'))
        block.append(tok('pun','}'))
        block.extend(step)
        block.extend([tok('id','break'), tok('pun',';')])
        cases.extend(block)
    for _ in range(8):
        f = random.randint(0x10000, 0x9ffff)
        if f not in states:
            states.append(f)
            g = fresh(used); b = random.randint(1,0xfe); c = random.randint(1,0xfe)
            cases.extend([tok('id','case'), tok('num',str(f)), tok('pun',':'), tok('pun','{'),
                          tok('id','var'), tok('id',g), tok('op','='), tok('num',hex(b^c)), tok('op','^'), tok('num',hex(c)), tok('pun',';'),
                          tok('pun','}'), tok('id','break'), tok('pun',';')])
    end = states[len(stmts)]
    seed = random.randint(1,0xfe); mask = random.randint(1,0xfe)
    result.extend([tok('id','while'), tok('pun','('), tok('pun','('), tok('id',s), tok('op','^'), tok('id',t), tok('pun',')'), tok('op','!=='), tok('num',str(end)), tok('pun',')'), tok('pun','{')])
    result.extend([tok('id','switch'), tok('pun','('), tok('pun','('), tok('id',s), tok('op','^'), tok('id',t), tok('pun',')'), tok('op','^'), tok('num',hex(seed^mask)), tok('op','^'), tok('num',hex(seed^mask)), tok('pun',')'), tok('pun','{')])
    result.extend(cases)
    result.extend([tok('pun','}'), tok('pun','}')])
    return result

def flat(toks, used):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t['t'] == 'id' and t['v'] == 'function':
            out.append(t); i += 1
            while i < len(toks) and toks[i]['v'] != '{': out.append(toks[i]); i += 1
            if i >= len(toks): break
            out.append(toks[i]); i += 1
            body = []; depth = 1
            while i < len(toks) and depth > 0:
                c = toks[i]
                if c['v'] == '{': depth += 1
                else:
                    if c['v'] == '}':
                        depth -= 1
                        if depth == 0: break
                body.append(c); i += 1
            body = [tok('id','var') if x['t']=='id' and x['v'] in ('let','const') else x for x in body]
            r = any(x['t']=='id' and x['v']=='return' and x['v'] for x in body)
            m = machine(chop(body), used) if not r else None
            if m: out.extend(m)
            else: out.extend(body)
            if i < len(toks): out.append(toks[i]); i += 1
        else: out.append(t); i += 1
    return out

def dead(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','!'), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('num',hex(w)), tok('op','>>'), tok('num','0x0'), tok('op','|'), tok('num',hex(r^r)), tok('pun',')'), tok('pun',',')] + [
            tok('id',d), tok('op','='), tok('id',a), tok('op','^'), tok('id',c), tok('op','|'), tok('num','0x0'), tok('pun',';')]

def ghost(used):
    a = random.randint(1,0xfe); b = random.randint(1,0xfe); g = fresh(used); h = fresh(used); q = fresh(used)
    cond = hex(a^b) + '^' + hex(b) + '===' + hex(a)
    result = [tok('id','if'), tok('pun','(')]
    result.extend(scan(cond))
    result.extend([tok('pun',')'), tok('pun','{'),
        tok('id','var'), tok('id',g), tok('op','='), tok('num',hex(a^b)), tok('op','|'), tok('num',hex(b)), tok('pun',','),
        tok('id',h), tok('op','='), tok('pun','~'), tok('pun','('), tok('pun','~'), tok('id',g), tok('op','+'), tok('num','0x0'), tok('pun',')'), tok('pun',','),
        tok('id',q), tok('op','='), tok('id',g), tok('op','^'), tok('id',h), tok('op','^'), tok('id',h), tok('pun',';'),
        tok('pun','}')])
    return result

def hush(used):
    g = fresh(used); f = fresh(used); r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','void'), tok('pun','('), tok('pun','('), tok('id','function'), tok('pun','('), tok('pun',')'), tok('pun','{'),
            tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(r)), tok('op','+'), tok('num',hex(u)), tok('op','-'), tok('num',hex(r)), tok('pun',')'), tok('op','|'), tok('num',hex(w^w)), tok('pun',';'),
            tok('id','var'), tok('id',f), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','&'), tok('num',hex(u)), tok('op','|'), tok('num',hex(w)), tok('pun',')'), tok('pun',';'),
            tok('pun','}'), tok('pun','('), tok('pun',')'), tok('pun',')'), tok('pun',')'), tok('pun',';')]

def flux(used):
    f = fresh(used); g = fresh(used); h = fresh(used); x = fresh(used)
    u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',f), tok('op','='), tok('pun','['), tok('num',hex(u^w)), tok('op',','), tok('num',hex(u|w)), tok('op',','), tok('num',hex(u&w)), tok('pun',']'), tok('pun',','),
            tok('id',g), tok('op','='), tok('id',f), tok('pun','['), tok('num','0x0'), tok('pun',']'), tok('op','^'), tok('id',f), tok('pun','['), tok('num','0x1'), tok('pun',']'), tok('pun',','),
            tok('id',h), tok('op','='), tok('pun','('), tok('pun','~'), tok('pun','('), tok('id',g), tok('op','|'), tok('num',hex(u)), tok('pun',')'), tok('pun',')'), tok('op','+'), tok('num','0x1'), tok('pun',',')] + [
            tok('id',x), tok('op','='), tok('id',f), tok('pun','['), tok('num','0x2'), tok('pun',']'), tok('op','^'), tok('id',h), tok('op','&'), tok('num','0x0'), tok('pun',';')]

def echo(used):
    f = fresh(used); g = fresh(used); x = fresh(used); y = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',f), tok('op','='), tok('id','function'), tok('pun','('), tok('id',g), tok('pun',')'), tok('pun','{'),
            tok('id','var'), tok('id',y), tok('op','='), tok('id',g), tok('op','^'), tok('num',hex(r)), tok('op','^'), tok('num',hex(r)), tok('pun',';'),
            tok('id','return'), tok('id',y), tok('op','|'), tok('num','0x0'), tok('pun',';'),
            tok('pun','}'), tok('pun',','),
            tok('id',x), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('op','*'), tok('num','0x1'), tok('op','&'), tok('num',hex(w^w^w^w)), tok('pun',')'), tok('pun',';')]

def knot(used):
    f = fresh(used); g = fresh(used); r = fresh(used); q = fresh(used)
    u = random.randint(1,0xfe); w = random.randint(1,0xfe); x = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',f), tok('op','='), tok('id','function'), tok('pun','('), tok('id',g), tok('pun',')'), tok('pun','{'),
            tok('id','var'), tok('id',r), tok('op','='), tok('id',g), tok('op','|'), tok('num','0x0'), tok('op','-'), tok('num','0x0'), tok('pun',';'),
            tok('id','var'), tok('id',q), tok('op','='), tok('pun','~'), tok('pun','('), tok('pun','~'), tok('id',r), tok('op','+'), tok('num','0x0'), tok('pun',')'), tok('pun',';'),
            tok('id','return'), tok('id',q), tok('op','&'), tok('num',hex(u^u)), tok('op','^'), tok('id',q), tok('pun',';'),
            tok('pun','}'), tok('pun',';'),
            tok('id','void'), tok('pun','('), tok('id',f), tok('pun','('), tok('num',hex(x^w)), tok('op','^'), tok('num',hex(w)), tok('pun',')'), tok('pun',')'), tok('pun',';')]

def tinge(used):
    a = fresh(used); b = fresh(used); c = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('num',hex(w)), tok('op','+'), tok('id',a), tok('op','-'), tok('id',a), tok('pun',')'), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('id',b), tok('op','<<'), tok('num','0x0'), tok('op','|'), tok('id',a), tok('pun',')'), tok('pun',';')]

def glaze(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r)), tok('op','*'), tok('num',hex(u)), tok('op','+'), tok('num',hex(w)), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('op','^'), tok('num',hex(r^u)), tok('pun',')'), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('id',b), tok('op','&'), tok('id',a), tok('op','|'), tok('num','0x0'), tok('pun',')'), tok('pun',','),
            tok('id',d), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',c), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','^'), tok('id',c), tok('pun',';')]

def hooke(used):
    a = fresh(used); b = fresh(used); c = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','for'), tok('pun','('), tok('id','var'), tok('id',a), tok('op','='), tok('num','0x0'), tok('pun',';'),] + [
            tok('id',a), tok('op','<'), tok('num','0x1'), tok('pun',';'), tok('id',a), tok('op','++'), tok('pun',')'), tok('pun','{')] + [
            tok('id','var'), tok('id',b), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',',')] + [
            tok('id',c), tok('op','='), tok('pun','('), tok('id',b), tok('op','^'), tok('num',hex(w)), tok('op','^'), tok('id',b), tok('pun',')'), tok('pun',';'),
            tok('pun','}')]

def kane(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe); x = random.randint(1,0xfe)
    return [tok('id','do'), tok('pun','{'), tok('id','var'), tok('id',a), tok('op','='), tok('num',hex(r)), tok('op','|'), tok('num','0x0'), tok('pun',';')] + [
            tok('id','var'), tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('op','&'), tok('id',a), tok('pun',';')] + [
            tok('id','var'), tok('id',c), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',a), tok('op','&'), tok('num',hex(w)), tok('pun',')'), tok('op','|'), tok('id',b), tok('pun',';')] + [
            tok('id','var'), tok('id',d), tok('op','='), tok('num',hex(x)), tok('op','>'), tok('num',hex(x)), tok('pun','?'), tok('id',c), tok('pun',':'), tok('id',a), tok('pun',';'),
            tok('pun','}'), tok('id','while'), tok('pun','('), tok('num','0x0'), tok('pun',')'), tok('pun',';')]

def chalk(toks, d, idx, used):
    out = []; i = 0; p = 0; b = 0; vals = list(idx.values())
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 3 and i+1 < len(toks) and toks[i+1]['v'] not in skip and vals:
            x = vals[0]
            a = fresh(used)
            out.extend([tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('id',d), tok('pun','('), tok('num',str(x)), tok('pun',')'),
                        tok('op','?'), tok('id',d), tok('pun','('), tok('num',str(x)), tok('pun',')'), tok('pun',':'), tok('id',d), tok('pun','('), tok('num',str(x)), tok('pun',')'), tok('pun',')'), tok('pun',';')])
            y = vals[-1] if len(vals) > 1 else vals[0]
            n = fresh(used); m = fresh(used)
            out.extend([tok('id','var'), tok('id',n), tok('op','='), tok('id',d), tok('pun','('), tok('num',str(y)), tok('pun',')'), tok('pun',','),
                        tok('id',m), tok('op','='), tok('pun','('), tok('id',n), tok('op','.'), tok('id','length'), tok('op','+'), tok('num','0x0'), tok('pun',')'), tok('pun',';')])
        i += 1
    return out


def shine(used):
    f = fresh(used); g = fresh(used); h = fresh(used); x = fresh(used); y = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',f), tok('op','='), tok('id','function'), tok('pun','('), tok('id',g), tok('pun',','), tok('id',h), tok('pun',')'), tok('pun','{'),
            tok('id','var'), tok('id',x), tok('op','='), tok('id',g), tok('op','^'), tok('id',h), tok('pun',','),
            tok('id',y), tok('op','='), tok('id',x), tok('op','|'), tok('num','0x0'), tok('pun',';'),
            tok('id','return'), tok('id',y), tok('op','&'), tok('num',hex(u^u)), tok('op','^'), tok('id',x), tok('pun',';'),
            tok('pun','}'), tok('pun',';'),
            tok('id','void'), tok('pun','('), tok('id',f), tok('pun','('), tok('num',hex(r^u)), tok('op',','), tok('num',hex(u^w)), tok('pun',')'), tok('pun',')'), tok('pun',';')]

def quirk(used):
    f = fresh(used); g = fresh(used); h = fresh(used); x = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','do'), tok('pun','{'), tok('id','var'), tok('id',f), tok('op','='), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',','),
            tok('id',g), tok('op','='), tok('pun','('), tok('id',f), tok('op','>>'), tok('num','0x1'), tok('op','<<'), tok('num','0x1'), tok('pun',')'), tok('pun',','),
            tok('id',h), tok('op','='), tok('id',f), tok('op','-'), tok('id',g), tok('pun',','),
            tok('id',x), tok('op','='), tok('pun','('), tok('id',g), tok('op','^'), tok('id',h), tok('op','|'), tok('num','0x0'), tok('pun',')'), tok('pun',';'),
            tok('pun','}'), tok('id','while'), tok('pun','('), tok('num','0x0'), tok('pun',')'), tok('pun',';')]

def wisp(used):
    f = fresh(used); g = fresh(used); h = fresh(used); x = fresh(used); y = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','void'), tok('pun','('), tok('id','function'), tok('pun','('), tok('id',g), tok('pun',','), tok('id',h), tok('pun',')'), tok('pun','{'),
            tok('id','var'), tok('id',f), tok('op','='), tok('id',g), tok('op','^'), tok('id',h), tok('op','|'), tok('num','0x0'), tok('pun',','),
            tok('id',x), tok('op','='), tok('pun','('), tok('id',f), tok('op','&'), tok('id',g), tok('pun',')'), tok('op','|'), tok('num','0x0'), tok('pun',','),
            tok('id',y), tok('op','='), tok('pun','~'), tok('id',x), tok('op','+'), tok('num','0x1'), tok('op','+'), tok('id',f), tok('pun',';'),
            tok('pun','}'), tok('pun','('), tok('num',hex(r^u)), tok('op',','), tok('num',hex(u^w)), tok('pun',')'), tok('pun',')'), tok('pun',';')]

def surge(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used); f = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r<<1>>1)), tok('op','|'), tok('num','0x0'), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('num',hex(u&r)), tok('op','&'), tok('num',hex(r)), tok('pun',')'), tok('pun',','),
            tok('id',c), tok('op','='), tok('id',a), tok('op','^'), tok('id',b), tok('op','&'), tok('num','0x0'), tok('pun',','),
            tok('id',d), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',a), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',a), tok('pun',','),
            tok('id',e), tok('op','='), tok('pun','('), tok('id',c), tok('op','>>'), tok('num','0x10'), tok('op','<<'), tok('num','0x10'), tok('pun',')'), tok('pun',','),
            tok('id',f), tok('op','='), tok('id',e), tok('op','^'), tok('id',d), tok('op','|'), tok('num','0x0'), tok('pun',';'),
            tok('id','void'), tok('pun','('), tok('id','function'), tok('pun','('), tok('id',a), tok('pun',','), tok('id',c), tok('pun',')'), tok('pun','{'),
            tok('id','var'), tok('id',d), tok('op','='), tok('id',a), tok('op','^'), tok('id',c), tok('op','|'), tok('num','0x0'), tok('pun',';'),
            tok('id','return'), tok('id',d), tok('op','&'), tok('num',hex(w^w)), tok('op','^'), tok('id',d), tok('pun',';'),
            tok('pun','}'), tok('pun','('), tok('num',hex(u^w)), tok('op',','), tok('num',hex(w)), tok('pun',')'), tok('pun',')'), tok('pun',';')]

def blip(used):
    a = fresh(used); b = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe)
    return [tok('id','try'), tok('pun','{'),
            tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',a), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',a), tok('pun',';'),
            tok('pun','}'), tok('id','catch'), tok('pun','('), tok('id','e'), tok('pun',')'), tok('pun','{'), tok('pun','}')]

def hatch(used):
    a = fresh(used); b = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe)
    return [tok('id','switch'), tok('pun','('), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',')'), tok('pun','{'),
            tok('id','case'), tok('num',hex(r)), tok('pun',':'),
            tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(u^r)), tok('op','^'), tok('num',hex(r)), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('op','&'), tok('num','0x0'), tok('op','|'), tok('id',a), tok('pun',')'), tok('pun',';'),
            tok('id','break'), tok('pun',';'),
            tok('pun','}')]

def pike(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','try'), tok('pun','{'),
            tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('op','>>>'), tok('num','0x0'), tok('pun',')'), tok('op','^'), tok('num',hex(w^w)), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',b), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',b), tok('pun',','),
            tok('id',d), tok('op','='), tok('id',c), tok('op','*'), tok('num','0x1'), tok('op','&'), tok('num','0x0'), tok('pun',','),
            tok('id',e), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',d), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',d), tok('op','^'), tok('num','0x0'), tok('pun',';'),
            tok('pun','}'), tok('id','catch'), tok('pun','('), tok('id','e'), tok('pun',')'), tok('pun','{'), tok('pun','}')]

def rack(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','['), tok('num',hex(r)), tok('pun',','), tok('num',hex(u)), tok('pun',','), tok('num',hex(w)), tok('pun',']'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('pun','['), tok('num','0x0'), tok('pun',']'), tok('op','&'), tok('id',a), tok('pun','['), tok('num','0x1'), tok('pun',']'), tok('pun',')'), tok('op','^'), tok('num','0x0'), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',b), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',b), tok('pun',','),
            tok('id',d), tok('op','='), tok('id',c), tok('op','|'), tok('id',a), tok('pun','['), tok('num','0x2'), tok('pun',']'), tok('op','&'), tok('num','0x0'), tok('pun',','),
            tok('id',e), tok('op','='), tok('pun','('), tok('id',d), tok('op','>>'), tok('num','0x10'), tok('op','<<'), tok('num','0x10'), tok('pun',')'), tok('op','^'), tok('id',b), tok('op','&'), tok('num','0x0'), tok('pun',';')]

def coil(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r)), tok('op','<<'), tok('num','0x0'), tok('op','|'), tok('num','0x0'), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('op','>>>'), tok('num','0x1'), tok('pun',')'), tok('op','|'), tok('num','0x0'), tok('pun',','),
            tok('id',c), tok('op','='), tok('id',b), tok('op','^'), tok('id',a), tok('op','&'), tok('num','0x0'), tok('pun',','),
            tok('id',d), tok('op','='), tok('pun','('), tok('id',a), tok('op','*'), tok('num','0x1'), tok('op','+'), tok('num',hex(u^u)), tok('pun',')'), tok('pun',','),
            tok('id',e), tok('op','='), tok('id',d), tok('op','-'), tok('id',b), tok('op','&'), tok('num','0x0'), tok('pun',';')]

def snarl(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','['), tok('num',hex(r^u)), tok('pun',','), tok('num',hex(u^w)), tok('pun',','), tok('num',hex(r^w)), tok('pun',']'), tok('pun',','),
            tok('id',b), tok('op','='), tok('id',a), tok('pun','['), tok('num','0x0'), tok('pun',']'), tok('op','^'), tok('id',a), tok('pun','['), tok('num','0x1'), tok('pun',']'), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('id',b), tok('op','|'), tok('id',a), tok('pun','['), tok('num','0x2'), tok('pun',']'), tok('pun',')'), tok('op','&'), tok('num','0x0'), tok('pun',','),
            tok('id',d), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',b), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',b), tok('pun',','),
            tok('id',e), tok('op','='), tok('id',c), tok('op','^'), tok('id',d), tok('op','|'), tok('num','0x0'), tok('pun',';')]

def grit(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r<<1>>1)), tok('op','>>>'), tok('num','0x0'), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('op','^'), tok('num',hex(u^u)), tok('op','|'), tok('num',hex(w)), tok('pun',')'), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('id',b), tok('op','>>'), tok('num','0x10'), tok('op','<<'), tok('num','0x10'), tok('pun',')'), tok('pun',','),
            tok('id',d), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',c), tok('op','^'), tok('pun','~'), tok('id',a), tok('pun',')'), tok('op','&'), tok('num','0x0'), tok('pun',';')]

def rune(used):
    f = fresh(used); n = fresh(used); r = fresh(used)
    dep = random.randint(2, 4); mask = random.randint(1, 0xfe)
    return [tok('id','var'), tok('id',r), tok('op','='),
            tok('pun','('), tok('id','function'), tok('id',f), tok('pun','('), tok('id',n), tok('pun',')'), tok('pun','{'),
            tok('id','if'), tok('pun','('), tok('id',n), tok('op','<='), tok('num','0x0'), tok('pun',')'),
            tok('id','return'), tok('pun','('), tok('num',hex(mask)), tok('op','^'), tok('num',hex(mask)), tok('op','|'), tok('num','0x0'), tok('pun',')'), tok('pun',';'),
            tok('id','return'), tok('id',f), tok('pun','('), tok('id',n), tok('op','-'), tok('num','0x1'), tok('pun',')'), tok('op','&'), tok('num','0x0'), tok('pun',';'),
            tok('pun','}'), tok('pun','('), tok('num',hex(dep)), tok('pun',')'), tok('pun',')'), tok('pun',';')]

def meld(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','{'),
            tok('str','\'p\''), tok('pun',':'), tok('num',hex(r^u)), tok('pun',','),
            tok('str','\'q\''), tok('pun',':'), tok('num',hex(u^w)), tok('pun','}'), tok('pun',','),
            tok('id',b), tok('op','='), tok('id',a), tok('pun','['), tok('str','\'p\''), tok('pun',']'), tok('op','^'), tok('id',a), tok('pun','['), tok('str','\'q\''), tok('pun',']'), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',b), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',b), tok('pun',','),
            tok('id',d), tok('op','='), tok('id',c), tok('op','&'), tok('num','0x0'), tok('op','^'), tok('num',hex(w^w)), tok('pun',';')]

def lure(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','['), tok('num',hex(r^u)), tok('pun',','), tok('num',hex(u^w)), tok('pun',','), tok('num',hex(w^r)), tok('pun',']'), tok('pun',','),
            tok('id',b), tok('op','='), tok('id',a), tok('pun','['), tok('num','0x0'), tok('pun',']'), tok('op','^'), tok('id',a), tok('pun','['), tok('num','0x1'), tok('pun',']'), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('id',b), tok('op','|'), tok('num','0x0'), tok('pun',')'), tok('op','^'), tok('id',a), tok('pun','['), tok('num','0x2'), tok('pun',']'), tok('pun',','),
            tok('id',d), tok('op','='), tok('pun','~'), tok('id',c), tok('op','+'), tok('num','0x1'), tok('op','+'), tok('id',c), tok('pun',','),
            tok('id',e), tok('op','='), tok('pun','('), tok('id',d), tok('op','*'), tok('num','0x1'), tok('op','&'), tok('num','0x0'), tok('pun',')'), tok('op','^'), tok('id',b), tok('pun',';')]

def molt(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used); f = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r)), tok('op','<<'), tok('num','0x1'), tok('op','>>'), tok('num','0x1'), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('op','>>>'), tok('num','0x0'), tok('pun',')'), tok('op','&'), tok('num',hex(u)), tok('pun',','),
            tok('id',c), tok('op','='), tok('id',b), tok('op','^'), tok('pun','('), tok('id',a), tok('op','&'), tok('num','0xff'), tok('pun',')'), tok('pun',','),
            tok('id',d), tok('op','='), tok('pun','('), tok('id',c), tok('op','+'), tok('num','0x0'), tok('pun',')'), tok('op','|'), tok('num','0x0'), tok('pun',','),
            tok('id',e), tok('op','='), tok('id',d), tok('op','>>'), tok('num','0x0'), tok('op','^'), tok('id',d), tok('pun',','),
            tok('id',f), tok('op','='), tok('pun','~'), tok('pun','('), tok('id',e), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',e), tok('op','+'), tok('num','0x1'), tok('pun',';')]

def weld(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','try'), tok('pun','{'),
            tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','|'), tok('num','0x0'), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('num',hex(u)), tok('op','&'), tok('id',a), tok('pun',')'), tok('op','^'), tok('id',a), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',b), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',b), tok('pun',','),
            tok('id',d), tok('op','='), tok('pun','('), tok('id',c), tok('op','*'), tok('num','0x1'), tok('op','^'), tok('num',hex(w^w)), tok('pun',')'), tok('pun',';'),
            tok('id','if'), tok('pun','('), tok('id',d), tok('op','!=='), tok('num',hex(w^w)), tok('pun',')'), tok('pun','{'), tok('id','void'), tok('pun','('), tok('num','0x0'), tok('pun',')'), tok('pun',';'), tok('pun','}'),
            tok('pun','}'), tok('id','catch'), tok('pun','('), tok('id','e'), tok('pun',')'), tok('pun','{'), tok('pun','}'), tok('pun',';')]

def fend(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('num',hex(r|u)), tok('op','>>>'), tok('num','0x0'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('op','^'), tok('num',hex(r)), tok('pun',')'), tok('op','&'), tok('num','0xff'), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('id',b), tok('op','|'), tok('id',a), tok('pun',')'), tok('op','^'), tok('id',a), tok('pun',','),
            tok('id',d), tok('op','='), tok('id',c), tok('op','>>'), tok('num','0x0'), tok('op','&'), tok('num','0x0'), tok('pun',','),
            tok('id',e), tok('op','='), tok('pun','~'), tok('id',d), tok('op','+'), tok('num','0x1'), tok('op','+'), tok('id',d), tok('pun',';')]

def sway(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used); f = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('op','<<'), tok('num','0x1'), tok('op','>>'), tok('num','0x1'), tok('pun',')'), tok('pun',','),
            tok('id',c), tok('op','='), tok('id',b), tok('op','&'), tok('num',hex(w)), tok('op','|'), tok('pun','('), tok('id',a), tok('op','^'), tok('id',b), tok('pun',')'), tok('pun',','),
            tok('id',d), tok('op','='), tok('pun','~'), tok('id',c), tok('op','+'), tok('num','0x1'), tok('op','+'), tok('id',c), tok('pun',','),
            tok('id',e), tok('op','='), tok('id',d), tok('op','*'), tok('num','0x1'), tok('op','^'), tok('num','0x0'), tok('pun',','),
            tok('id',f), tok('op','='), tok('pun','('), tok('id',e), tok('op','>>>'), tok('num','0x0'), tok('pun',')'), tok('op','^'), tok('id',a), tok('op','&'), tok('num','0x0'), tok('pun',';')]

def hulk(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','void'), tok('pun','('), tok('id','function'), tok('pun','('), tok('pun',')'), tok('pun','{'),
            tok('id','var'), tok('id',a), tok('op','='), tok('num',hex(r^u^w)), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('op','&'), tok('num',hex(u)), tok('pun',')'), tok('op','^'), tok('id',a), tok('pun',','),
            tok('id',c), tok('op','='), tok('id',b), tok('op','>>'), tok('num','0x1'), tok('op','<<'), tok('num','0x1'), tok('pun',','),
            tok('id',d), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',c), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',c), tok('pun',';'),
            tok('id','return'), tok('id',d), tok('op','&'), tok('num','0x0'), tok('pun',';'),
            tok('pun','}'), tok('pun','('), tok('pun',')'), tok('pun',')'), tok('pun',';')]

def bray(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('pun','('), tok('num',hex(r)), tok('op','|'), tok('num',hex(u)), tok('pun',')'), tok('op','^'), tok('num',hex(r^u)), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','('), tok('id',a), tok('op','+'), tok('pun','('), tok('pun','~'), tok('id',a), tok('pun',')'), tok('pun',')'), tok('op','&'), tok('num','0x0'), tok('pun',','),
            tok('id',c), tok('op','='), tok('id',b), tok('op','|'), tok('id',a), tok('op','&'), tok('num','0x0'), tok('pun',','),
            tok('id',d), tok('op','='), tok('id',c), tok('op','^'), tok('pun','('), tok('id',a), tok('op','&'), tok('num',hex(w)), tok('pun',')'), tok('pun',','),
            tok('id',e), tok('op','='), tok('pun','~'), tok('id',d), tok('op','+'), tok('num','0x1'), tok('op','+'), tok('id',d), tok('pun',';')]

def dray(used):
    a = fresh(used); b = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used); f = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('num',hex(r)), tok('op','+'), tok('pun','('), tok('pun','~'), tok('num',hex(r)), tok('pun',')'), tok('op','+'), tok('num','0x1'), tok('pun',','),
            tok('id',b), tok('op','='), tok('id',a), tok('op','|'), tok('num',hex(u)), tok('op','^'), tok('num',hex(u)), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('id',b), tok('op','>>>'), tok('num','0x0'), tok('pun',')'), tok('op','&'), tok('num',hex(w^w)), tok('pun',','),
            tok('id',d), tok('op','='), tok('id',c), tok('op','^'), tok('id',b), tok('op','&'), tok('num','0x0'), tok('pun',','),
            tok('id',e), tok('op','='), tok('pun','~'), tok('pun','('), tok('id',d), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',d), tok('op','+'), tok('num','0x1'), tok('pun',','),
            tok('id',f), tok('op','='), tok('pun','('), tok('id',e), tok('op','*'), tok('num','0x1'), tok('op','+'), tok('num','0x0'), tok('pun',')'), tok('op','&'), tok('num','0x0'), tok('pun',';')]

bank = [dead, ghost, hush, flux, echo, knot, tinge, glaze, hooke, kane, shine, quirk, wisp, surge, blip, hatch, snarl, grit, rack, coil, rune, pike, lure, molt, weld, fend, sway, hulk, bray, dray]

def fill(toks, used):
    out = []; i = 0; p = 0; b = 0; seq = cycle(bank)
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 3 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            out.extend(next(seq)(used)); out.extend(next(seq)(used))
            r = random.randint(1,0xfe); u = random.randint(1,0xfe); g = fresh(used)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',';')])
            out.extend(trap(used))
        i += 1
    return out

def inject(toks, used):
    out = []; i = 0; b = 0; seq = cycle(bank)
    while i < len(toks):
        t = toks[i]
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == '{' and i > 0 and b >= 3:
            prev = toks[i-1]['v']
            v = prev in ('else', 'do', 'try', 'finally', '{')
            if prev == ')':
                d = 1; j = i - 2
                while j >= 0 and d > 0:
                    if toks[j]['v'] == ')': d += 1
                    if toks[j]['v'] == '(': d -= 1
                    j -= 1
                v = j >= 0 and toks[j]['v'] != 'switch'
            if v:
                out.extend(next(seq)(used)); out.extend(next(seq)(used))
        i += 1
    return out

def body(toks, i):
    j = i + 1
    while j < len(toks) and toks[j]['v'] not in ('{', ';'): j += 1
    return j < len(toks) and toks[j]['v'] == '{'

def alias(toks, used):
    out = []; i = 0; depth = 0; g = False
    while i < len(toks):
        t = toks[i]
        if t['t'] == 'id' and t['v'] == 'function' and body(toks, i): g = True
        if t['v'] == '{' and g:
            depth += 1
            if depth == 1:
                out.append(t); i += 1
                x = fresh(used); y = fresh(used); z = fresh(used); r = fresh(used)
                u = random.randint(1,0xfe); w = random.randint(1,0xfe)
                p = fresh(used); q = fresh(used)
                n = fresh(used); s = fresh(used)
                out.extend([tok('id','var'), tok('id',x), tok('op','='), tok('id','globalThis'), tok('pun',','),
                             tok('id',y), tok('op','='), tok('id','Math'), tok('pun',','),
                             tok('id',n), tok('op','='), tok('id','Number'), tok('pun',','),
                             tok('id',s), tok('op','='), tok('id','String'), tok('pun',','),
                             tok('id',z), tok('op','='), tok('num',hex(random.randint(1,0xfe)^random.randint(1,0xfe))), tok('pun',','),
                             tok('id',r), tok('op','='), tok('pun','('), tok('num',hex(u^w)), tok('op','^'), tok('num',hex(w)), tok('pun',')'), tok('pun',','),
                             tok('id',p), tok('op','='), tok('pun','('), tok('num',hex(u|w)), tok('op','&'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
                             tok('id',q), tok('op','='), tok('id',p), tok('op','^'), tok('id',z), tok('pun',';')])
                r2 = fresh(used); u2 = random.randint(1,0xfe); w2 = random.randint(1,0xfe)
                q2 = fresh(used); z2 = fresh(used)
                out.extend([tok('id','var'), tok('id',r2), tok('op','='), tok('id','function'), tok('pun','('), tok('pun',')'), tok('pun','{'),
                             tok('id','return'), tok('pun','('), tok('num',hex(u2^w2)), tok('op','^'), tok('num',hex(w2)), tok('pun',')'), tok('pun',';'),
                             tok('pun','}'), tok('pun',','),
                             tok('id',q2), tok('op','='), tok('num',hex(u2^w2)), tok('op','^'), tok('num',hex(w2)), tok('pun',','),
                             tok('id',z2), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',q2), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',q2), tok('pun',';')])
                g = False; continue
        if t['v'] == '}' and depth > 0:
            depth -= 1
            if depth == 0: g = False
        out.append(t); i += 1
    return out

def extra(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        if t['t'] == 'id' and t['v'] == 'void' and i+1 < len(toks) and toks[i+1]['t'] == 'num':
            masked = mask([t, toks[i+1]])
            out.extend(masked); i += 2; continue
        if t['t'] == 'id' and t['v'] == 'break' and p == 0 and b >= 1 and i > 0 and toks[i-1]['v'] in (';','{'):
            x = fresh(used); r = random.randint(1,0xfe); u = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',x), tok('op','='), tok('pun','('), tok('num',hex(r)), tok('op','|'), tok('num',hex(u)), tok('pun',')'), tok('pun',';')])
        out.append(t); i += 1
    return out

def morph(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        if t['t'] == 'id' and t['v'] == 'return' and p == 0 and b >= 2 and i > 0 and toks[i-1]['v'] in (';','{'):
            g = fresh(used); r = random.randint(1,0xfe); u = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('num',hex(r|u)), tok('op','^'), tok('num',hex(r)), tok('pun',';')])
            g2 = fresh(used); r2 = fresh(used); u2 = random.randint(1,0xfe); w2 = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g2), tok('op','='), tok('num',hex(u2^w2)), tok('op','|'), tok('num','0x0'), tok('pun',';'),
                        tok('id','var'), tok('id',r2), tok('op','='), tok('pun','~'), tok('pun','('), tok('id',g2), tok('op','^'), tok('num',hex(u2)), tok('pun',')'), tok('pun',';')])
        if b >= 4: out.extend(tangle([tok('pun',';')], used)[1:])
        out.append(t); i += 1
    return out

def cloak(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        if t['t'] == 'id' and t['v'] == 'const' and p == 0 and b >= 2 and i > 0 and toks[i-1]['v'] in (';','{'):
            r = fresh(used); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',r), tok('op','='), tok('num',hex(u|w)), tok('pun',';')])
        out.append(t); i += 1
    return out

def opaque():
    a = random.randint(1, 0xfe); b = random.randint(1, 0xfe)
    return '(' + hex(a^b) + '^' + hex(b) + ')===' + hex(a)

def noop(used):
    result = [tok('id','void'), tok('pun','(')]
    result.extend(scan(opaque()))
    result.extend([tok('pun',')'), tok('pun',';')])
    return result

def shuffle(pool, keys):
    n = len(pool)
    order = list(range(n)); random.shuffle(order)
    p = [pool[o] for o in order]; r = [keys[o] for o in order]
    inv = [0]*n
    for new, old in enumerate(order): inv[old] = new
    return p, r, inv

def map(toks, inv, d):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t['t'] == 'id' and t['v'] == d and i+2 < len(toks) and toks[i+1]['v'] == '(' and toks[i+2]['t'] == 'num':
            try:
                old = int(toks[i+2]['v'], 0)
                if old < len(inv):
                    out.append(t); out.append(toks[i+1]); out.append(tok('num', str(inv[old]))); i += 3
                    continue
            except: pass
        out.append(t); i += 1
    return out

def split(s):
    if len(s) < 12: return None
    mid = len(s) // 2
    return s[:mid], s[mid:]

def trice(s):
    if len(s) < 18: return None
    a = len(s) // 3; b = a + len(s) // 3
    return s[:a], s[a:b], s[b:]

def pairs(pool, keys, idx, snap):
    add = {}
    for key, pos in list(snap.items()):
        tri = trice(key)
        if tri is not None:
            p, q, r = tri
            for v in (p, q, r):
                if v not in idx:
                    n = random.randint(1, 62); e = enc(v, n)
                    idx[v] = len(pool); pool.append(''.join('\\x{:02x}'.format(ord(c)) for c in e)); keys.append(n)
            add[pos] = ('tri', idx[p], idx[q], idx[r]); continue
        seg = split(key)
        if seg is None: continue
        x, y = seg
        if x not in idx:
            n = random.randint(1, 62); e = enc(x, n)
            idx[x] = len(pool); pool.append(''.join('\\x{:02x}'.format(ord(c)) for c in e)); keys.append(n)
        if y not in idx:
            n = random.randint(1, 62); e = enc(y, n)
            idx[y] = len(pool); pool.append(''.join('\\x{:02x}'.format(ord(c)) for c in e)); keys.append(n)
        add[pos] = (idx[x], idx[y])
    return add

def link(toks, d, mapping):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t['t'] == 'id' and t['v'] == d and i+3 < len(toks) and toks[i+1]['v'] == '(' and toks[i+2]['t'] == 'num' and toks[i+3]['v'] == ')':
            try:
                pos = int(toks[i+2]['v'], 0)
                if pos in mapping:
                    entry = mapping[pos]
                    if entry[0] == 'tri':
                        _, p, q, r = entry
                        out.extend([tok('pun','('), tok('id',d), tok('pun','('), tok('num',str(p)), tok('pun',')'),
                                     tok('op','+'), tok('id',d), tok('pun','('), tok('num',str(q)), tok('pun',')'),
                                     tok('op','+'), tok('id',d), tok('pun','('), tok('num',str(r)), tok('pun',')'), tok('pun',')')])
                    else:
                        x, y = entry
                        out.extend([tok('pun','('), tok('id',d), tok('pun','('), tok('num',str(x)), tok('pun',')'),
                                     tok('op','+'), tok('id',d), tok('pun','('), tok('num',str(y)), tok('pun',')'), tok('pun',')')])
                    i += 4; continue
            except: pass
        out.append(t); i += 1
    return out

def grain(pool, keys, idx):
    for val in list(idx.keys()):
        if len(val) < 3: continue
        r = val[1:] + val[:1]
        if r not in idx:
            n = random.randint(1, 62); e = enc(r, n)
            idx[r] = len(pool); pool.append(''.join('\\x{:02x}'.format(ord(c)) for c in e)); keys.append(n)

def twist(pool, keys, a, q):
    n = len(pool)
    if n < 2: return pool, keys, ''
    r = random.randint(1, max(1, n - 1))
    p = [pool[(j + r) % n] for j in range(n)]
    g = [keys[(j + r) % n] for j in range(n)]
    s = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    code = ('(function(){var ' + s + '=' + mba(r) + ';'
            'while(' + s + '-->0x0){' + a + '.unshift(' + a + '.pop());' + q + '.unshift(' + q + '.pop());}'
            '}());')
    return p, g, code

def swap(toks, old, new):
    return [tok('id', new) if t['t'] == 'id' and t['v'] == old else t for t in toks]


def comma(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 3 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            r = random.randint(1,0xfe); u = random.randint(1,0xfe); g = fresh(used)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',';')])
        i += 1
    return out

def bury(n):
    if n <= 3: return mba(n)
    a = random.randint(1, n - 2); b = random.randint(1, n - a - 1); c = n - a - b
    r = random.randint(1, 0xff); s = random.randint(1, 0xff)
    return '(((' + mba(a) + '+' + mba(b) + '+' + mba(c) + ')^' + hex(r) + ')^' + hex(r) + ')'

def mask(toks):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t['t'] == 'id' and t['v'] == 'void' and i+1 < len(toks) and toks[i+1]['t'] == 'num':
            r = random.randint(1, 0xfe)
            out.extend([tok('id','void'), tok('pun','('), tok('num',hex(r)), tok('op','^'), tok('num',hex(r)), tok('op','|'), toks[i+1], tok('pun',')')])
            i += 2; continue
        out.append(t); i += 1
    return out

def chain(toks, d, idx):
    out = []; i = 0; vals = list(idx.values())
    while i < len(toks):
        t = toks[i]
        if t['t'] == 'id' and t['v'] == d and i+3 < len(toks) and toks[i+1]['v'] == '(' and toks[i+2]['t'] == 'num' and toks[i+3]['v'] == ')':
            try:
                n = int(toks[i+2]['v'], 0)
                alt = [v for v in vals if v != n]
                if alt:
                    x = alt[0]
                    out.extend([tok('pun','('), tok('id',d), tok('pun','('), tok('num',str(x)), tok('pun',')'),
                                 tok('op',','), tok('id',d), tok('pun','('), tok('num',str(n)), tok('pun',')'), tok('pun',')')])
                    i += 4; continue
            except: pass
        out.append(t); i += 1
    return out

def lit(toks):
    out = []
    for t in toks:
        if t['t'] == 'str':
            r = raw(t['v'])
            if r and len(r) >= 2 and all(ord(c) < 128 for c in r):
                k = random.randint(1, 0x3f)
                enc = [ord(c)^k for c in r]
                v = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
                code = ('(' + chars('fromCharCode') + ')' if False else
                        '(function(){var ' + v + '=[' + ','.join(str(x) for x in enc) + '];return ' + v +
                        '.map(function(c){return String.fromCharCode(c^' + str(k) + ');}).join(\'\');}())')
                out.extend(scan(code)); continue
        out.append(t)
    return out

def encode(toks):
    def conv(v):
        return v[:2] + '\\u{:04x}'.format(ord(v[2])) + v[3:]
    return [tok('id', conv(t['v'])) if t['t'] == 'id' and t['v'].startswith('_0x') else t for t in toks]

def word(c): return c.isalnum() or c in '_$\\' or ord(c) > 127

def gap(a, b):
    if not a or not b: return False
    if word(a) and word(b[0]): return True
    if a in ('+','-') and b[0] in ('+','-'): return True
    return False

def emit(toks):
    parts = []; prev = ''
    for t in toks:
        v = t['v']
        if prev and gap(prev[-1], v): parts.append(' ')
        parts.append(v); prev = v
    return ''.join(parts)

def chars(s):
    return 'String.fromCharCode(' + ','.join(str(ord(c)) for c in s) + ')'

def val(s):
    k = random.randint(1, 0x3f)
    enc = [ord(c)^k for c in s]
    v = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){var ' + v + '=[' + ','.join(str(x) for x in enc) + '];return ' + v + '.map(function(c){return c^' + str(k) + ';}).map(function(c){return String.fromCharCode(c);}).join("");}())')

def probe():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){var f=function(){var ' + s + '=new RegExp(' + chars(r'\r?\n( {4}|\t)') + ');if(' + s + '.test(f.toString()))throw new Error();};f();}());')

def snare():
    d = chars('debugger')
    return ('(function(){var t=Date.now(),f=function(){(new Function(' + d + '))();if(Date.now()-t>600)throw new Error();t=Date.now();};f();var timer=setInterval(f,500);if(timer&&timer.unref)timer.unref();}());')

def guard():
    mark = val('[native code]')
    return ('(function(){try{if(Math.abs.toString().indexOf(' + mark +')===-1)throw new Error();if(Function.prototype.toString.toString().indexOf(' + mark +')===-1)throw new Error();}catch(e){throw new Error();}}());')

def cage():
    mark = val('[native code]')
    return ('(function(){try{if(Function.prototype.bind.toString().indexOf(' + mark +')===-1)throw new Error();}catch(e){throw new Error();}}());')

def save():
    f = hex((0x7a|0x1)^0x2); c = hex(0x40|0x9); g = hex(0x40|0xa); h = hex(0x50|0x15)
    evk = chars('keydown')
    return ('(function(){document.addEventListener(' + evk + ',function(e){if(e.keyCode===' + f + '||(e.ctrlKey&&e.shiftKey&&(e.keyCode===' + c + '||e.keyCode===' + g + '))||(e.ctrlKey&&e.keyCode===' + h + ')){e.preventDefault();e.stopPropagation();}});}());')

def leak():
    return ('(function(){var r=function(){try{r();}catch(e){var a=[];for(var i=(0x0|0x0);i<(0x2000|0x710);i++)a.push(i);}};try{r();}catch(e){}}());')

def tamper():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    u = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    d = chars('debugger')
    return ('(function(){var ' + s + '=Date.now();var ' + t + '=function(){return Date.now()-' + s + ';};var ' + u + '=new Function(' + d + ');try{' + u + '();}catch(e){}if(' + t + '()>800)throw new Error();}());')

def block():
    type = chars('function'); cx = chars('clear')
    return ('(function(){try{if(typeof console[' + cx + ']!==' + type +')throw new Error();}catch(e){}}());')

def dom():
    u = chars('undefined'); ce = chars('createElement')
    return ('(function(){try{if(typeof document===' + u + '||!document[' + ce + '])throw new Error();}catch(e){}}());')

def timing():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){var ' + s + '=Date.now();for(var ' + t + '=(0x0|0x0);' + t + '<(0x186a0|0x0);' + t + '++);if(Date.now()-' + s + '>800)throw new Error();}());')

def hooks():
    name = chars('name')
    return ('(function(){try{var f=function(){};Object.defineProperty(f,' + name + ',{get:function(){throw new Error();}});f.name;}catch(e){}}());')

def detect():
    e = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    r = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    i = chars('id')
    return ('(function(){try{var ' + e + '=new Image();Object.defineProperty(' + e + ',' + i + ',{get:function(){throw new Error();}});' + e + '[' + i + '];}catch(' + r + '){}}());')

def watch():
    mark = val('[native code]')
    return ('(function(){try{if(Function.prototype.call.toString().indexOf(' + mark +')===-1)throw new Error();}catch(e){}}());')

def frame():
    u = chars('undefined')
    return ('(function(){try{if(typeof window!==' + u + '&&window.top!==window.self)throw new Error();}catch(e){}}());')

def net():
    a = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    pat = val('[object Object]')
    return ('(function(){try{var ' + a + '=new RegExp(' + pat + ');if(!' + a + '.test(Object.prototype.toString.call({})))throw new Error();}catch(e){}}());')

def crypt():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    empty = chars('^$')
    return ('(function(){try{var ' + s + '=!RegExp(' + empty + ');if(!' + s + ')throw new Error();}catch(e){}}());')

def loop():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){var ' + s + '=(0x0|0x0);for(var ' + t + '=(0x0|0x0);' + t + '<(0x64|0x0);' + t + '++)' + s + '+=' + t + ';if(' + s + '<(0x0|0x0))throw new Error();}());')

def seal():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    u = chars('undefined')
    return ('(function(){try{var ' + s + '=typeof window!==' + u + '?window:globalThis;if(!(' + s + ' instanceof Object))throw new Error();}catch(e){}}());')

def drift():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    mark = val('[native code]')
    return ('(function(){try{var ' + s + '=eval;if(' + s + '.toString().indexOf(' + mark +')===-1)throw new Error();}catch(e){}}());')

def score():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=[];var ' + t + '=Object.keys(' + s + ');if(' + t + '.length!==(0x0|0x0))throw new Error();}catch(e){}}());')

def pixel():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    kind = val('string')
    return ('(function(){try{var ' + s + '=new Error().stack;if(typeof ' + s + '!==' + kind +')throw new Error();}catch(e){}}());')

def flare():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=Date;var ' + t + '=new ' + s + '();if(!(' + t + ' instanceof ' + s + '))throw new Error();}catch(e){}}());')

def pulse():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=Object.create(null);var ' + t + '=Object.getPrototypeOf(' + s + ');if(' + t + '!==null)throw new Error();}catch(e){}}());')

def spark():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=JSON.stringify({a:(0x1|0x0)});if(' + s + '!==\'{"a":1}\')throw new Error();}catch(e){}}());')

def trace():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=function(){};var ' + t + '=' + s + '.length;if(' + t + '!==(0x0|0x0))throw new Error();}catch(e){}}());')

def glow():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=(0x1|0x0)<<(0x3|0x0);if(' + s + '!==(0x8|0x0))throw new Error();}catch(e){}}());')

def frost():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    ob = val('object')
    return ('(function(){try{var ' + s + '=typeof globalThis;var ' + t + '=typeof window;if(' + s + '!==' + ob + '&&' + t + '!==' + ob + ')throw new Error();}catch(e){}}());')

def haze():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=Array.isArray([]);if(!' + s + ')throw new Error();}catch(e){}}());')

def bench():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=Date.now();for(var ' + t + '=(0x0|0x0);' + t + '<(0x3e8|0x0);' + t + '++)(0x1|0x0);if(Date.now()-' + s + '>2000)throw new Error();}catch(e){}}());')

def lock():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    type = val('Function'); name = chars('name')
    return ('(function(){try{var ' + s + '=Object.keys;var ' + t + '=' + s + '.constructor;if(' + t + '[' + name + ']!==' + type +')throw new Error();}catch(e){}}());')

def shield():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    mark = val('[native code]')
    return ('(function(){try{var ' + s + '=Function.prototype.constructor;if(' + s + '.toString().indexOf(' + mark +')===-1)throw new Error();}catch(e){}}());')

def vault():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=new Error();var ' + t + '=Object.getPrototypeOf(' + s + ');if(!(' + t + ' instanceof Object))throw new Error();}catch(e){}}());')

def spike():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    func = chars('log'); mark = val('[native code]')
    return ('(function(){try{var ' + s + '=console[' + func + '].toString();if(' + s + '.indexOf(' + mark +')===-1)throw new Error();}catch(e){}}());')

def glint():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=(~0x0+0x1+0x0)^(~0x0+0x1+0x0);if(' + s + '!==(0x0|0x0))throw new Error();}catch(e){}}());')

def ridge():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    type = chars('function')
    return ('(function(){try{var ' + s + '=typeof Array.isArray;if(' + s + '!==' + type +')throw new Error();}catch(e){}}());')

def veil():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    name = chars('named'); nk = chars('name')
    return ('(function(){try{var ' + s + '=(function named(){}).name;if(' + s + '!==' + name + ')throw new Error();}catch(e){}}());')

def smelt():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    gtm = chars('getTime')
    return ('(function(){try{var ' + s + '=new Date((0x0|0x0));var ' + t + '=' + s + '[' + gtm + ']();if(' + t + '!==(0x0|0x0))throw new Error();}catch(e){}}());')

def crimp():
    s = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    both = chars('both'); ast = chars('a'); bst = chars('b')
    return ('(function(){try{var ' + s + '=' + ast + '+' + bst + ';if(' + s + '!==' + both + ')throw new Error();}catch(e){}}());')

def smog():
    s = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    jar = chars('[1,2,3]'); pfn = chars('parse')
    return ('(function(){try{var ' + s + '=JSON[' + pfn + '](' + jar + ');if(!Array.isArray(' + s + '))throw new Error();}catch(e){}}());')

def blaze():
    s = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    mxf = chars('max')
    return ('(function(){try{var ' + s + '=Math[' + mxf + '];var ' + t + '=' + s + '((0x1|0x0),(0x2|0x0));if(' + t + '!==(0x2|0x0))throw new Error();}catch(e){}}());')

def draft():
    s = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    kind = chars('string'); tof = chars('toString')
    return ('(function(){try{var ' + s + '=(0x1|0x0)[' + tof + ']();if(typeof ' + s + '!==' + kind +')throw new Error();}catch(e){}}());')

def shard():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    type = chars('function'); ax = chars('assign')
    return ('(function(){try{if(typeof Object[' + ax + ']!==' + type +')throw new Error();var ' + s + '=Object[' + ax + ']({},{a:(0x1|0x0)});if(' + s + '.a!==(0x1|0x0))throw new Error();}catch(e){}}());')

def flint():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    push = chars('push'); pop = chars('pop')
    return ('(function(){try{var ' + s + '=[];' + s + '[' + push + ']((0x1|0x0));var ' + t + '=' + s + '[' + pop + ']();if(' + t + '!==(0x1|0x0))throw new Error();}catch(e){}}());')

def loom():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    type = chars('function')
    return ('(function(){try{var ' + s + '=typeof Symbol;if(' + s + '!==' + type +')throw new Error();}catch(e){}}());')

def stealth():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    pat = val('^([^ ]+( +[^ ]+)+)+[^ ]}')
    return ('(function(){try{var ' + s + '=new RegExp(' + pat + ');' + s + '[' + chars('constructor') + '](' + chars('') + ');throw new Error();}catch(e){if(e instanceof TypeError)return;throw new Error();}}());')

def burn():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=(0x2|0x0);var ' + t + '=(0x2|0x0);if((' + s + '*' + t + ')!==(0x4|0x0))throw new Error();}catch(e){}}());')

def bane():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    cxs = chars('cookieEnabled'); nav = chars('navigator')
    bool = val('boolean')
    return ('(function(){try{var ' + s + '=typeof navigator!==' + chars('undefined') + '?navigator:{};if(typeof ' + s + '[' + cxs + ']!==' + bool + ')throw new Error();}catch(e){}}());')

def mire():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=window.self;var ' + t + '=window.top;if(' + s + '!==' + t + ')throw new Error();}catch(e){}}());')

def yoke():
    s = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    nav = chars('navigator'); plt = chars('platform'); wbd = chars('webdriver')
    return ('(function(){try{var ' + s + '=typeof ' + nav + '!==' + chars('undefined') + '?' + nav + '[' + plt + ']:null;}catch(e){}}());')

def tang():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=new Array((0x3|0x0));if(' + s + '.length!==(0x3|0x0))throw new Error();}catch(e){}}());')

def jade():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=Array.prototype;if(' + s + '.constructor!==Array)throw new Error();}catch(e){}}());')

def pith():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    type = chars('function'); name = chars('name')
    return ('(function(){try{var ' + s + '=function pith(){};if(typeof ' + s + '[' + name + ']!==' + type + ')throw new Error();}catch(e){}}());')

def breve():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    call = chars('call'); bind = chars('bind')
    return ('(function(){try{var ' + s + '=Function.prototype[' + call + '];if(typeof ' + s + '!=='+chars('function')+')throw new Error();var ' + t + '=Function.prototype[' + bind + '];if(typeof ' + t + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def grove():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=new Promise(function(r){r((0x1|0x0));});var ' + t + '=typeof ' + s + ';if(' + t + '!=='+chars('object')+')throw new Error();}catch(e){}}());')

def crown():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=(0x7f|0x0);var ' + t + '=(0x80|0x0);if((' + s + '&' + t + ')!==(0x0|0x0))throw new Error();}catch(e){}}());')

def rivet():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=(0xffffffff>>>0x0);if(' + s + '!==(0xffffffff|0x0))throw new Error();}catch(e){}}());')

def quill():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=typeof crypto;if(' + s + '==='+chars('undefined')+')return;if(typeof crypto.getRandomValues!=='+chars('function')+')throw new Error();}catch(e){}}());')

def chisel():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    tos = chars('toString'); nmx = chars('name')
    return ('(function(){try{var ' + s + '=Math.abs;var ' + t + '=' + s + '[' + tos + ']()[' + nmx + '];if(typeof ' + t + '!=='+chars('undefined')+')throw new Error();}catch(e){}}());')

def sling():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=(0x1e240|0x0);if((' + s + '%' + '(' + hex(0x3e8|0x0) + '|0x0))!==(0x0|0x0))throw new Error();}catch(e){}}());')

def stave():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=new DataView(new ArrayBuffer((0x4|0x0)));' + s + '.setInt32((0x0|0x0),(0x12345678|0x0));var ' + t + '=' + s + '.getInt32((0x0|0x0));if(' + t + '!==(0x12345678|0x0))throw new Error();}catch(e){}}());')

def keel():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    itr = chars('iterator'); sym = chars('symbol')
    return ('(function(){try{var ' + s + '=typeof Symbol[' + itr + '];if(' + s + '!==' + sym + ')throw new Error();}catch(e){}}());')

def gale():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    nm = chars('name'); er = chars('Error')
    return ('(function(){try{var ' + s + '=new Error()[' + nm + '];if(' + s + '!==' + er + ')throw new Error();}catch(e){}}());')

def tarn():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    fn = chars('function')
    return ('(function(){try{var ' + s + '=typeof class{};if(' + s + '!==' + fn + ')throw new Error();}catch(e){}}());')

def furl():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    fn = chars('function')
    return ('(function(){try{var ' + s + '=typeof function*(){};if(' + s + '!==' + fn + ')throw new Error();}catch(e){}}());')

def dune():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    frz = chars('freeze'); fzd = chars('isFrozen')
    return ('(function(){try{var ' + s + '=Object[' + frz + ']({});if(!Object[' + fzd + '](' + s + '))throw new Error();}catch(e){}}());')

def rook():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    ndx = chars('indexOf')
    return ('(function(){try{var ' + s + '=[1,2,3][' + ndx + '](2);if(' + s + '!==(0x1|0x0))throw new Error();}catch(e){}}());')

def mast():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    bv = chars('b')
    return ('(function(){try{var ' + s + '="abc"[1];if(' + s + '!==' + bv + ')throw new Error();}catch(e){}}());')

def brim():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    udf = chars('undefined')
    return ('(function(){try{var ' + s + '=Object.create(null).__proto__;if(typeof ' + s + '!==' + udf + ')throw new Error();}catch(e){}}());')

def knap():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    obj = chars('object')
    return ('(function(){try{var ' + s + '=typeof Reflect;if(' + s + '!==' + obj + ')throw new Error();}catch(e){}}());')

def gill():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    bpe = chars('BYTES_PER_ELEMENT')
    return ('(function(){try{var ' + s + '=Uint8Array[' + bpe + '];if(' + s + '!==(0x1|0x0))throw new Error();}catch(e){}}());')

def dais():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    sym = chars('symbol')
    return ('(function(){try{var ' + s + '=typeof Symbol();if(' + s + '!==' + sym + ')throw new Error();}catch(e){}}());')

def celt():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    obj = chars('object')
    return ('(function(){try{var ' + s + '=typeof globalThis;if(' + s + '!==' + obj + ')throw new Error();}catch(e){}}());')

def swag():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    nm = chars('name')
    return ('(function(){try{function _v(){}var ' + s + '=_v[' + nm + '];if(' + s + '!=='+chars('_v')+')throw new Error();}catch(e){}}());')

def pave():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    slc = chars('slice'); bc = chars('bc')
    return ('(function(){try{var ' + s + '="abc"[' + slc + '](1);if(' + s + '!==' + bc + ')throw new Error();}catch(e){}}());')

def lisp():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=parseInt("ff",(0x10|0x0));if(' + s + '!==(0xff|0x0))throw new Error();}catch(e){}}());')

def welt():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    fl = chars('fill')
    return ('(function(){try{var ' + s + '=new Array(3)[' + fl + ']((0x0|0x0));var ' + t + '=' + s + '.length;if(' + t + '!==(0x3|0x0))throw new Error();}catch(e){}}());')

def fizz():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    af = chars('from')
    return ('(function(){try{var ' + s + '=Array[' + af + ']({length:(0x3|0x0)},function(_,i){return i;});var ' + t + '=' + s + '.length;if(' + t + '!==(0x3|0x0))throw new Error();}catch(e){}}());')

def tump():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    ni = chars('isInteger')
    return ('(function(){try{var ' + s + '=Number[' + ni + ']((0x1|0x0));if(!' + s + ')throw new Error();}catch(e){}}());')

def luff():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    en = chars('entries')
    return ('(function(){try{var ' + s + '=Object[' + en + ']({a:(0x1|0x0)});var ' + t + '=' + s + '.length;if(' + t + '!==(0x1|0x0))throw new Error();}catch(e){}}());')

def bulb():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    al = chars('all'); res = chars('resolve')
    return ('(function(){try{var ' + s + '=Promise[' + al + ']([Promise[' + res + ']((0x1|0x0))]);if(typeof ' + s + '!=='+chars('object')+')throw new Error();}catch(e){}}());')

def fawn():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    tst = chars('test')
    return ('(function(){try{var ' + s + '=/^[a-z]+$/[' + tst + ']("abc");if(!' + s + ')throw new Error();}catch(e){}}());')

def nave():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    ft = chars('flat')
    return ('(function(){try{var ' + s + '=typeof [1,[2]][' + ft + '];if(' + s + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def spur():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    ps = chars('padStart')
    return ('(function(){try{var ' + s + '="a"[' + ps + '](3,"0");if(' + s + '!=='+chars('00a')+')throw new Error();}catch(e){}}());')

def limb():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    fe = chars('fromEntries')
    return ('(function(){try{var ' + s + '=Object[' + fe + ']([["a",(0x1|0x0)]]);if(' + s + '.a!==(0x1|0x0))throw new Error();}catch(e){}}());')

def twig():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    fm = chars('flatMap')
    return ('(function(){try{var ' + s + '=[1,2][' + fm + '](function(x){return[x,x];});if(' + s + '.length!==(0x4|0x0))throw new Error();}catch(e){}}());')


def reap(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 6 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            a = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used); f = fresh(used)
            r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
                        tok('id',c), tok('op','='), tok('pun','('), tok('id',a), tok('op','>>'), tok('num','0x0'), tok('pun',')'), tok('op','|'), tok('num',hex(w^w)), tok('pun',','),
                        tok('id',d), tok('op','='), tok('id',c), tok('op','^'), tok('id',a), tok('op','&'), tok('num','0x0'), tok('pun',','),
                        tok('id',e), tok('op','='), tok('pun','('), tok('id',d), tok('op','*'), tok('num','0x1'), tok('op','+'), tok('num',hex(r^r)), tok('pun',')'), tok('pun',','),
                        tok('id',f), tok('op','='), tok('pun','~'), tok('id',e), tok('op','+'), tok('num','0x1'), tok('op','+'), tok('id',e), tok('pun',';')])
        i += 1
    return out

def abuf():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    bf = chars('buffer'); bl = chars('byteLength')
    return ('(function(){try{var ' + s + '=new ArrayBuffer((0x8|0x0));if(' + s + '[' + bl + ']!==(0x8|0x0))throw new Error();}catch(e){}}());')

def volt():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    sc = chars('structuredClone')
    return ('(function(){try{if(typeof ' + sc + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def wire():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    gc = chars('groupCollapsed')
    return ('(function(){try{var ' + s + '=typeof console[' + gc + '];if(' + s + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def mote():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    qm = chars('queueMicrotask')
    return ('(function(){try{if(typeof ' + qm + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def burl():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    ae = chars('at')
    return ('(function(){try{var ' + s + '=[1,2,3][' + ae + '](-1);if(' + s + '!==(0x3|0x0))throw new Error();}catch(e){}}());')

def cult():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    hs = chars('hasOwn')
    return ('(function(){try{var ' + s + '=Object[' + hs + ']({a:1},'+chars('a')+');if(!' + s + ')throw new Error();}catch(e){}}());')

def dolt():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    cs = chars('cause'); udf = chars('undefined')
    return ('(function(){try{var ' + s + '=new Error("t",{"cause":1});if(typeof ' + s + '[' + cs + ']===' + udf + ')throw new Error();}catch(e){}}());')

def fret():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    fs = chars('findLast')
    return ('(function(){try{var ' + s + '=[1,2,3][' + fs + '](function(x){return x<3;});if(' + s + '!==(0x2|0x0))throw new Error();}catch(e){}}());')

def gust():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    fc = chars('findLastIndex')
    return ('(function(){try{var ' + s + '=[1,2,3][' + fc + '](function(x){return x<3;});if(' + s + '!==(0x1|0x0))throw new Error();}catch(e){}}());')

def harp():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    tc = chars('toSorted')
    return ('(function(){try{if(typeof [1,3,2][' + tc + ']!=='+chars('function')+')throw new Error();}catch(e){}}());')

def itch():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    tr = chars('toReversed')
    return ('(function(){try{if(typeof [1,2,3][' + tr + ']!=='+chars('function')+')throw new Error();}catch(e){}}());')

def jest():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    wt = chars('with')
    return ('(function(){try{if(typeof [1,2,3][' + wt + ']!=='+chars('function')+')throw new Error();}catch(e){}}());')

def kink():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    ac = chars('a'); udf = chars('undefined')
    return ('(function(){try{var ' + s + '=Object.fromEntries(Object.entries({"a":1,"b":2}).filter(function(e){return e[0]!==' + ac + '}));if(typeof ' + s + '[' + ac + ']!==' + udf + ')throw new Error();}catch(e){}}());')

def lank():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=Array.prototype.at.call([1,2,3],-1);if(' + s + '!==(0x3|0x0))throw new Error();}catch(e){}}());')

def form():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    sc = chars('string')
    return ('(function(){try{var ' + s + '=typeof(0x0)[' + chars('toString') + '];if(' + s + '!=='+ sc + ')throw new Error();}catch(e){}}());')

def rind():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    ks = chars('keys')
    return ('(function(){try{var ' + s + '=Object[' + ks + ']({a:1,b:2,c:3});var ' + t + '=' + s + '.length;if(' + t + '!==(0x3|0x0))throw new Error();}catch(e){}}());')

def serf():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    vs = chars('values')
    return ('(function(){try{var ' + s + '=Object[' + vs + ']({a:1,b:2});var ' + t + '=' + s + '[0]+' + s + '[1];if(' + t + '!==(0x3|0x0))throw new Error();}catch(e){}}());')

def toll():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    tc = chars('toString')
    return ('(function(){try{var ' + s + '=(0xf)[' + tc + '](0x10);if(' + s + '!=='+chars('f')+')throw new Error();}catch(e){}}());')

def prow():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    mc = chars('map'); jc = chars('join')
    return ('(function(){try{var ' + s + '=[1,2,3][' + mc + '](function(x){return x*x;})[' + jc + '](",");if(' + s + '!=='+chars('1,4,9')+')throw new Error();}catch(e){}}());')

def dart():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    sc = chars('slice'); lc = chars('length')
    return ('(function(){try{var ' + s + '=[1,2,3,4][' + sc + '](1,3);if(' + s + '[' + lc + ']!==(0x2|0x0))throw new Error();}catch(e){}}());')

def wren():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    rc = chars('reduce')
    return ('(function(){try{var ' + s + '=[1,2,3,4,5][' + rc + '](function(a,b){return a+b;},0);if(' + s + '!==(0xf|0x0))throw new Error();}catch(e){}}());')

def geld():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    nc = chars('name'); sc = chars('string')
    return ('(function(){try{var ' + s + '=function named(){};if(typeof ' + s + '[' + nc + ']!=='+ sc + ')throw new Error();}catch(e){}}());')

def raft():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    fc = chars('filter'); lc = chars('length')
    return ('(function(){try{var ' + s + '=[1,2,3,4,5][' + fc + '](function(x){return x%2===0;});if(' + s + '[' + lc + ']!==(0x2|0x0))throw new Error();}catch(e){}}());')

def apex():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    ec = chars('entries'); lc = chars('length')
    return ('(function(){try{var ' + s + '=new Map([[1,2],[3,4]]);var ' + t + '=Array.from(' + s + '[' + ec + ']())[' + lc + '];if(' + t + '!==(0x2|0x0))throw new Error();}catch(e){}}());')

def bask():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    sc = chars('size')
    return ('(function(){try{var ' + s + '=new Set([1,2,3,2,1]);var ' + t + '=' + s + '[' + sc + '];if(' + t + '!==(0x3|0x0))throw new Error();}catch(e){}}());')

def wmap():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    hc = chars('has')
    return ('(function(){try{var ' + s + '=new WeakMap();var ' + t + '={};' + s + '[' + hc + '](' + t + ');if(typeof ' + s + '[' + hc + ']!=='+chars('function')+')throw new Error();}catch(e){}}());')

def dawn():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    nc = chars('now')
    return ('(function(){try{var ' + s + '=typeof Date[' + nc + '];if(' + s + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def dusk():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    ac = chars('assign')
    return ('(function(){try{var ' + s + '=Object[' + ac + ']({},{a:1,b:2});if(' + s + '.a!==(0x1|0x0)||' + s + '.b!==(0x2|0x0))throw new Error();}catch(e){}}());')

def eve():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    ec = chars('every')
    return ('(function(){try{var ' + s + '=[2,4,6][' + ec + '](function(x){return x%2===0;});if(!' + s + ')throw new Error();}catch(e){}}());')

def prot():
    traps = [probe(),snare(),guard(),cage(),leak(),save(),tamper(),block(),dom(),timing(),hooks(),detect(),watch(),frame(),net(),crypt(),loop(),seal(),drift(),score(),pixel(),flare(),pulse(),spark(),trace(),glow(),frost(),haze(),burn(),stealth(),bench(),lock(),shield(),vault(),spike(),glint(),ridge(),veil(),smelt(),crimp(),smog(),blaze(),draft(),shard(),flint(),loom(),bane(),mire(),yoke(),tang(),jade(),pith(),raze(),snag(),damp(),warp(),seep(),blot(),comet(),orbit(),reek(),ember(),sinew(),knell(),sieve(),crux(),gripe(),notch(),troth(),scour(),prong(),girth(),whirl(),wrack(),spall(),breve(),grove(),crown(),rivet(),quill(),chisel(),sling(),stave(),keel(),gale(),tarn(),furl(),dune(),rook(),mast(),brim(),knap(),gill(),dais(),celt(),swag(),pave(),lisp(),welt(),fizz(),tump(),luff(),bulb(),fawn(),nave(),spur(),limb(),twig(),abuf(),volt(),wire(),mote(),burl(),cult(),dolt(),fret(),gust(),harp(),itch(),jest(),kink(),lank(),form(),rind(),serf(),toll(),prow(),dart(),wren(),geld(),raft(),apex(),bask(),wmap(),dawn(),dusk(),eve()]
    random.shuffle(traps); wrapped = ['try{' + t + '}catch(e){}' for t in traps]; delay = hex(random.randint(30, 80))
    return 'setTimeout(function(){' + ''.join(wrapped) + '},' + delay + ');'


def inflate(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 3 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            g = fresh(used); r = fresh(used); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(u)), tok('op','>>>'), tok('num','0x0'), tok('pun',')'), tok('op','|'), tok('num',hex(w^w)), tok('pun',';')])
            out.extend([tok('id','var'), tok('id',r), tok('op','='), tok('pun','~'), tok('pun','('), tok('pun','~'), tok('id',g), tok('pun',')'), tok('op','+'), tok('num','0x0'), tok('pun',';')])
            x = fresh(used); y = fresh(used)
            out.extend([tok('id','var'), tok('id',x), tok('op','='), tok('pun','('), tok('pun','('), tok('num',hex(u^w)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('op','>>>'), tok('num','0x0'), tok('pun',')'), tok('pun',','),
                        tok('id',y), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',x), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',x), tok('pun',';')])
            g2 = fresh(used); r2 = fresh(used); u2 = random.randint(1,0xfe); w2 = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g2), tok('op','='), tok('pun','('), tok('num',hex(u2^w2)), tok('op','^'), tok('num',hex(w2)), tok('op','>>'), tok('num','0x0'), tok('pun',')'), tok('pun',';')])
            out.extend([tok('id','var'), tok('id',r2), tok('op','='), tok('pun','('), tok('num',hex(u2|w2)), tok('op','&'), tok('num',hex(w2^w2)), tok('op','|'), tok('id',g2), tok('pun',')'), tok('pun',';')])
        i += 1
    return out

def hurl(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 3 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            g = fresh(used); r = fresh(used); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(u)), tok('op','&'), tok('num',hex(u)), tok('pun',')'), tok('pun',';')])
            out.extend([tok('id','var'), tok('id',r), tok('op','='), tok('pun','('), tok('id',g), tok('op','^'), tok('num',hex(w^w)), tok('op','|'), tok('num',hex(0)), tok('pun',')'), tok('pun',';')])
            a = fresh(used); c = fresh(used); d = fresh(used)
            out.extend([tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(u<<1>>1)), tok('op','*'), tok('num','0x1'), tok('op','|'), tok('num','0x0'), tok('pun',')'), tok('pun',','),
                        tok('id',c), tok('op','='), tok('pun','('), tok('num',hex(w)), tok('op','>>'), tok('num','0x1'), tok('op','<<'), tok('num','0x1'), tok('pun',')'), tok('pun',','),
                        tok('id',d), tok('op','='), tok('id',a), tok('op','^'), tok('id',c), tok('op','&'), tok('num','0x0'), tok('pun',';')])
        i += 1
    return out



def smear(toks, d, idx, used):
    out = []; i = 0; p = 0; b = 0; vals = list(idx.values())
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v']==';' and p==0 and b>=4 and i+1<len(toks) and toks[i+1]['v'] not in skip and vals:
            x = vals[0]
            out.extend([tok('id','void'), tok('pun','('), tok('id',d), tok('pun','('), tok('num',str(x)), tok('pun',')'), tok('pun',')'), tok('pun',';')])
        i += 1
    return out

def tame(toks):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t['t']=='id' and t['v']=='if' and i+1<len(toks) and toks[i+1]['v']=='(':
            out.append(t); i += 1
            out.append(toks[i]); i += 1
            depth = 1; end = i
            while end < len(toks) and depth > 0:
                if toks[end]['v'] == '(': depth += 1
                if toks[end]['v'] == ')': depth -= 1
                end += 1
            end -= 1
            out.extend(toks[i:end])
            i = end
            k = random.randint(1, 0x7e); r = random.randint(1, 0xfe)
            pred = '&&(' + hex(k^r) + '+0x2*' + hex(k&r) + '-' + hex(r) + '===' + hex(k) + ')'
            out.extend(scan(pred))
            out.append(toks[i]); i += 1; continue
        out.append(t); i += 1
    return out

def lash(toks, d, idx, used):
    out = []; i = 0; vals = list(idx.values())
    while i < len(toks):
        t = toks[i]
        if t['t'] == 'id' and t['v'] == d and i+3 < len(toks) and toks[i+1]['v'] == '(' and toks[i+2]['t'] == 'num' and toks[i+3]['v'] == ')':
            try:
                n = int(toks[i+2]['v'], 0)
                alt = [v for v in vals if v != n]
                if alt:
                    x = alt[0]
                    out.extend([tok('pun','('), tok('id',d), tok('pun','('), tok('num',str(x)), tok('pun',')'),
                                tok('op',','), tok('id',d), tok('pun','('), tok('num',str(n)), tok('pun',')'), tok('pun',')')])
                    i += 4; continue
            except: pass
        out.append(t); i += 1
    return out

def build(pool, keys, a, k):
    if not pool:
        return 'var ' + a + '=[];var ' + k + '=[];'
    size = max(1, (len(pool)+3)//4)
    seg = [pool[j*size:(j+1)*size] for j in range(4)]
    ks = [keys[j*size:(j+1)*size] for j in range(4)]
    xk = [random.randint(1, 0x7e) for _ in range(4)]
    masked = []
    for j, part in enumerate(seg):
        x = xk[j]
        masked.append([''.join('\\x{:02x}'.format(int(s[i+2:i+4], 16)^x) for i in range(0, len(s), 4)) for s in part])
    kv = ['_0x'+hex(random.randint(0xaaaa,0xffff))[2:] for _ in range(4)]
    pv = ['_0x'+hex(random.randint(0xaaaa,0xffff))[2:] for _ in range(4)]
    qv = ['_0x'+hex(random.randint(0xaaaa,0xffff))[2:] for _ in range(4)]
    code = ''
    for j in range(4):
        code += 'var ' + kv[j] + '=' + str(xk[j]) + ';'
        code += ('var ' + pv[j] + '=[' + ','.join('\"'+s+'\"' for s in masked[j]) +
                 '].map(function(s){return s.split(\"\").map(function(c){return String.fromCharCode(c.charCodeAt(0)^' + kv[j] + ');}).join(\"\");});')
        code += 'var ' + qv[j] + '=[' + ','.join(str(v) for v in ks[j]) + '];'
    code += ('var ' + a + '=' + pv[0] + '.concat(' + pv[1] + ',' + pv[2] + ',' + pv[3] + ');' +
             'var ' + k + '=' + qv[0] + '.concat(' + qv[1] + ',' + qv[2] + ',' + qv[3] + ');')
    return code

def weave(n):
    k = random.randint(1, 0xfe); r = random.randint(1, 0xfe)
    s = random.randint(1, 0xfe); q = random.randint(1, 0xfe)
    return [0, n^k, 1, k, 5, 0, 4, 0x7fffffff, 6, 0, 7, 0, 7, 0, 2, s, 3, s, 1, q, 1, q]

def forge(name):
    stk = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    prog = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    idx = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    op = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    val = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('function ' + name + '(' + prog + '){'
            'var ' + stk + '=[];'
            'for(var ' + idx + '=0x0;' + idx + '<' + prog + '.length;' + idx + '+=0x2){'
            'var ' + op + '=' + prog + '[' + idx + '],' + val + '=' + prog + '[' + idx + '+0x1];'
            'if(' + op + '===0x0){' + stk + '.push(' + val + ');}'
            'else if(' + op + '===0x1){' + stk + '.push(' + stk + '.pop()^' + val + ');}'
            'else if(' + op + '===0x2){' + stk + '.push(' + stk + '.pop()+' + val + ');}'
            'else if(' + op + '===0x3){' + stk + '.push(' + stk + '.pop()-' + val + ');}'
            'else if(' + op + '===0x4){' + stk + '.push(' + stk + '.pop()&' + val + ');}'
            'else if(' + op + '===0x5){' + stk + '.push(' + stk + '.pop()|' + val + ');}'
            'else if(' + op + '===0x6){' + stk + '.push(' + stk + '.pop()>>>' + val + ');}'
            'else if(' + op + '===0x7){' + stk + '.push((~' + stk + '.pop()+0x1)&0xffffffff);}'
            '}'
            'return ' + stk + '.pop();}')

def run(toks, d, vmn):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t['t']=='id' and t['v']==d and i+3<len(toks) and toks[i+1]['v']=='(' and toks[i+2]['t']=='num' and toks[i+3]['v']==')':
            try:
                n = int(toks[i+2]['v'], 0)
                prog = weave(n)
                out.extend(scan(d+'(['+','.join(hex(x) for x in prog)+'])'))
                i += 4; continue
            except: pass
        out.append(t); i += 1
    return out

def raze():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    undef = chars('undefined'); perf = chars('performance')
    return ('(function(){try{if(typeof performance===' + undef + ')return;var ' + s + '=performance.now();for(var ' + t + '=0;' + t + '<1e4;' + t + '++);if(performance.now()-' + s + '>3000)throw new Error();}catch(e){}}());')

def snag():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    nln = chars('\n')
    return ('(function(){try{var ' + s + '=new Error().stack||' + chars('') + ';var ' + t + '=' + s + '.split(' + nln + ').length;if(' + t + '>(' + hex(10) + '|0x0))throw new Error();}catch(e){}}());')

def damp():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    wbd = chars('webdriver'); undef = chars('undefined')
    return ('(function(){try{var ' + s + '=typeof navigator!==' + undef + '?navigator:{};if(' + s + '[' + wbd + '])throw new Error();}catch(e){}}());')

def warp():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    tof = chars('toString'); mark = val('[native code]')
    return ('(function(){try{var ' + s + '=Array.prototype[' + tof + '].call([]);if(typeof ' + s + '!=='+val('string')+')throw new Error();}catch(e){}}());')

def seep():
    tfn = chars('function'); tbl = chars('table')
    return ('(function(){try{if(typeof console[' + tbl + ']!==' + tfn + ')throw new Error();}catch(e){}}());')

def blot():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    hpr = chars('hasOwnProperty')
    return ('(function(){try{var ' + s + '=Object.prototype[' + hpr + '];if(typeof ' + s + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def lodge(toks, used):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] == 'switch' and i+1 < len(toks) and toks[i+1]['v'] == '(':
            out.append(t); i += 1
            out.append(toks[i]); i += 1
            depth = 1; end = i
            while end < len(toks) and depth > 0:
                if toks[end]['v'] == '(': depth += 1
                if toks[end]['v'] == ')': depth -= 1
                end += 1
            end -= 1
            out.extend(toks[i:end]); i = end
            r = random.randint(1,0xfe); u = random.randint(1,0xfe)
            out.extend(scan('^' + hex(r^u) + '^' + hex(r^u)))
            out.append(toks[i]); i += 1; continue
        out.append(t); i += 1
    return out


def nest(toks, used):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] == 'case':
            out.append(t); i += 1
            while i < len(toks) and toks[i]['v'] not in ('{', 'break'): out.append(toks[i]); i += 1
            if i >= len(toks) or toks[i]['v'] != '{': continue
            out.append(toks[i]); i += 1
            bind = []; depth = 1
            while i < len(toks) and depth > 0:
                c = toks[i]
                if c['v'] == '{': depth += 1
                if c['v'] == '}': depth -= 1
                if depth > 0: bind.append(c)
                i += 1
            d = 0; c = 0
            for x in bind:
                if x['v'] in ('(','['): d += 1
                if x['v'] in (')',']'): d -= 1
                if x['v'] == ';' and d == 0: c += 1
            r = any(x['t'] == 'id' and x['v'] == 'return' for x in bind)
            m = machine(chop(bind), used) if c >= 3 and not r else None
            if m: out.extend(m)
            else: out.extend(bind)
            out.append(tok('pun','}'))
        else: out.append(t); i += 1
    return out

def route(toks, names, tab):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t['t'] == 'id' and t['v'] in names and i+1 < len(toks) and toks[i+1]['v'] == '(':
            pos = names[t['v']]
            out.extend(scan(tab + '[' + mba(pos) + ']'))
            i += 1; continue
        out.append(t); i += 1
    return out

def decoy(d, a, k):
    v = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    w = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    x = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    y = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    j = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    r = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    q = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    e = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    c = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('var ' + c + '={};'
            'function ' + d + '(' + v + '){'
            'if(' + v + ' in ' + c + ')return ' + c + '[' + v + '];'
            'var ' + w + '=' + a + '[' + v + '],' + x + '=' + k + '[' + v + '],' + y + '=\'\',' + j + '=0;'
            'var ' + r + '=(' + x + '^0x5b)&0x7f,' + q + '=(' + x + '*0x13+0x5)&0x7f;'
            'for(;' + j + '<' + w + '.length;' + j + '++){' +
            r + '=(' + r + '*0x1f+' + q + '+' + j + ')&0x7f;' +
            q + '=(' + q + '^' + r + '^' + j + ')&0x7f;' +
            'var ' + e + '=' + r + '^' + q + ';' +
            y + '+=String.fromCharCode(' + w + '.charCodeAt(' + j + ')^' + e + ');' +
            '}'
            'return(' + c + '[' + v + ']=' + y + ');}')

def comet():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=typeof Proxy;if(' + s + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def orbit():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=typeof Map;if(' + s + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def reek():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    mark = val('[native code]'); tof = chars('toString')
    return ('(function(){try{var ' + s + '=Function.prototype[' + tof + '].call(function(){});if(' + s + '.indexOf(' + mark + ')===-1)throw new Error();}catch(e){}}());')

def ember():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=Object.freeze({});Object.defineProperty(' + s + ','+chars('x')+',{value:(0x1|0x0)});throw new Error();}catch(e){if(e instanceof TypeError)return;throw new Error();}}());')

def sinew():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=(0xffffff|0x0)^(0xffffff|0x0);if(' + s + '!==(0x0|0x0))throw new Error();}catch(e){}}());')

def knell():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=Number.parseInt;var ' + t + '=parseInt;if(' + s + '!==' + t + ')throw new Error();}catch(e){}}());')

def sieve():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    parse = chars('parse'); f = chars('stringify')
    return ('(function(){try{var ' + s + '=JSON[' + parse + '](JSON[' + f + ']({a:(0x1|0x0),b:(0x2|0x0)}));if(' + s + '.a+(0x0|0x0)!==(0x1|0x0))throw new Error();}catch(e){}}());')

def crux():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=typeof WeakMap;var ' + t + '=typeof WeakSet;if(' + s + '!=='+chars('function')+'||' + t + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def gripe():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=Math.PI;if(typeof ' + s + '!=='+chars('number')+')throw new Error();}catch(e){}}());')

def notch():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=new Set([(0x1|0x0),(0x2|0x0),(0x1|0x0)]);if(' + s + '.size!==(0x2|0x0))throw new Error();}catch(e){}}());')

def troth():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    f = chars('sqrt')
    return ('(function(){try{var ' + s + '=Math[' + f + ']((0x4|0x0));if(' + s + '!==(0x2|0x0))throw new Error();}catch(e){}}());')

def scour():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    r = chars('replace'); x = val('\\x20')
    return ('(function(){try{var ' + s + '=' + chars('a b') + '[' + r + '](/ /g,' + chars('_') + ');if(' + s + '!=='+chars('a_b')+')throw new Error();}catch(e){}}());')

def prong():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    f = chars('from')
    return ('(function(){try{var ' + s + '=Array[' + f + ']({length:(0x3|0x0)},function(_,i){return i;});if(' + s + '.length!==(0x3|0x0))throw new Error();}catch(e){}}());')

def girth():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=Object.create({});var ' + t + '=Object.getOwnPropertyNames(' + s + ');if(' + t + '.length!==(0x0|0x0))throw new Error();}catch(e){}}());')

def whirl():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=typeof Object.keys;if(' + s + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def wrack():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    bind = chars('bind'); cl = chars('call')
    return ('(function(){try{var ' + s + '=function(){};var ' + t + '=' + s + '[' + bind + ']({});if(typeof ' + t + '!=='+chars('function')+')throw new Error();}catch(e){}}());')

def spall():
    s = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=new Map();' + s + '.set((0x1|0x0),(0x2|0x0));var ' + t + '=' + s + '.get((0x1|0x0));if(' + t + '!==(0x2|0x0))throw new Error();}catch(e){}}());')

def press(toks, used=None):
    out = []; i = 0; n = len(toks); p = 0; b = 0
    while i < n:
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        if t['t'] == 'id' and t['v'] == 'var' and i+1 < n and toks[i+1]['t'] == 'id' and toks[i+1]['v'].startswith('_0x'):
            if (used is not None and p == 0 and b >= 2 and i+2 < n and toks[i+2]['v'] == '='):
                nm1 = toks[i+1]; j = i+3; dp = 0; xp = 0
                while j < n:
                    v2 = toks[j]['v']
                    if v2 in ('(','['): dp += 1
                    if v2 in (')',']'): dp -= 1
                    if v2 == '{': xp += 1
                    if v2 == '}': xp -= 1
                    if v2 == ';' and dp == 0 and xp == 0: break
                    j += 1
                if j < n:
                    k2 = j+1
                    if (k2 < n and toks[k2]['t'] == 'id' and toks[k2]['v'] == 'var'
                            and k2+2 < n and toks[k2+1]['t'] == 'id' and toks[k2+2]['v'] == '='):
                        nm2 = toks[k2+1]; m = k2+3; dp = 0; xp = 0
                        while m < n:
                            v2 = toks[m]['v']
                            if v2 in ('(','['): dp += 1
                            if v2 in (')',']'): dp -= 1
                            if v2 == '{': xp += 1
                            if v2 == '}': xp -= 1
                            if v2 == ';' and dp == 0 and xp == 0: break
                            m += 1
                        if m < n:
                            val2 = toks[k2+3:m]; val1 = toks[i+3:j]
                            gv = fresh(used); rv = random.randint(1,0xfe); uv = random.randint(1,0xfe)
                            out.extend([tok('id','var'), nm1, tok('op','=')] + val1 + [tok('op',','),
                                         nm2, tok('op','=')] + val2 + [tok('op',','),
                                         tok('id',gv), tok('op','='), tok('pun','('), tok('num',hex(rv^uv)), tok('op','^'), tok('num',hex(uv)), tok('pun',')'), tok('pun',';')])
                            i = m+1; continue
            out.append(t); i += 1
            while i < n:
                while i < n and toks[i]['v'] != ';': out.append(toks[i]); i += 1
                if i < n and toks[i]['v'] == ';':
                    j = i + 1
                    if j < n and toks[j]['t'] == 'id' and toks[j]['v'] == 'var' and j+1 < n and toks[j+1]['t'] == 'id' and toks[j+1]['v'].startswith('_0x'):
                        out.append(tok('pun', ',')); i = j + 1
                    else:
                        out.append(tok('pun', ';')); i += 1; break
        else:
            out.append(t); i += 1
    return out

def strip(code):
    m = re.match(r'(// ==UserScript==.*?// ==/UserScript==\s*)', code, re.DOTALL)
    if m: return m.group(1), code[m.end():]
    return '', code

def chord(toks, d, used):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        out.append(t)
        if t['v'] == '{' and body(toks, i-1) and i > 1 and toks[i-2]['t'] == 'id' and toks[i-2]['v'] == 'function':
            g = fresh(used); r = random.randint(1,0xfe); u = random.randint(1,0xfe)
            w = random.randint(1,0xfe); h = fresh(used)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
                        tok('id',h), tok('op','='), tok('id',g), tok('op','|'), tok('num',hex(w^w)), tok('pun',';')])
        i += 1
    return out

def fork(toks, used):
    out = list(toks); i = 0
    while i < len(out):
        t = out[i]
        if t['t'] == 'id' and t['v'] == 'if' and i+1 < len(out) and out[i+1]['v'] == '(':
            j = i + 2; dep = 1
            while j < len(out) and dep > 0:
                if out[j]['v'] == '(': dep += 1
                if out[j]['v'] == ')': dep -= 1
                j += 1
            if j < len(out) and out[j]['v'] == '{':
                k = j + 1; dep = 1
                while k < len(out) and dep > 0:
                    if out[k]['v'] == '{': dep += 1
                    if out[k]['v'] == '}': dep -= 1
                    k += 1
                if k >= len(out) or out[k]['v'] != 'else':
                    g = fresh(used); r = random.randint(1,0xfe); u = random.randint(1,0xfe)
                    ins = [tok('id','else'), tok('pun','{'),
                           tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',';'),
                           tok('pun','}')]
                    out = out[:k] + ins + out[k:]
                    i = k + len(ins); continue
        i += 1
    return out

def shadow(toks, d, idx, used):
    if not idx: return toks
    fake = {}
    for nm in idx.keys():
        fake[nm] = fresh(used)
    out = []
    decls = [tok('id','var')]
    items = list(fake.items())
    for j, (nm, fi) in enumerate(items):
        r = random.randint(1, 0xfe); u = random.randint(1, 0xfe)
        decls.extend([tok('id',fi), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')')])
        decls.append(tok('pun', ',' if j < len(items)-1 else ';'))
    out.extend(decls)
    rev = {v: k for k, v in idx.items()}
    i = 0
    while i < len(toks):
        t = toks[i]
        if t['t'] == 'id' and t['v'] == d and i+3 < len(toks) and toks[i+1]['v'] == '(' and toks[i+2]['t'] == 'num' and toks[i+3]['v'] == ')':
            try:
                n = int(toks[i+2]['v'], 0)
                nm = rev.get(n)
                if nm and nm in fake:
                    fi = fake[nm]
                    out.extend([tok('pun','('), tok('id',fi), tok('op',','), tok('id',d), tok('pun','('), tok('num',str(n)), tok('pun',')'), tok('pun',')')])
                    i += 4; continue
            except: pass
        out.append(t); i += 1
    return out


def wrap(toks, used):
    out = []; i = 0; dep = 0; par = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): par += 1
        if t['v'] in (')',']'): par -= 1
        if t['v'] == '{': dep += 1
        if t['v'] == '}': dep -= 1
        if (t['t'] == 'id' and t['v'] == 'function' and dep == 0 and par == 0
                and i+1 < len(toks) and toks[i+1]['t'] == 'id'
                and i+2 < len(toks) and toks[i+2]['v'] == '('):
            nm = toks[i+1]['v']
            j = i+3; pd = 1
            while j < len(toks) and pd > 0:
                if toks[j]['v'] == '(': pd += 1
                if toks[j]['v'] == ')': pd -= 1
                j += 1
            if j >= len(toks) or toks[j]['v'] != '{': out.append(t); i += 1; continue
            k = j+1; bd = 1; be = j+1
            while be < len(toks) and bd > 0:
                if toks[be]['v'] == '{': bd += 1
                if toks[be]['v'] == '}': bd -= 1
                be += 1
            out.extend(toks[i:be])
            i = be
            pn = fresh(used); h = fresh(used); ap = fresh(used); ctx = fresh(used)
            out.extend([tok('id','var'), tok('id',pn), tok('op','='),
                         tok('id','new'), tok('id','Proxy'), tok('pun','('), tok('id',nm), tok('pun',','), tok('pun','{'),
                         tok('id','apply'), tok('pun',':'), tok('id','function'), tok('pun','('), tok('id',h), tok('pun',','), tok('id',ctx), tok('pun',','), tok('id',ap), tok('pun',')'), tok('pun','{'),
                         tok('id','return'), tok('id',h), tok('pun','.'), tok('id','apply'), tok('pun','('), tok('id',ctx), tok('pun',','), tok('id',ap), tok('pun',')'), tok('pun',';'),
                         tok('pun','}'), tok('pun','}'), tok('pun',')'), tok('pun',';')])
            continue
        out.append(t); i += 1
    return out

def glue(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        if (t['t'] == 'id' and t['v'] == 'return' and p == 0 and b >= 2
                and i+1 < len(toks) and toks[i+1]['t'] in ('num',) ):
            j = i+1; dp = 0; db = 0
            while j < len(toks):
                v = toks[j]['v']
                if v in ('(','['): dp += 1
                if v in (')',']'): dp -= 1
                if v == '{': db += 1
                if v == '}': db -= 1
                if v == ';' and dp == 0 and db == 0: break
                j += 1
            expr = toks[i+1:j]
            if expr and j < len(toks):
                g = fresh(used); h = fresh(used); r = random.randint(1,0xfe); u = random.randint(1,0xfe)
                out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
                             tok('id',h), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',g), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',g), tok('pun',';')])
                out.extend([tok('id','return'), tok('pun','('), tok('id',h), tok('op',','), tok('pun','(')])
                out.extend(expr)
                out.extend([tok('pun',')'), tok('pun',')'), tok('pun',';')])
                i = j+1; continue
        out.append(t); i += 1
    return out

def drip(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if (t['v'] == '{' and p == 0 and b >= 3 and i >= 2
                and toks[i-1]['v'] == ')' and i >= 4):
            j = i - 2; depth = 1
            while j >= 0 and depth > 0:
                if toks[j]['v'] == ')': depth += 1
                if toks[j]['v'] == '(': depth -= 1
                j -= 1
            kw = toks[j]['v'] if j >= 0 else ''
            if kw in ('for', 'while', 'do'):
                a = fresh(used); c = fresh(used); d = fresh(used)
                r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
                out.extend([tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
                             tok('id',c), tok('op','='), tok('pun','('), tok('id',a), tok('op','&'), tok('num','0x0'), tok('pun',')'), tok('op','|'), tok('id',a), tok('pun',','),
                             tok('id',d), tok('op','='), tok('pun','~'), tok('id',c), tok('op','+'), tok('num','0x1'), tok('op','+'), tok('id',c), tok('pun',';')])
        i += 1
    return out

def twin(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if (t['t'] == 'id' and t['v'] == 'var' and p == 0 and b >= 3
                and i+4 < len(toks) and toks[i+1]['t'] == 'id'
                and toks[i+2]['v'] == '=' and toks[i+3]['t'] == 'num'
                and toks[i+4]['v'] == ';'):
            nm = toks[i+1]['v']; val = toks[i+3]['v']
            a = fresh(used); r = random.randint(1,0xfe)
            out.extend([tok('id',a), tok('op','='), tok('pun','('), tok('id',nm), tok('op','^'), tok('num',hex(r^r)), tok('pun',')'), tok('op','^'), tok('num',hex(r^r)), tok('pun',',')])
        i += 1
    return out

def sift(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if (t['t'] == 'id' and t['v'] == 'default' and p == 0 and b >= 3
                and i+1 < len(toks) and toks[i+1]['v'] == ':'):
            a = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used)
            r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
            out.extend([tok('pun',':'), tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
                        tok('id',c), tok('op','='), tok('pun','('), tok('id',a), tok('op','>>'), tok('num','0x0'), tok('pun',')'), tok('op','|'), tok('num','0x0'), tok('pun',','),
                        tok('id',d), tok('op','='), tok('id',c), tok('op','^'), tok('id',a), tok('op','&'), tok('num','0x0'), tok('pun',','),
                        tok('id',e), tok('op','='), tok('pun','~'), tok('id',d), tok('op','+'), tok('num','0x1'), tok('op','+'), tok('id',d), tok('pun',';')])
            i += 2; continue
        i += 1
    return out

def limn(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if (t['t'] == 'id' and t['v'] == 'return' and p == 0 and b >= 4
                and i+1 < len(toks) and toks[i+1]['t'] == 'id'
                and i > 0 and toks[i-1]['v'] in (';','{')):
            a = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used)
            r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
            out.extend([tok('id','void'), tok('pun','('), tok('id','function'), tok('pun','('), tok('pun',')'), tok('pun','{'),
                        tok('id','var'), tok('id',a), tok('op','='), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',','),
                        tok('id',c), tok('op','='), tok('pun','('), tok('id',a), tok('op','&'), tok('num','0x0'), tok('pun',')'), tok('op','^'), tok('id',a), tok('pun',','),
                        tok('id',d), tok('op','='), tok('pun','~'), tok('id',c), tok('op','+'), tok('num','0x1'), tok('op','+'), tok('id',c), tok('pun',','),
                        tok('id',e), tok('op','='), tok('id',d), tok('op','*'), tok('num','0x1'), tok('op','&'), tok('num','0x0'), tok('pun',';'),
                        tok('id','return'), tok('id',e), tok('op','&'), tok('num','0x0'), tok('pun',';'),
                        tok('pun','}'), tok('pun','('), tok('pun',')'), tok('pun',')'), tok('pun',';')])
        i += 1
    return out

def groove(toks, used):
    out = []; i = 0; dep = 0; g = False; outer = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] == '{': outer += 1
        if t['v'] == '}': outer -= 1
        if t['t'] == 'id' and t['v'] == 'function' and body(toks, i) and outer == 0: g = True
        if t['v'] == '{' and g:
            dep += 1
            if dep == 1:
                out.append(t); i += 1
                f1 = fresh(used); f2 = fresh(used)
                p = fresh(used); q = fresh(used); x = fresh(used)
                r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
                out.extend([tok('id','var'),
                    tok('id',f2), tok('op','='), tok('id','function'), tok('pun','('), tok('id',p), tok('pun',')'), tok('pun','{'),
                    tok('id','return'), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('id',p), tok('pun',')'), tok('op','&'), tok('num','0x0'), tok('pun',';'),
                    tok('pun','}'), tok('pun',','),
                    tok('id',f1), tok('op','='), tok('id','function'), tok('pun','('), tok('id',q), tok('pun',','), tok('id',x), tok('pun',')'), tok('pun','{'),
                    tok('id','return'), tok('id',f2), tok('pun','('), tok('id',q), tok('pun',')'), tok('op','^'), tok('id',f2), tok('pun','('), tok('id',x), tok('pun',')'), tok('op','&'), tok('num','0x0'), tok('pun',';'),
                    tok('pun','}'), tok('pun',';'),
                    tok('id','void'), tok('pun','('), tok('id',f1), tok('pun','('), tok('num',hex(r)), tok('pun',','), tok('num',hex(u^w)), tok('pun',')'), tok('pun',')'), tok('pun',';')])
                a = fresh(used); b2 = fresh(used); c2 = fresh(used); d2 = fresh(used)
                r2 = random.randint(1,0xfe); u2 = random.randint(1,0xfe); w2 = random.randint(1,0xfe)
                out.extend([tok('id','void'), tok('pun','('), tok('id','function'), tok('pun','('), tok('id',a), tok('pun',','), tok('id',b2), tok('pun',','), tok('id',c2), tok('pun',')'), tok('pun','{'),
                    tok('id','var'), tok('id',d2), tok('op','='), tok('id',a), tok('op','^'), tok('id',b2), tok('op','|'), tok('num','0x0'), tok('pun',';'),
                    tok('id','return'), tok('id','function'), tok('pun','('), tok('pun',')'), tok('pun','{'),
                    tok('id','return'), tok('id',d2), tok('op','&'), tok('id',c2), tok('op','&'), tok('num','0x0'), tok('pun',';'),
                    tok('pun','}'), tok('pun',';'),
                    tok('pun','}'), tok('pun','('), tok('num',hex(r2^u2)), tok('pun',','), tok('num',hex(u2^w2)), tok('pun',','), tok('num',hex(w2^r2)), tok('pun',')'), tok('pun',')'), tok('pun','('), tok('pun',')'), tok('pun',';')])
                g = False; continue
        if t['v'] == '}' and dep > 0:
            dep -= 1
            if dep == 0: g = False
        out.append(t); i += 1
    return out

def knit(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 4 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            lb = fresh(used); a = fresh(used); c = fresh(used); d = fresh(used); e = fresh(used)
            r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
            out.extend([tok('id',lb), tok('pun',':'), tok('pun','{'),
                tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',';'),
                tok('id','if'), tok('pun','('), tok('pun','('), tok('id',a), tok('op','|'), tok('num','0x0'), tok('pun',')'), tok('op','!=='), tok('id',a), tok('pun',')'), tok('id','break'), tok('id',lb), tok('pun',';'),
                tok('id','var'), tok('id',c), tok('op','='), tok('id',a), tok('op','&'), tok('num','0x0'), tok('pun',','),
                tok('id',d), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',c), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',c), tok('pun',','),
                tok('id',e), tok('op','='), tok('id',d), tok('op','^'), tok('num',hex(w^w)), tok('op','|'), tok('num','0x0'), tok('pun',';'),
                tok('pun','}'),])
            lb2 = fresh(used); a2 = fresh(used); c2 = fresh(used); d2 = fresh(used)
            r2 = random.randint(1,0xfe); u2 = random.randint(1,0xfe); w2 = random.randint(1,0xfe)
            out.extend([tok('id',lb2), tok('pun',':'), tok('id','do'), tok('pun','{'),
                tok('id','var'), tok('id',a2), tok('op','='), tok('pun','('), tok('num',hex(r2^u2)), tok('op','^'), tok('num',hex(u2)), tok('pun',')'), tok('pun',','),
                tok('id',c2), tok('op','='), tok('pun','('), tok('id',a2), tok('op','&'), tok('num','0x0'), tok('pun',')'), tok('op','|'), tok('id',a2), tok('pun',','),
                tok('id',d2), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',c2), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',c2), tok('pun',';'),
                tok('id','if'), tok('pun','('), tok('id',d2), tok('op','!=='), tok('num',hex(w2^w2)), tok('pun',')'), tok('id','break'), tok('id',lb2), tok('pun',';'),
                tok('pun','}'), tok('id','while'), tok('pun','('), tok('num','0x0'), tok('pun',')'), tok('pun',';')])
        i += 1
    return out


def brew(toks, used):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        out.append(t)
        if t['v'] == ':' and i >= 2 and toks[i-2]['v'] == 'case' and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            g = fresh(used); r = random.randint(1,0xfe); u = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',';')])
        i += 1
    return out

def obf(src):
    header, body = strip(src)
    toks = scan(body)
    if toks:
        toks = tpl(toks)
        used = set()
        toks = name(toks, used)
        toks = nums(toks)
        toks = bools(toks)
        toks, pool, keys, d, a, k, idx = cipher(toks)
        snap = dict(idx)
        toks = props(toks, d, snap)
        toks = chain(toks, d, snap)
        toks = smear(toks, d, snap, used)
        toks = tame(toks)
        toks, v, l, e, b, m, y = cipher(toks)
        size = dict(y)
        toks = chain(toks, e, size)
        toks = lash(toks, e, size, set())
        used |= {t['v'] for t in toks if t['t'] == 'id' and t['v'].startswith('_0x')}
        if used:
            toks = chalk(toks, d, snap, used)
            toks = shadow(toks, d, snap, used)
            toks = flat(toks, used)
            toks = inject(toks, used)
            toks = chord(toks, d, used)
            toks = alias(toks, used)
            toks = fork(toks, used)
            toks = glue(toks, used)
            toks = extra(toks, used)
            toks = morph(toks, used)
            toks = cloak(toks, used)
            toks = lodge(toks, used)
            if len(toks):
                toks = fill(toks, used)
                toks = inflate(toks, used)
                toks = hurl(toks, used)
                toks = cloud(toks, used)
                toks = brew(toks, used)
                toks = knit(toks, used)
                toks = reap(toks, used)
                toks = press(toks, used)
                toks = comma(toks, used)
        grain(pool, keys, idx)
        z = pairs(pool, keys, idx, snap)
        if z:
            toks = link(toks, d, z)
        pool, keys = rot(pool, keys)
        pool, keys, w = shuffle(pool, keys)
        toks = map(toks, w, d)
        v, l, w = shuffle(v, l)
        toks = map(toks, w, e)
        if pool:
            toks = nest(toks, used)
            toks = wrap(toks, used)
            toks = groove(toks, used)
        pool, keys, c = spin(pool, keys, a, k)
        v, l, f = twist(v, l, b, m)
        def pick(): x = '_0x'+hex(random.randint(0xaaaa,0xffff))[2:]; used.add(x); return x
        g,h,i,n,o,p,s,t,shell = pick(),pick(),pick(),pick(),pick(),pick(),pick(),pick(),pick()
        proxy = ('var ' + g + '=(function(' + i + ',' + s + '){return function(' + o + '){return ' + i + '(' + o + '^' + s + '^' + s + ');};}(' + d + ',' + mba(random.randint(1,0xfe)) + '));'
                 'var ' + h + '=(function(' + n + ',' + t + '){return function(' + p + '){return ' + n + '(' + p + '^' + t + '^' + t + ');};}(' + e + ',' + mba(random.randint(1,0xfe)) + '));'
                 'var ' + shell + '=(function(' + i + ',' + s + '){return function(' + o + '){return ' + i + '(' + o + ');};}(' + g + ',' + mba(random.randint(1,0xfe)) + '));')
        toks = swap(toks, d, g)
        toks = swap(toks, e, h)
        tab = fresh(used)
        x = 'var ' + tab + '=[' + g + ',' + h + ',' + shell + '];'
        toks = route(toks, {g: 0, h: 1, shell: 2}, tab)
        vm = fresh(used)
        toks = run(toks, tab, vm)
        toks = lit(toks)
        toks = noop(used) + toks
        toks = press(toks)
        toks = encode(toks)
        code = emit(toks)
        r = build(pool, keys, a, k)
        q = arrays(v, l, b, m)
        j = rolling(d, a, k)
        u = dec(e, b, m)
        work = forge(vm)
        seed = fresh(used); arr = fresh(used); fn = fresh(used)
        lure = ['\\x68\\x65\\x6c\\x6c\\x6f', '\\x77\\x6f\\x72\\x6c\\x64', '\\x74\\x65\\x73\\x74']
        part = 'var ' + arr + '=[' + ','.join('"'+s+'"' for s in lure) + '];var ' + seed + '=[' + ','.join(str(random.randint(1,62)) for _ in range(3)) + '];'
        call = decoy(fn, arr, seed)
        anchor = 'if(false){GM_xmlhttpRequest({});' + fn + '(0x0);}'
        text = emit(math(scan(prot())))
        return header + anchor + part + call + work + r + q + j + u + c + f + proxy + x + text + code
    return src


def tangle(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 2 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            g = fresh(used); h = fresh(used); r = fresh(used)
            u = random.randint(1,0xfe); w = random.randint(1,0xfe); x = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(u^w)), tok('op','^'), tok('num',hex(w)), tok('pun',')'), tok('pun',','),
                         tok('id',h), tok('op','='), tok('pun','('), tok('id',g), tok('op','|'), tok('num',hex(x^x)), tok('op','^'), tok('id',g), tok('pun',')'), tok('pun',','),
                         tok('id',r), tok('op','='), tok('pun','~'), tok('pun','('), tok('pun','~'), tok('id',h), tok('op','+'), tok('num','0x0'), tok('pun',')'), tok('pun',';')])
        i += 1
    return out

def math(toks):
    out = []
    for t in toks:
        if t['t'] == 'num':
            try:
                v = t['v']
                if v.endswith('n') or '.' in v or 'e' in v.lower(): out.append(t); continue
                n = int(v, 0)
                if 2 <= n <= 0xffff:
                    a = random.randint(1, 0xff); b = random.randint(1, 0xff)
                    expr = '(((' + hex(n^a) + '^' + hex(a) + ')^' + hex(b) + ')^' + hex(b) + ')'
                    out.extend(scan(expr)); continue
            except: pass
            out.append(t)
        else: out.append(t)
    return out

def trap(used):
    s = fresh(used); t = fresh(used); r = fresh(used)
    u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',s), tok('op','='), tok('pun','('), tok('num',hex(u^w)), tok('op','^'), tok('num',hex(w)), tok('pun',')'), tok('pun',';'),
            tok('id','var'), tok('id',t), tok('op','='), tok('pun','('), tok('id',s), tok('op','>>'), tok('num','0x0'), tok('op','|'), tok('num','0x0'), tok('pun',')'), tok('pun',';'),
            tok('id','var'), tok('id',r), tok('op','='), tok('pun','('), tok('pun','~'), tok('id',t), tok('op','+'), tok('num','0x1'), tok('pun',')'), tok('op','+'), tok('id',s), tok('pun',';')]

def cloud(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 4 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            out.extend(trap(used))
        i += 1
    return out

def spin(pool, keys, a, q):
    n = len(pool)
    if n < 2: return pool, keys, ''
    r = random.randint(1, max(1, n - 1))
    p = [pool[(j + r) % n] for j in range(n)]
    k = [keys[(j + r) % n] for j in range(n)]
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    half = r // 2
    code = ('(function(){var ' + s + '=' + mba(half) + ';var ' + t + '=' + mba(r - half) + ';'
            'while(' + s + '-->0x0){' + a + '.unshift(' + a + '.pop());' + q + '.unshift(' + q + '.pop());}' +
            'while(' + t + '-->0x0){' + a + '.unshift(' + a + '.pop());' + q + '.unshift(' + q + '.pop());}' +
            '}());')
    return p, k, code

def vex(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 3 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            g = fresh(used); r = fresh(used); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(u^w)), tok('op','^'), tok('num',hex(w)), tok('op','>>'), tok('num','0x0'), tok('pun',')'), tok('pun',';')])
            out.extend([tok('id','var'), tok('id',r), tok('op','='), tok('pun','('), tok('num',hex(u|w)), tok('op','&'), tok('num',hex(w^w)), tok('op','|'), tok('id',g), tok('pun',')'), tok('pun',';')])
        i += 1
    return out

def read(path):
    with open(path, 'r', encoding='utf-8') as f: return f.read()

def write(path, data):
    with open(path, 'w', encoding='utf-8') as f: f.write(data)

def main():
    if len(sys.argv) < 2:
        print('Usage: python obf.py file.js'); sys.exit(1)
    src = sys.argv[1]
    base = os.path.splitext(os.path.basename(src))[0]
    out = os.path.join(os.path.dirname(os.path.abspath(src)), base + '_obf.js')
    write(out, obf(read(src)))
    print('done ->', out)

if __name__ == '__main__': main()
