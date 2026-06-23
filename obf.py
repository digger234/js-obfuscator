import re, random, sys, os

def tok(t, v): return {'t': t, 'v': v}
def alpha(c): return c.isalpha() or c in '_$' or ord(c) > 127

kwds = {'var','let','const','function','return','if','else','for','while','do','switch','case','break','continue','default','try','catch','finally','throw','new','this','typeof','instanceof','delete','void','in','of','class','extends','import','export','debugger','true','false','null','undefined','async','await','yield','with','super','static','get','set','from','as','target','arguments','eval'}
safe = {'document','window','globalThis','console','Math','JSON','Date','Object','Array','String','Number','Boolean','Function','Promise','Error','Symbol','TypeError','ReferenceError','SyntaxError','RangeError','EvalError','setTimeout','setInterval','clearTimeout','clearInterval','requestAnimationFrame','cancelAnimationFrame','queueMicrotask','location','navigator','localStorage','sessionStorage','history','screen','XMLHttpRequest','fetch','URL','FormData','Blob','FileReader','Headers','Request','Response','WebSocket','Worker','Event','CustomEvent','MouseEvent','KeyboardEvent','HTMLElement','Element','Node','NodeList','MutationObserver','IntersectionObserver','ResizeObserver','Map','Set','WeakMap','WeakSet','Proxy','Reflect','Uint8Array','Int8Array','Uint16Array','Int16Array','Uint32Array','Int32Array','Float32Array','Float64Array','DataView','ArrayBuffer','TextDecoder','TextEncoder','encodeURIComponent','decodeURIComponent','encodeURI','decodeURI','escape','unescape','parseInt','parseFloat','isNaN','isFinite','atob','btoa','alert','confirm','prompt','performance','crypto','Notification','Audio','Image','RegExp','WeakRef','BigInt','Infinity','NaN','GM_xmlhttpRequest','GM_setValue','GM_getValue','GM_deleteValue','GM_listValues','GM_addStyle','GM_getResourceText','GM_info','GM_notification','GM_setClipboard','GM_openInTab','GM_registerMenuCommand','unsafeWindow','GM','GM_cookie'}
chset = {'x': '0123456789abcdefABCDEF', 'b': '01', 'o': '01234567'}
bmap = {'true': '(!![])','false': '(![])','null': '(void 0x0,null)','undefined': '(void 0x0)'}
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
                z = chset.get(r, '01234567')
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
        v = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
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

def templit(toks):
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

def rename(toks):
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
    mapping = {}; used = set()
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

def xenc(s, k):
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
        enc = xenc(val, n)
        idx[val] = len(pool)
        pool.append(''.join('\\x{:02x}'.format(ord(c)) for c in enc))
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

def dehex(s):
    return ''.join(chr(int(s[j+2:j+4], 16)) for j in range(0, len(s), 4))

def reroll(pool, keys):
    rp = []; rk = []
    for s, k in zip(pool, keys):
        mid = dehex(s); orig = xenc(mid, k)
        nk = random.randint(1, 62); enc = roll(orig, nk)
        rp.append(''.join('\\x{:02x}'.format(ord(c)) for c in enc)); rk.append(nk)
    return rp, rk

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

def decode(d, a, k):
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
                out.extend([tok('pun','['), tok('str','"' + p + '"'), tok('pun',']')])
            i += 2; continue
        out.append(t); i += 1
    return out

def mba(n):
    m = random.randint(1,0xff); a = random.randint(0,max(0,n)); b = n-a
    k = random.randint(1,0xff); j = random.randint(1,0xff)
    p = random.randint(1,0xff); q = random.randint(1,0xff)
    core = '((' + hex(a^m) + '^' + hex(m) + ')+' + hex(b) + ')'
    lv2 = '((' + core + '^' + hex(k) + ')^' + hex(k) + ')'
    lv3 = '((' + lv2 + '^' + hex(j) + ')^' + hex(j) + ')'
    lv4 = '((' + lv3 + '^' + hex(p) + ')^' + hex(p) + ')'
    return '((' + lv4 + '^' + hex(q) + ')^' + hex(q) + ')'

def nums(toks):
    out = []
    for t in toks:
        if t['t'] != 'num': out.append(t); continue
        try:
            v = t['v']
            if v.endswith('n') or '.' in v or 'e' in v.lower(): out.append(t); continue
            n = int(v, 0)
            out.extend(scan(bury(n) if n > 255 else mba(n))); continue
        except: pass
        out.append(t)
    return out

def bools(toks):
    out = []
    for t in toks:
        if t['t'] == 'id' and t['v'] in bmap: out.extend(scan(bmap[t['v']]))
        else: out.append(t)
    return out

def chop(toks):
    stmts = []; cur = []; d = 0; i = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('{','(','['):
            d += 1; cur.append(t)
        else:
            if t['v'] in ('}',')',']'):
                if d > 0:
                    d -= 1; cur.append(t)
                else:
                    if cur: stmts.append(cur[:]); cur = []
                    stmts.append([t]); i += 1; continue
            else:
                if t['v'] == ';' and d == 0:
                    if cur: stmts.append(cur[:]); cur = []
                else:
                    cur.append(t)
        i += 1
    if cur: stmts.append(cur)
    return [s for s in stmts if s and not (len(s)==1 and s[0]['v']=='}')]

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
    result.extend([tok('id','while'), tok('pun','('), tok('pun','('), tok('id',s), tok('op','^'), tok('id',t), tok('pun',')'), tok('op','!=='), tok('num',str(end)), tok('pun',')'), tok('pun','{')])
    result.extend([tok('id','switch'), tok('pun','('), tok('id',s), tok('op','^'), tok('id',t), tok('pun',')'), tok('pun','{')])
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
            hasret = any(x['t']=='id' and x['v']=='return' and x['v'] for x in body)
            m = machine(chop(body), used) if not hasret else None
            if m: out.extend(m)
            else: out.extend(body)
            if i < len(toks): out.append(toks[i]); i += 1
        else: out.append(t); i += 1
    return out

def dead(used):
    a = fresh(used); b = fresh(used); c = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',a), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
            tok('id',b), tok('op','='), tok('pun','!'), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
            tok('id',c), tok('op','='), tok('pun','('), tok('num',hex(w)), tok('op','>>'), tok('num','0x0'), tok('op','|'), tok('num',hex(r^r)), tok('pun',')'), tok('pun',';')]

def ghost(used):
    a = random.randint(1,0xfe); b = random.randint(1,0xfe); g = fresh(used); h = fresh(used)
    cond = hex(a^b) + '^' + hex(b) + '===' + hex(a)
    result = [tok('id','if'), tok('pun','(')]
    result.extend(scan(cond))
    result.extend([tok('pun',')'), tok('pun','{'),
        tok('id','var'), tok('id',g), tok('op','='), tok('num',hex(a^b)), tok('op','|'), tok('num',hex(b)), tok('pun',','),
        tok('id',h), tok('op','='), tok('pun','~'), tok('pun','('), tok('pun','~'), tok('id',g), tok('op','+'), tok('num','0x0'), tok('pun',')'), tok('pun',';'),
        tok('pun','}')])
    return result

def hush(used):
    g = fresh(used); r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','void'), tok('pun','('), tok('pun','('), tok('id','function'), tok('pun','('), tok('pun',')'), tok('pun','{'),
            tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(r)), tok('op','+'), tok('num',hex(u)), tok('op','-'), tok('num',hex(r)), tok('pun',')'), tok('op','|'), tok('num',hex(w^w)), tok('pun',';'),
            tok('pun','}'), tok('pun','('), tok('pun',')'), tok('pun',')'), tok('pun',')'), tok('pun',';')]

def flux(used):
    f = fresh(used); g = fresh(used); h = fresh(used)
    u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',f), tok('op','='), tok('pun','['), tok('num',hex(u^w)), tok('op',','), tok('num',hex(u|w)), tok('pun',']'), tok('pun',','),
            tok('id',g), tok('op','='), tok('id',f), tok('pun','['), tok('num','0x0'), tok('pun',']'), tok('op','^'), tok('id',f), tok('pun','['), tok('num','0x1'), tok('pun',']'), tok('pun',','),
            tok('id',h), tok('op','='), tok('pun','('), tok('pun','~'), tok('pun','('), tok('id',g), tok('op','|'), tok('num',hex(u)), tok('pun',')'), tok('pun',')'), tok('op','+'), tok('num','0x1'), tok('pun',';')]

def echo(used):
    f = fresh(used); g = fresh(used); x = fresh(used)
    r = random.randint(1,0xfe); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',f), tok('op','='), tok('id','function'), tok('pun','('), tok('id',g), tok('pun',')'), tok('pun','{'),
            tok('id','return'), tok('pun','('), tok('id',g), tok('op','^'), tok('num',hex(r)), tok('op','^'), tok('num',hex(r)), tok('op','|'), tok('num','0x0'), tok('pun',')'), tok('pun',';'),
            tok('pun','}'), tok('pun',','),
            tok('id',x), tok('op','='), tok('pun','('), tok('num',hex(r^u)), tok('op','^'), tok('num',hex(u)), tok('op','*'), tok('num','0x1'), tok('op','&'), tok('num',hex(w^w^w^w)), tok('pun',')'), tok('pun',';')]

def knot(used):
    f = fresh(used); g = fresh(used); r = fresh(used)
    u = random.randint(1,0xfe); w = random.randint(1,0xfe); x = random.randint(1,0xfe)
    return [tok('id','var'), tok('id',f), tok('op','='), tok('id','function'), tok('pun','('), tok('id',g), tok('pun',')'), tok('pun','{'),
            tok('id','var'), tok('id',r), tok('op','='), tok('id',g), tok('op','|'), tok('num','0x0'), tok('op','-'), tok('num','0x0'), tok('pun',';'),
            tok('id','return'), tok('id',r), tok('op','&'), tok('num',hex(u^u)), tok('op','^'), tok('id',r), tok('pun',';'),
            tok('pun','}'), tok('pun',';'),
            tok('id','void'), tok('pun','('), tok('id',f), tok('pun','('), tok('num',hex(x^w)), tok('op','^'), tok('num',hex(w)), tok('pun',')'), tok('pun',')'), tok('pun',';')]

bank = [dead, ghost, hush, flux, echo, knot]

def fill(toks, used):
    out = []; i = 0; p = 0; b = 0; c = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 1 and i+1 < len(toks) and toks[i+1]['v'] not in skip and c % 3 == 0:
            out.extend(bank[c // 3 % len(bank)](used))
        if t['v'] == ';': c += 1
        i += 1
    return out

def inject(toks, used):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        out.append(t)
        if t['v'] == '{' and i > 0:
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
                out.extend(bank[0](used)); out.extend(bank[1](used))
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
                xa = fresh(used); xb = fresh(used)
                out.extend([tok('id','var'), tok('id',x), tok('op','='), tok('id','globalThis'), tok('pun',','),
                             tok('id',y), tok('op','='), tok('id','Math'), tok('pun',','),
                             tok('id',z), tok('op','='), tok('num',hex(random.randint(1,0xfe)^random.randint(1,0xfe))), tok('pun',','),
                             tok('id',r), tok('op','='), tok('pun','('), tok('num',hex(u^w)), tok('op','^'), tok('num',hex(w)), tok('pun',')'), tok('pun',','),
                             tok('id',xa), tok('op','='), tok('pun','('), tok('num',hex(u|w)), tok('op','&'), tok('num',hex(u)), tok('pun',')'), tok('pun',','),
                             tok('id',xb), tok('op','='), tok('id',xa), tok('op','^'), tok('id',z), tok('pun',';')])
                g = False; continue
        if t['v'] == '}' and depth > 0: depth -= 1
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
        if t['t'] == 'id' and t['v'] == 'return' and p == 0 and b >= 1 and i > 0 and toks[i-1]['v'] in (';','{'):
            g = fresh(used); r = random.randint(1,0xfe); u = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('num',hex(r|u)), tok('op','^'), tok('num',hex(r)), tok('pun',';')])
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
        if t['t'] == 'id' and t['v'] == 'const' and p == 0 and b >= 1 and i > 0 and toks[i-1]['v'] in (';','{'):
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

def reindex(toks, inv, d):
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
    for val, pos in list(snap.items()):
        tri = trice(val)
        if tri is not None:
            xa, xb, xc = tri
            for xv in (xa, xb, xc):
                if xv not in idx:
                    n = random.randint(1, 62); enc = xenc(xv, n)
                    idx[xv] = len(pool); pool.append(''.join('\\x{:02x}'.format(ord(c)) for c in enc)); keys.append(n)
            add[pos] = ('tri', idx[xa], idx[xb], idx[xc]); continue
        parts = split(val)
        if parts is None: continue
        x, y = parts
        if x not in idx:
            n = random.randint(1, 62); enc = xenc(x, n)
            idx[x] = len(pool); pool.append(''.join('\\x{:02x}'.format(ord(c)) for c in enc)); keys.append(n)
        if y not in idx:
            n = random.randint(1, 62); enc = xenc(y, n)
            idx[y] = len(pool); pool.append(''.join('\\x{:02x}'.format(ord(c)) for c in enc)); keys.append(n)
        add[pos] = (idx[x], idx[y])
    return add

def rejoin(toks, d, mapping):
    out = []; i = 0
    while i < len(toks):
        t = toks[i]
        if t['t'] == 'id' and t['v'] == d and i+3 < len(toks) and toks[i+1]['v'] == '(' and toks[i+2]['t'] == 'num' and toks[i+3]['v'] == ')':
            try:
                pos = int(toks[i+2]['v'], 0)
                if pos in mapping:
                    entry = mapping[pos]
                    if entry[0] == 'tri':
                        _, xa, xb, xc = entry
                        out.extend([tok('pun','('), tok('id',d), tok('pun','('), tok('num',str(xa)), tok('pun',')'),
                                     tok('op','+'), tok('id',d), tok('pun','('), tok('num',str(xb)), tok('pun',')'),
                                     tok('op','+'), tok('id',d), tok('pun','('), tok('num',str(xc)), tok('pun',')'), tok('pun',')')])
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
            n = random.randint(1, 62); enc = xenc(r, n)
            idx[r] = len(pool); pool.append(''.join('\\x{:02x}'.format(ord(c)) for c in enc)); keys.append(n)

def twist(pool, keys, a, q):
    n = len(pool)
    if n < 4: return pool, keys, ''
    r = random.randint(2, n - 2)
    p = [pool[(j + r) % n] for j in range(n)]
    g = [keys[(j + r) % n] for j in range(n)]
    s = '_0x' + hex(random.randint(0xaaaa, 0xffff))[2:]
    code = ('(function(){var ' + s + '=' + mba(r) + ';'
            'while(' + s + '-->0x0){' + a + '.unshift(' + a + '.pop());' + q + '.unshift(' + q + '.pop());}'
            '}());')
    return p, g, code

def remap(toks, old, new):
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
        if t['v'] == ';' and p == 0 and b >= 1 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
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
                    x = random.choice(alt)
                    out.extend([tok('pun','('), tok('id',d), tok('pun','('), tok('num',str(x)), tok('pun',')'),
                                 tok('op',','), tok('id',d), tok('pun','('), tok('num',str(n)), tok('pun',')'), tok('pun',')')])
                    i += 4; continue
            except: pass
        out.append(t); i += 1
    return out

def fromlit(toks):
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
    conv = lambda v: ''.join('\\u{:04x}'.format(ord(c)) for c in v)
    return [tok('id', conv(t['v'])) if t['t']=='id' and t['v'].startswith('_0x') else t for t in toks]

def word(c): return c.isalnum() or c in '_$\\' or ord(c) > 127

def gap(a, b):
    if not a or not b: return False
    if word(a) and word(b[0]): return True
    if a in ('+','-') and b[0] in ('+','-'): return True
    return False

def emit(toks):
    out = ''
    for t in toks:
        v = t['v']
        if out and gap(out[-1], v): out += ' '
        out += v
    return out

def chars(s):
    return 'String.fromCharCode(' + ','.join(str(ord(c)) for c in s) + ')'

def xstr(s):
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
    mark = xstr('[native code]')
    return ('(function(){try{if(Math.abs.toString().indexOf(' + mark +')===-1)throw new Error();if(Function.prototype.toString.toString().indexOf(' + mark +')===-1)throw new Error();}catch(e){throw new Error();}}());')

def cage():
    mark = xstr('[native code]')
    return ('(function(){try{if(Function.prototype.bind.toString().indexOf(' + mark +')===-1)throw new Error();}catch(e){throw new Error();}}());')

def save():
    f = hex((0x7a|0x1)^0x2); c = hex(0x40|0x9); g = hex(0x40|0xa); h = hex(0x50|0x15)
    ev = chars('keydown')
    return ('(function(){document.addEventListener(' + ev + ',function(e){if(e.keyCode===' + f + '||(e.ctrlKey&&e.shiftKey&&(e.keyCode===' + c + '||e.keyCode===' + g + '))||(e.ctrlKey&&e.keyCode===' + h + ')){e.preventDefault();e.stopPropagation();}});}());')

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
    nm = chars('name')
    return ('(function(){try{var f=function(){};Object.defineProperty(f,' + nm + ',{get:function(){throw new Error();}});f.name;}catch(e){}}());')

def detect():
    e = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    r = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    i = chars('id')
    return ('(function(){try{var ' + e + '=new Image();Object.defineProperty(' + e + ',' + i + ',{get:function(){throw new Error();}});' + e + '[' + i + '];}catch(' + r + '){}}());')

def watch():
    mark = xstr('[native code]')
    return ('(function(){try{if(Function.prototype.call.toString().indexOf(' + mark +')===-1)throw new Error();}catch(e){}}());')

def frame():
    u = chars('undefined')
    return ('(function(){try{if(typeof window!==' + u + '&&window.top!==window.self)throw new Error();}catch(e){}}());')

def net():
    a = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    pat = xstr('[object Object]')
    return ('(function(){try{var ' + a + '=new RegExp(' + pat + ');if(!' + a + '.test(Object.prototype.toString.call({})))throw new Error();}catch(e){}}());')

def crypt():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    empty = chars('^$')
    return ('(function(){try{var ' + s + '=!RegExp(' + empty + ');if(!' + s + ')throw new Error();}catch(e){}}());')

def cloop():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){var ' + s + '=(0x0|0x0);for(var ' + t + '=(0x0|0x0);' + t + '<(0x64|0x0);' + t + '++)' + s + '+=' + t + ';if(' + s + '<(0x0|0x0))throw new Error();}());')

def seal():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    u = chars('undefined')
    return ('(function(){try{var ' + s + '=typeof window!==' + u + '?window:globalThis;if(!(' + s + ' instanceof Object))throw new Error();}catch(e){}}());')

def drift():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    mark = xstr('[native code]')
    return ('(function(){try{var ' + s + '=eval;if(' + s + '.toString().indexOf(' + mark +')===-1)throw new Error();}catch(e){}}());')

def score():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=[];var ' + t + '=Object.keys(' + s + ');if(' + t + '.length!==(0x0|0x0))throw new Error();}catch(e){}}());')

def pixel():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    kind = xstr('string')
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
    ob = xstr('object')
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
    type = xstr('Function'); nm = chars('name')
    return ('(function(){try{var ' + s + '=Object.keys;var ' + t + '=' + s + '.constructor;if(' + t + '[' + nm + ']!==' + type +')throw new Error();}catch(e){}}());')

def shield():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    mark = xstr('[native code]')
    return ('(function(){try{var ' + s + '=Function.prototype.constructor;if(' + s + '.toString().indexOf(' + mark +')===-1)throw new Error();}catch(e){}}());')

def vault():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=new Error();var ' + t + '=Object.getPrototypeOf(' + s + ');if(!(' + t + ' instanceof Object))throw new Error();}catch(e){}}());')

def spike():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    func = chars('log'); mark = xstr('[native code]')
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
    nm = chars('named'); nk = chars('name')
    return ('(function(){try{var ' + s + '=(function named(){}).name;if(' + s + '!==' + nm + ')throw new Error();}catch(e){}}());')

def smelt():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    gt = chars('getTime')
    return ('(function(){try{var ' + s + '=new Date((0x0|0x0));var ' + t + '=' + s + '[' + gt + ']();if(' + t + '!==(0x0|0x0))throw new Error();}catch(e){}}());')

def crimp():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    ab = chars('ab'); ac = chars('a'); bc = chars('b')
    return ('(function(){try{var ' + s + '=' + ac + '+' + bc + ';if(' + s + '!==' + ab + ')throw new Error();}catch(e){}}());')

def smog():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    js = chars('[1,2,3]'); ps = chars('parse')
    return ('(function(){try{var ' + s + '=JSON[' + ps + '](' + js + ');if(!Array.isArray(' + s + '))throw new Error();}catch(e){}}());')

def blaze():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    mx = chars('max')
    return ('(function(){try{var ' + s + '=Math[' + mx + '];var ' + t + '=' + s + '((0x1|0x0),(0x2|0x0));if(' + t + '!==(0x2|0x0))throw new Error();}catch(e){}}());')

def draft():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    kind = chars('string'); ts = chars('toString')
    return ('(function(){try{var ' + s + '=(0x1|0x0)[' + ts + ']();if(typeof ' + s + '!==' + kind +')throw new Error();}catch(e){}}());')

def shard():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    type = chars('function'); ax = chars('assign')
    return ('(function(){try{if(typeof Object[' + ax + ']!==' + type +')throw new Error();var ' + s + '=Object[' + ax + ']({},{a:(0x1|0x0)});if(' + s + '.a!==(0x1|0x0))throw new Error();}catch(e){}}());')

def flint():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    pu = chars('push'); po = chars('pop')
    return ('(function(){try{var ' + s + '=[];' + s + '[' + pu + ']((0x1|0x0));var ' + t + '=' + s + '[' + po + ']();if(' + t + '!==(0x1|0x0))throw new Error();}catch(e){}}());')

def loom():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    type = chars('function')
    return ('(function(){try{var ' + s + '=typeof Symbol;if(' + s + '!==' + type +')throw new Error();}catch(e){}}());')

def stealth():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    pat = xstr('^([^ ]+( +[^ ]+)+)+[^ ]}')
    return ('(function(){try{var ' + s + '=new RegExp(' + pat + ');' + s + '[' + chars('constructor') + '](' + chars('') + ');throw new Error();}catch(e){if(e instanceof TypeError)return;throw new Error();}}());')

def burn():
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    return ('(function(){try{var ' + s + '=(0x2|0x0);var ' + t + '=(0x2|0x0);if((' + s + '*' + t + ')!==(0x4|0x0))throw new Error();}catch(e){}}());')

def prot():
    traps = [probe(),snare(),guard(),cage(),leak(),save(),tamper(),block(),dom(),timing(),hooks(),detect(),watch(),frame(),net(),crypt(),cloop(),seal(),drift(),score(),pixel(),flare(),pulse(),spark(),trace(),glow(),frost(),haze(),burn(),stealth(),bench(),lock(),shield(),vault(),spike(),glint(),ridge(),veil(),smelt(),crimp(),smog(),blaze(),draft(),shard(),flint(),loom()]
    random.shuffle(traps)
    wrapped = ['try{' + t + '}catch(e){}' for t in traps]
    delay = hex(random.randint(30, 80))
    return 'setTimeout(function(){' + ''.join(wrapped) + '},' + delay + ');'

def scatter(toks, used):
    out = []; i = 0; depth = 0; g = False
    while i < len(toks):
        t = toks[i]
        if t['t'] == 'id' and t['v'] == 'function' and body(toks, i): g = True
        if t['v'] == '{' and g:
            depth += 1
            if depth == 1:
                out.append(t); i += 1
                r = fresh(used); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
                out.extend([tok('id','var'), tok('id',r), tok('op','='), tok('id','function'), tok('pun','('), tok('pun',')'), tok('pun','{'),
                             tok('id','return'), tok('pun','('), tok('num',hex(u^w)), tok('op','^'), tok('num',hex(w)), tok('pun',')'), tok('pun',';'),
                             tok('pun','}'), tok('pun',';')])
                g = False; continue
        if t['v'] == '}' and depth > 0: depth -= 1
        out.append(t); i += 1
    return out

def inflate(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 1 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            g = fresh(used); r = fresh(used); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(u)), tok('op','>>>'), tok('num','0x0'), tok('pun',')'), tok('op','|'), tok('num',hex(w^w)), tok('pun',';')])
            out.extend([tok('id','var'), tok('id',r), tok('op','='), tok('pun','~'), tok('pun','('), tok('pun','~'), tok('id',g), tok('pun',')'), tok('op','+'), tok('num','0x0'), tok('pun',';')])
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
        if t['v'] == ';' and p == 0 and b >= 2 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            g = fresh(used); r = fresh(used); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('pun','('), tok('num',hex(u)), tok('op','&'), tok('num',hex(u)), tok('pun',')'), tok('pun',';')])
            out.extend([tok('id','var'), tok('id',r), tok('op','='), tok('pun','('), tok('id',g), tok('op','^'), tok('num',hex(w^w)), tok('op','|'), tok('num',hex(0)), tok('pun',')'), tok('pun',';')])
        i += 1
    return out

def jolt(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        if t['t'] == 'id' and t['v'] == 'return' and p == 0 and b >= 1 and i > 0 and toks[i-1]['v'] in (';','{'):
            g = fresh(used); r = fresh(used); u = random.randint(1,0xfe); w = random.randint(1,0xfe)
            out.extend([tok('id','var'), tok('id',g), tok('op','='), tok('num',hex(u^w)), tok('op','|'), tok('num','0x0'), tok('pun',';'),
                        tok('id','var'), tok('id',r), tok('op','='), tok('pun','~'), tok('pun','('), tok('id',g), tok('op','^'), tok('num',hex(u)), tok('pun',')'), tok('pun',';')])
        out.append(t); i += 1
    return out

def strip(code):
    m = re.match(r'(// ==UserScript==.*?// ==/UserScript==\s*)', code, re.DOTALL)
    if m: return m.group(1), code[m.end():]
    return '', code

def obf(src):
    header, body = strip(src)
    toks = scan(body)
    toks = templit(toks)
    toks = rename(toks)
    toks, pool, keys, d, a, k, idx = cipher(toks)
    snap = dict(idx)
    toks = props(toks, d, snap)
    toks = chain(toks, d, snap)
    toks, v, l, e, b, m, y = cipher(toks)
    lens = dict(y)
    toks = chain(toks, e, lens)
    used = {t['v'] for t in toks if t['t'] == 'id' and t['v'].startswith('_0x')}
    toks = flat(toks, used)
    toks = inject(toks, used)
    toks = alias(toks, used)
    toks = scatter(toks, used)
    toks = extra(toks, used)
    toks = morph(toks, used)
    toks = jolt(toks, used)
    toks = cloak(toks, used)
    toks = fill(toks, used)
    toks = inflate(toks, used)
    toks = hurl(toks, used)
    grain(pool, keys, idx)
    z = pairs(pool, keys, idx, snap)
    toks = rejoin(toks, d, z)
    pool, keys = reroll(pool, keys)
    pool, keys, w = shuffle(pool, keys)
    toks = reindex(toks, w, d)
    v, l, w = shuffle(v, l)
    toks = reindex(toks, w, e)
    toks = nums(toks)
    toks = bools(toks)
    pool, keys, c = spin(pool, keys, a, k)
    v, l, f = twist(v, l, b, m)
    def pick(): return '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    g,h,i,n,o,p,s,t,shell = pick(),pick(),pick(),pick(),pick(),pick(),pick(),pick(),pick()
    proxy = ('var ' + g + '=(function(' + i + ',' + s + '){return function(' + o + '){return ' + i + '(' + o + '^' + s + '^' + s + ');};}(' + d + ',' + mba(random.randint(1,0xfe)) + '));'
             'var ' + h + '=(function(' + n + ',' + t + '){return function(' + p + '){return ' + n + '(' + p + '^' + t + '^' + t + ');};}(' + e + ',' + mba(random.randint(1,0xfe)) + '));'
             'var ' + shell + '=(function(' + i + ',' + s + '){return function(' + o + '){return ' + i + '(' + o + ');};}(' + g + ',' + mba(random.randint(1,0xfe)) + '));')
    toks = remap(toks, d, g)
    toks = remap(toks, e, h)
    toks = fromlit(toks)
    toks = noop(used) + toks
    toks = encode(toks)
    code = emit(toks)
    r = arrays(pool, keys, a, k)
    q = arrays(v, l, b, m)
    j = rolling(d, a, k)
    u = decode(e, b, m)
    anchor = 'if(false){GM_xmlhttpRequest({});}'
    pt = emit(obsnum(scan(prot())))
    return header + anchor + r + q + j + u + c + f + proxy + pt + code


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

def obsnum(toks):
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
        if t['v'] == ';' and p == 0 and b >= 1 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
            out.extend(trap(used))
        i += 1
    return out

def spin(pool, keys, a, q):
    n = len(pool)
    if n < 4: return pool, keys, ''
    r = random.randint(2, n - 2)
    rp = [pool[(j + r) % n] for j in range(n)]
    rk = [keys[(j + r) % n] for j in range(n)]
    s = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    t = '_0x' + hex(random.randint(0xaaaa,0xffff))[2:]
    half = r // 2
    code = ('(function(){var ' + s + '=' + mba(half) + ';var ' + t + '=' + mba(r - half) + ';'
            'while(' + s + '-->0x0){' + a + '.unshift(' + a + '.pop());' + q + '.unshift(' + q + '.pop());}' +
            'while(' + t + '-->0x0){' + a + '.unshift(' + a + '.pop());' + q + '.unshift(' + q + '.pop());}' +
            '}());')
    return rp, rk, code

def vex(toks, used):
    out = []; i = 0; p = 0; b = 0
    while i < len(toks):
        t = toks[i]
        if t['v'] in ('(','['): p += 1
        if t['v'] in (')',']'): p -= 1
        if t['v'] == '{': b += 1
        if t['v'] == '}': b -= 1
        out.append(t)
        if t['v'] == ';' and p == 0 and b >= 2 and i+1 < len(toks) and toks[i+1]['v'] not in skip:
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
