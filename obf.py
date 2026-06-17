import sys
import re
import random
import base64
from collections import namedtuple

token = namedtuple('token', ['t', 'v'])

abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
maps = {}
def hide(data):
    std = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    raw = base64.b64encode(data).decode('utf-8')
    trans = str.maketrans(std, abc)
    return raw.translate(trans)

def haze(code):
    greek = ["α", "β", "γ", "δ", "ε", "ζ", "η", "θ", "ι", "κ", "λ", "μ", "ν", "ξ", "ο", "π", "ρ", "σ", "τ", "υ", "φ", "χ", "ψ", "ω"]
    stash = []
    code = re.sub(r'("[^"\\]*(?:\\.[^"\\]*)*"|\'[^\'\\]*(?:\\.[^\'\\]*)*\'|`[^`\\]*(?:\\.[^`\\]*)*`|/(?![*+?])(?:[^\r\n\[/\\]|\\.|\[(?:[^\r\n\]\\]|\\.)*\])+/g?)', lambda m: (stash.append(m.group(0)), f"__STR_{len(stash)-1}__")[1], code)
    vars = re.findall(r'\b[a-zA-Z_$][a-zA-Z0-9_$]*\b', code)
    skip = {"var", "let", "const", "function", "return", "if", "else", "for", "while", "do", "switch", "case", "break", "continue", "default", "try", "catch", "finally", "throw", "new", "this", "typeof", "instanceof", "delete", "void", "in", "of", "class", "extends", "import", "export", "debugger", "true", "false", "null", "undefined", "async", "await", "yield", "with", "super", "decodeURIComponent", "escape", "Date", "now", "push", "length", "charCodeAt", "fromCharCode", "console", "Function", "d", "o", "k", "String", "Object", "Image", "globalThis", "window", "document", "setInterval", "setTimeout", "performance", "Math", "Infinity", "NaN", "arguments", "__ABC__", "slice", "toString", "join", "unref", "imul", "max", "min", "abs", "floor", "defineProperty", "freeze", "keys", "prototype", "test", "log", "shift", "push", "_0xdec", "_0xabc", "__ARRAY__", "substring", "indexOf", "split", "replace", "throw", "Error", "innerWidth", "outerWidth", "innerHeight", "outerHeight", "__HASH__", "__LEN__", "sign", "size", "map", "eval", "error", "GM_xmlhttpRequest", "GM_setValue", "GM_getValue", "GM_deleteValue", "GM_listValues", "GM_addStyle", "GM_getResourceText", "GM_getResourceURL", "GM_log", "GM_openInTab", "GM_registerMenuCommand", "GM_unregisterMenuCommand", "GM_setClipboard", "GM_info"}

    vars = sorted(list(set(vars) - skip))
    vars = [v for v in vars if not (len(v) == 3 and v[0] == 'x' and all(c in '0123456789abcdefABCDEF' for c in v[1:]))]
    vars = [v for v in vars if not (v.startswith('__STR_') and v.endswith('__'))]
    mapping = {v: greek[i % len(greek)] + str(i // len(greek)) for i, v in enumerate(vars)}
    for old, new in mapping.items():
        code = re.sub(r'\b' + re.escape(old) + r'\b', lambda m, val=new: val, code)
    for old, nw in [
        ('charCodeAt', '["\\x63\\x68\\x61\\x72\\x43\\x6f\\x64\\x65\\x41\\x74"]'),
        ('fromCharCode', '["\\x66\\x72\\x6f\\x6d\\x43\\x68\\x61\\x72\\x43\\x6f\\x64\\x65"]'),
        ('length', '["\\x6c\\x65\\x6e\\x67\\x74\\x68"]'),
        ('push', '["\\x70\\x75\\x73\\x68"]'),
        ('shift', '["\\x73\\x68\\x69\\x66\\x74"]'),
        ('escape', 'globalThis["\\x65\\x73\\x63\\x61\\x70\\x65"]'),
        ('decodeURIComponent', 'globalThis["\\x64\\x65\\x63\\x6f\\x64\\x65\\x55\\x52\\x49\\x43\\x6f\\x6d\\x70\\x6f\\x6e\\x65\\x6e\\x74"]'),
        ('Function', 'globalThis["\\x46\\x75\\x6e\\x63\\x74\\x69\\x6f\\x6e"]')
    ]:
        code = code.replace('.' + old, nw)
        if old in {'escape', 'decodeURIComponent', 'Function'}:
            code = re.sub(r'\b' + re.escape(old) + r'\b', lambda m: nw.replace('\\', '\\\\'), code)
    code = re.sub(r'__STR_(\d+)__', lambda m: stash[int(m.group(1))], code)
    return code

def space(c): return c in ' \t\n\r\v\f'
def digit(c): return '0' <= c <= '9'
def alpha(c): return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or c == '_' or c == '$' or ord(c) > 127
def valid(c): return '0' <= c <= '9' or 'a' <= c <= 'f' or 'A' <= c <= 'F'

def chunk(val):
    raw = val[1:-1]
    res = []
    i = 0
    n = len(raw)
    start = 0
    while i < n:
        if raw[i:i+2] == '${':
            if i > start:
                res.append(('static', raw[start:i]))
            i += 2
            beg = i
            dep = 1
            while i < n and dep > 0:
                if raw[i] == '{': dep += 1
                elif raw[i] == '}': dep -= 1
                i += 1
            res.append(('dynamic', raw[beg:i-1]))
            start = i
        else:
            i += 1
    if start < n:
        res.append(('static', raw[start:]))
    return res


def text(code, i, n):
    q = code[i]
    start = i
    i += 1
    while i < n:
        c = code[i]
        if c == '\\':
            i += 2
            continue
        if c == q:
            i += 1
            return code[start:i], i
        i += 1
    return code[start:i], i

def num(code, i, n):
    start = i
    if code[i] == '0' and i + 1 < n:
        nxt = code[i+1].lower()
        if nxt == 'x':
            i += 2
            while i < n and valid(code[i]): i += 1
            return code[start:i], i
        if nxt == 'b':
            i += 2
            while i < n and code[i] in '01': i += 1
            return code[start:i], i
        if nxt == 'o':
            i += 2
            while i < n and '0' <= code[i] <= '7': i += 1
            return code[start:i], i
    while i < n and digit(code[i]): i += 1
    if i < n and code[i] == '.':
        i += 1
        while i < n and digit(code[i]): i += 1
    if i < n and code[i].lower() == 'e':
        i += 1
        if i < n and code[i] in '+-': i += 1
        while i < n and digit(code[i]): i += 1
    return code[start:i], i

def name(code, i, n):
    start = i
    i += 1
    while i < n and (alpha(code[i]) or digit(code[i])): i += 1
    return code[start:i], i

def regex(code, i, n):
    start = i
    i += 1
    flag = False
    while i < n:
        c = code[i]
        if c == '\\':
            i += 2
            continue
        if c == '[': flag = True
        if c == ']': flag = False
        if c == '/' and not flag:
            i += 1
            while i < n and alpha(code[i]): i += 1
            return code[start:i], i
        i += 1
    return code[start:i], i

def sign(code, i, n):
    ops = [
        '>>>=', '===', '!==', '***', '&&=', '||=', '??=', '<<=', '>>=',
        '++', '--', '==', '!=', '+=', '-=', '*=', '/=', '%=', '&=', '|=',
        '^=', '&&', '||', '??', '<<', '>>', '**', '<=', '>=', '=>', '?.',
        '+', '-', '*', '/', '%', '=', '<', '>', '&', '|', '^', '!', '~',
        '?', ':', ';', ',', '.', '(', ')', '[', ']', '{', '}'
    ]
    for op in ops:
        size = len(op)
        if i + size <= n and code[i:i+size] == op: return op, i + size
    return code[i], i + 1

def scan(code):
    res = []
    i = 0
    n = len(code)
    prev = None
    ops = {
        '=', '+', '-', '*', '/', '%', '&', '|', '^', '!', '?', ':', '~',
        ',', ';', '(', '[', '{', 'return', 'throw', 'typeof', 'in',
        'instanceof', 'case', 'delete', 'void', 'new', '=>'
    }
    while i < n:
        c = code[i]
        if space(c):
            i += 1
            continue
        if c == '/' and i + 1 < n and code[i+1] == '/':
            i += 2
            while i < n and code[i] != '\n': i += 1
            continue
        if c == '/' and i + 1 < n and code[i+1] == '*':
            i += 2
            while i < n and not (code[i] == '*' and i + 1 < n and code[i+1] == '/'): i += 1
            i += 2
            continue
        if c == '/':
            flag = False
            if prev is None: flag = True
            if prev and (prev.t == 'op' or prev.t == 'punc') and prev.v in ops: flag = True
            if prev and prev.t == 'id' and prev.v in ops: flag = True
            if flag:
                val, i = regex(code, i, n)
                prev = token('regex', val)
                res.append(prev)
                continue
        if c in '"\'`':
            val, i = text(code, i, n)
            prev = token('str', val)
            res.append(prev)
            continue
        if digit(c) or (c == '.' and i + 1 < n and digit(code[i+1])):
            val, i = num(code, i, n)
            prev = token('num', val)
            res.append(prev)
            continue
        if alpha(c):
            val, i = name(code, i, n)
            prev = token('id', val)
            res.append(prev)
            continue
        val, i = sign(code, i, n)
        if val in {'(', ')', '[', ']', '{', '}', ';', ',', '.'}: prev = token('punc', val)
        if val not in {'(', ')', '[', ']', '{', '}', ';', ',', '.'}: prev = token('op', val)
        res.append(prev)
    return res

def ksa(key):
    s = list(range(256))
    j = 0
    for i in range(256):
        j = (j + s[i] + key[i % len(key)]) % 256
        s[i], s[j] = s[j], s[i]
    return s

def prga(s, n):
    i = 0
    j = 0
    key = []
    for x in range(n):
        i = (i + 1) % 256
        j = (j + s[i]) % 256
        s[i], s[j] = s[j], s[i]
        key.append(s[(s[i] + s[j]) % 256])
    return key

def caesar(data, key): return bytes([(d + key) % 256 for d in data])
def xor(data, key): return bytes([d ^ key[i % len(key)] for i, d in enumerate(data)])
def vigenere(data, key): return bytes([(d + key[i % len(key)]) % 256 for i, d in enumerate(data)])

def ext(a, b):
    if a == 0: return b, 0, 1
    g, y, x = ext(b % a, a)
    return g, x - (b // a) * y, y

def invert(a, m):
    g, x, y = ext(a, m)
    return x % m

def affine(data, a, b): return bytes([(a * d + b) % 256 for d in data])
def atbash(data): return bytes([255 - d for d in data])

def djb(data):
    h = 5381
    for d in data: h = ((h << 5) + h) + d
    return h & 0xffffffff

def sdbm(data):
    h = 0
    for d in data: h = d + (h << 6) + (h << 16) - h
    return h & 0xffffffff

def xtea(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    k = [
        int.from_bytes(key[0:4], 'big'),
        int.from_bytes(key[4:8], 'big'),
        int.from_bytes(key[8:12], 'big'),
        int.from_bytes(key[12:16], 'big')
    ]
    for i in range(0, len(data), 8):
        a = int.from_bytes(data[i:i+4], 'big')
        b = int.from_bytes(data[i+4:i+8], 'big')
        sum = 0
        delta = 0x9e3779b9
        for r in range(32):
            a = (a + (((b << 4 ^ b >> 5) + b) ^ (sum + k[sum & 3]))) & 0xffffffff
            sum = (sum + delta) & 0xffffffff
            b = (b + (((a << 4 ^ a >> 5) + a) ^ (sum + k[sum >> 11 & 3]))) & 0xffffffff
        out.extend(a.to_bytes(4, 'big'))
        out.extend(b.to_bytes(4, 'big'))
    return bytes(out)

def rc(data, key):
    s = ksa(key)
    k = prga(s, len(data))
    return bytes([d ^ k[i] for i, d in enumerate(data)])

def rcs(data, key):
    out = bytearray()
    pad = (16 - len(data) % 16) % 16
    data = data + bytes([pad] * (pad if pad > 0 else 16))
    k = [
        int.from_bytes(key[0:4], 'big'),
        int.from_bytes(key[4:8], 'big'),
        int.from_bytes(key[8:12], 'big'),
        int.from_bytes(key[12:16], 'big')
    ]
    for i in range(0, len(data), 16):
        a = int.from_bytes(data[i:i+4], 'big')
        b = int.from_bytes(data[i+4:i+8], 'big')
        c = int.from_bytes(data[i+8:i+12], 'big')
        d = int.from_bytes(data[i+12:i+16], 'big')
        b = (b + k[0]) & 0xffffffff
        d = (d + k[1]) & 0xffffffff
        for r in range(1, 21):
            t = (((b * (2 * b + 1)) & 0xffffffff) << 5 | ((b * (2 * b + 1)) & 0xffffffff) >> 27) & 0xffffffff
            u = (((d * (2 * d + 1)) & 0xffffffff) << 5 | ((d * (2 * d + 1)) & 0xffffffff) >> 27) & 0xffffffff
            a = (((a ^ t) << (u & 31) | (a ^ t) >> (32 - (u & 31))) + k[(2 * r) % 4]) & 0xffffffff
            c = (((c ^ u) << (t & 31) | (c ^ u) >> (32 - (t & 31))) + k[(2 * r + 1) % 4]) & 0xffffffff
            a, b, c, d = b, c, d, a
        a = (a + k[2]) & 0xffffffff
        c = (c + k[3]) & 0xffffffff
        out.extend(a.to_bytes(4, 'big'))
        out.extend(b.to_bytes(4, 'big'))
        out.extend(c.to_bytes(4, 'big'))
        out.extend(d.to_bytes(4, 'big'))
    return bytes(out)

def prep(key):
    seed = djb(key)
    val = seed
    p = []
    for i in range(18):
        val = (1103515245 * val + 12345) & 0xffffffff
        p.append(val)
    s = []
    for i in range(4):
        box = []
        for j in range(256):
            val = (1103515245 * val + 12345) & 0xffffffff
            box.append(val)
        s.append(box)
    return p, s

def blow(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    p, s = prep(key)
    for idx in range(0, len(data), 8):
        l = int.from_bytes(data[idx:idx+4], 'big')
        r = int.from_bytes(data[idx+4:idx+8], 'big')
        for round in range(16):
            l = l ^ p[round]
            w = (l >> 24) & 0xff
            x = (l >> 16) & 0xff
            y = (l >> 8) & 0xff
            z = l & 0xff
            f = (s[0][w] + s[1][x]) & 0xffffffff
            f = (f ^ s[2][y]) & 0xffffffff
            f = (f + s[3][z]) & 0xffffffff
            r = r ^ f
            l, r = r, l
        l, r = r, l
        r = r ^ p[16]
        l = l ^ p[17]
        out.extend(l.to_bytes(4, 'big'))
        out.extend(r.to_bytes(4, 'big'))
    return bytes(out)

def make(key):
    seed = djb(key)
    val = seed
    def rand():
        nonlocal val
        val = (1103515245 * val + 12345) & 0xffffffff
        return val
    ip = list(range(64))
    for i in range(63, 0, -1):
        j = rand() % (i + 1)
        ip[i], ip[j] = ip[j], ip[i]
    fp = [0] * 64
    for i, x in enumerate(ip): fp[x] = i
    e = []
    for i in range(48): e.append(rand() % 32)
    p = list(range(32))
    for i in range(31, 0, -1):
        j = rand() % (i + 1)
        p[i], p[j] = p[j], p[i]
    s = []
    for i in range(8):
        box = []
        for j in range(64): box.append(rand() % 16)
        s.append(box)
    sub = []
    for i in range(16):
        kl = rand() & 0xffffff
        kr = rand() & 0xffffff
        sub.append((kl, kr))
    return ip, fp, e, p, s, sub

def des(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    ip, fp, e, p, s, sub = make(key)
    for idx in range(0, len(data), 8):
        block = int.from_bytes(data[idx:idx+8], 'big')
        perm = 0
        for i in range(64):
            bit = (block >> (63 - ip[i])) & 1
            perm = (perm << 1) | bit
        l = (perm >> 32) & 0xffffffff
        r = perm & 0xffffffff
        for round in range(16):
            kl, kr = sub[round]
            exp = 0
            for i in range(48):
                bit = (r >> (31 - e[i])) & 1
                exp = (exp << 1) | bit
            exp = exp ^ ((kl << 24) | kr)
            u = 0
            for i in range(8):
                chunk = (exp >> (42 - i * 6)) & 0x3f
                val = s[i][chunk]
                u = (u << 4) | val
            v = 0
            for i in range(32):
                bit = (u >> (31 - p[i])) & 1
                v = (v << 1) | bit
            l, r = r, l ^ v
        combined = (r << 32) | l
        final = 0
        for i in range(64):
            bit = (combined >> (63 - fp[i])) & 1
            final = (final << 1) | bit
        out.extend(final.to_bytes(8, 'big'))
    return bytes(out)

def speck(data, key):
    out = bytearray()
    pad = (4 - len(data) % 4) % 4
    data = data + bytes([pad] * (pad if pad > 0 else 4))
    k = [
        int.from_bytes(key[0:2], 'big'),
        int.from_bytes(key[2:4], 'big'),
        int.from_bytes(key[4:6], 'big'),
        int.from_bytes(key[6:8], 'big')
    ]
    sub = []
    l = k[1:]
    a = k[0]
    sub.append(a)
    for i in range(21):
        val = ((((l[i] >> 7) | (l[i] << 9)) & 0xffff) + a) & 0xffff
        val = (val ^ i) & 0xffff
        a = (((a << 2) | (a >> 14)) & 0xffff) ^ val
        l.append(val)
        sub.append(a)
    for i in range(0, len(data), 4):
        x = int.from_bytes(data[i:i+2], 'big')
        y = int.from_bytes(data[i+2:i+4], 'big')
        for item in sub:
            x = ((((x >> 7) | (x << 9)) & 0xffff) + y) & 0xffff
            x = (x ^ item) & 0xffff
            y = (((y << 2) | (y >> 14)) & 0xffff) ^ x
        out.extend(x.to_bytes(2, 'big'))
        out.extend(y.to_bytes(2, 'big'))
    return bytes(out)

def simon(data, key):
    out = bytearray()
    pad = (4 - len(data) % 4) % 4
    data = data + bytes([pad] * (pad if pad > 0 else 4))
    k = [
        int.from_bytes(key[0:2], 'big'),
        int.from_bytes(key[2:4], 'big'),
        int.from_bytes(key[4:6], 'big'),
        int.from_bytes(key[6:8], 'big')
    ]
    sub = []
    for i in range(4): sub.append(k[i])
    z = [
        1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1,
        0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1,
        1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1,
        0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1
    ]
    for i in range(4, 32):
        temp = (((sub[i-1] >> 3) | (sub[i-1] << 13)) & 0xffff) ^ sub[i-3]
        temp = temp ^ (((temp >> 1) | (temp << 15)) & 0xffff)
        sub.append(sub[i-4] ^ temp ^ z[(i-4) % 62] ^ 0xfffc)
    for i in range(0, len(data), 4):
        x = int.from_bytes(data[i:i+2], 'big')
        y = int.from_bytes(data[i+2:i+4], 'big')
        for item in sub:
            temp = ((((x << 1) | (x >> 15)) & 0xffff) & (((x << 8) | (x >> 8)) & 0xffff)) ^ (((x << 2) | (x >> 14)) & 0xffff) ^ y ^ item
            y = x
            x = temp
        out.extend(x.to_bytes(2, 'big'))
        out.extend(y.to_bytes(2, 'big'))
    return bytes(out)

def rcf(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    l = [int.from_bytes(key[i:i+4], 'big') for i in range(0, 16, 4)]
    s = []
    s.append(0xb7e15163)
    for i in range(1, 26): s.append((s[i-1] + 0x9e3779b9) & 0xffffffff)
    i = 0
    j = 0
    a = 0
    b = 0
    for r in range(78):
        v = (s[i] + a + b) & 0xffffffff
        s[i] = a = ((v << 3) | (v >> 29)) & 0xffffffff
        t = (l[j] + a + b) & 0xffffffff
        rot = (a + b) & 31
        if rot == 0:
            l[j] = b = t
        else:
            l[j] = b = ((t << rot) | (t >> (32 - rot))) & 0xffffffff
        i = (i + 1) % 26
        j = (j + 1) % 4
    for i in range(0, len(data), 8):
        x = int.from_bytes(data[i:i+4], 'big')
        y = int.from_bytes(data[i+4:i+8], 'big')
        x = (x + s[0]) & 0xffffffff
        y = (y + s[1]) & 0xffffffff
        for r in range(1, 13):
            rot = y & 31
            u = (x ^ y) & 0xffffffff
            if rot == 0:
                x = (u + s[2*r]) & 0xffffffff
            else:
                x = (((u << rot) | (u >> (32 - rot))) + s[2*r]) & 0xffffffff
            rot = x & 31
            w = (y ^ x) & 0xffffffff
            if rot == 0:
                y = (w + s[2*r+1]) & 0xffffffff
            else:
                y = (((w << rot) | (w >> (32 - rot))) + s[2*r+1]) & 0xffffffff
        out.extend(x.to_bytes(4, 'big'))
        out.extend(y.to_bytes(4, 'big'))
    return bytes(out)

def chacha(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    for i in range(0, len(data), 8):
        x = int.from_bytes(data[i:i+4], 'big')
        y = int.from_bytes(data[i+4:i+8], 'big')
        k = [
            int.from_bytes(key[0:4], 'big'),
            int.from_bytes(key[4:8], 'big'),
            int.from_bytes(key[8:12], 'big'),
            int.from_bytes(key[12:16], 'big')
        ]
        x = (x ^ k[0]) & 0xffffffff
        y = (y ^ k[1]) & 0xffffffff
        x = (x + y) & 0xffffffff
        y = (((y ^ x) << 16) | ((y ^ x) >> 16)) & 0xffffffff
        x = (x + k[2]) & 0xffffffff
        y = (y ^ x) & 0xffffffff
        x = (x + y) & 0xffffffff
        y = (((y ^ x) << 12) | ((y ^ x) >> 20)) & 0xffffffff
        out.extend(x.to_bytes(4, 'big'))
        out.extend(y.to_bytes(4, 'big'))
    return bytes(out)

def sps(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    k = [
        int.from_bytes(key[0:4], 'big'),
        int.from_bytes(key[4:8], 'big'),
        int.from_bytes(key[8:12], 'big'),
        int.from_bytes(key[12:16], 'big')
    ]
    sub = []
    l = k[1:]
    a = k[0]
    sub.append(a)
    for i in range(26):
        val = ((((l[i] >> 8) | (l[i] << 24)) & 0xffffffff) + a) & 0xffffffff
        val = (val ^ i) & 0xffffffff
        a = (((a << 3) | (a >> 29)) & 0xffffffff) ^ val
        l.append(val)
        sub.append(a)
    for i in range(0, len(data), 8):
        x = int.from_bytes(data[i:i+4], 'big')
        y = int.from_bytes(data[i+4:i+8], 'big')
        for item in sub:
            x = ((((x >> 8) | (x << 24)) & 0xffffffff) + y) & 0xffffffff
            x = (x ^ item) & 0xffffffff
            y = (((y << 3) | (y >> 29)) & 0xffffffff) ^ x
        out.extend(x.to_bytes(4, 'big'))
        out.extend(y.to_bytes(4, 'big'))
    return bytes(out)

def sis(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    k = [
        int.from_bytes(key[0:4], 'big'),
        int.from_bytes(key[4:8], 'big'),
        int.from_bytes(key[8:12], 'big'),
        int.from_bytes(key[12:16], 'big')
    ]
    sub = []
    for i in range(4): sub.append(k[i])
    z = [
        1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1,
        0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1
    ]
    for i in range(4, 36):
        temp = (((sub[i-1] >> 3) | (sub[i-1] << 29)) & 0xffffffff) ^ sub[i-3]
        temp = temp ^ (((temp >> 1) | (temp << 31)) & 0xffffffff)
        sub.append(sub[i-4] ^ temp ^ z[(i-4) % 32] ^ 0xfffffffc)
    for i in range(0, len(data), 8):
        x = int.from_bytes(data[i:i+4], 'big')
        y = int.from_bytes(data[i+4:i+8], 'big')
        for item in sub:
            temp = ((((x << 1) | (x >> 31)) & 0xffffffff) & (((x << 8) | (x >> 24)) & 0xffffffff)) ^ (((x << 2) | (x >> 30)) & 0xffffffff) ^ y ^ item
            y = x
            x = temp
        out.extend(x.to_bytes(4, 'big'))
        out.extend(y.to_bytes(4, 'big'))
    return bytes(out)

def gcd(a, b):
    while b: a, b = b, a % b
    return a

def tea(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    k = [int.from_bytes(key[i:i+4], 'big') for i in range(0, 16, 4)]
    for i in range(0, len(data), 8):
        v0 = int.from_bytes(data[i:i+4], 'big')
        v1 = int.from_bytes(data[i+4:i+8], 'big')
        sum = 0
        delta = 0x9e3779b9
        for r in range(32):
            sum = (sum + delta) & 0xffffffff
            v0 = (v0 + (((v1 << 4) + k[0]) ^ (v1 + sum) ^ ((v1 >> 5) + k[1]))) & 0xffffffff
            v1 = (v1 + (((v0 << 4) + k[2]) ^ (v0 + sum) ^ ((v0 >> 5) + k[3]))) & 0xffffffff
        out.extend(v0.to_bytes(4, 'big'))
        out.extend(v1.to_bytes(4, 'big'))
    return bytes(out)

def loki(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    seed = djb(key)
    val = seed
    sub = []
    for i in range(16):
        val = (1103515245 * val + 12345) & 0xffffffff
        sub.append(val)
    for idx in range(0, len(data), 8):
        l = int.from_bytes(data[idx:idx+4], 'big')
        r = int.from_bytes(data[idx+4:idx+8], 'big')
        for round in range(16):
            f = (r ^ sub[round]) & 0xffffffff
            f = (((f << 7) | (f >> 25)) & 0xffffffff) ^ 0x9e3779b9
            l, r = r, l ^ f
        out.extend(l.to_bytes(4, 'big'))
        out.extend(r.to_bytes(4, 'big'))
    return bytes(out)

def hight(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    seed = djb(key)
    val = seed
    sub = []
    for i in range(32):
        val = (1103515245 * val + 12345) & 0xff
        sub.append(val)
    for idx in range(0, len(data), 8):
        state = list(data[idx:idx+8])
        for round in range(32):
            n = [0] * 8
            n[7] = (state[0] - sub[round]) & 0xff
            n[0] = state[1]
            n[1] = (state[2] ^ sub[round]) & 0xff
            n[2] = state[3]
            n[3] = (state[4] - sub[round]) & 0xff
            n[4] = state[5]
            n[5] = (state[6] ^ sub[round]) & 0xff
            n[6] = state[7]
            state = n
        out.extend(state)
    return bytes(out)

def present(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    seed = djb(key)
    val = seed
    sub = []
    for i in range(32):
        val = (1103515245 * val + 12345) & 0xffffffff
        sub.append(val)
    for idx in range(0, len(data), 8):
        l = int.from_bytes(data[idx:idx+4], 'big')
        r = int.from_bytes(data[idx+4:idx+8], 'big')
        for round in range(31):
            l ^= sub[round]
            r ^= sub[round+1]
            l = ((l << 9) | (l >> 23)) & 0xffffffff
            r = ((r << 13) | (r >> 19)) & 0xffffffff
        out.extend(l.to_bytes(4, 'big'))
        out.extend(r.to_bytes(4, 'big'))
    return bytes(out)

def cast(data, key):
    out = bytearray()
    pad = (8 - len(data) % 8) % 8
    data = data + bytes([pad] * (pad if pad > 0 else 8))
    seed = djb(key)
    val = seed
    sub = []
    for i in range(12):
        val = (1103515245 * val + 12345) & 0xffffffff
        sub.append(val)
    for idx in range(0, len(data), 8):
        l = int.from_bytes(data[idx:idx+4], 'big')
        r = int.from_bytes(data[idx+4:idx+8], 'big')
        for round in range(12):
            k = sub[round]
            f = ((r + k) & 0xffffffff) ^ (((r << 5) | (r >> 27)) & 0xffffffff)
            l, r = r, l ^ f
        out.extend(l.to_bytes(4, 'big'))
        out.extend(r.to_bytes(4, 'big'))
    return bytes(out)

def aff(d, k):
    primes = [3, 5, 7, 9, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97]
    idx = (djb(d[:4] if len(d) >= 4 else d + bytes(4)) ^ len(d)) % len(primes)
    scale = primes[idx]
    offset = ((djb(d) >> 3) ^ len(d)) & 0xff
    if offset == 0: offset = 1
    return bytes([4, invert(scale, 256), offset]) + affine(d, scale, offset)

encs = [
    lambda d, k: bytes([0]) + rc(d, k),
    lambda d, k: bytes([1]) + xor(d, k),
    lambda d, k: bytes([2]) + caesar(d, k[0]),
    lambda d, k: bytes([3]) + vigenere(d, k),
    aff,
    lambda d, k: bytes([5]) + atbash(d),
    lambda d, k: bytes([6]) + xtea(d, k),
    lambda d, k: bytes([7]) + speck(d, k),
    lambda d, k: bytes([8]) + simon(d, k),
    lambda d, k: bytes([9]) + rcf(d, k),
    lambda d, k: bytes([10]) + chacha(d, k),
    lambda d, k: bytes([11]) + sps(d, k),
    lambda d, k: bytes([12]) + sis(d, k),
    lambda d, k: bytes([13]) + rcs(d, k),
    lambda d, k: bytes([14]) + blow(d, k),
    lambda d, k: bytes([15]) + des(d, k),
    lambda d, k: bytes([16]) + tea(d, k),
    lambda d, k: bytes([17]) + loki(d, k),
    lambda d, k: bytes([18]) + hight(d, k),
    lambda d, k: bytes([19]) + present(d, k),
    lambda d, k: bytes([20]) + cast(d, k)
]

def pack(val, key):
    data = val.encode('utf-8')
    mode = djb(data) % len(encs)
    payload = encs[mode](data, key)
    return hide(payload)

def extract(toks):
    vars = []
    assigns = []
    i = 1
    n = len(toks)
    while i < n:
        if toks[i].t == 'id':
            name = toks[i].v
            vars.append(name)
            i += 1
            if i < n and toks[i].v == '=':
                i += 1
                init = []
                level = 0
                paren = 0
                bracket = 0
                while i < n:
                    v = toks[i].v
                    if v == '{': level += 1
                    if v == '}': level -= 1
                    if v == '(': paren += 1
                    if v == ')': paren -= 1
                    if v == '[': bracket += 1
                    if v == ']': bracket -= 1
                    if v == ',' and level == 0 and paren == 0 and bracket == 0: break
                    if v == ';' and level == 0 and paren == 0 and bracket == 0: break
                    init.append(toks[i])
                    i += 1
                decl = [token('id', name), token('op', '=')] + init + [token('punc', ';')]
                assigns.append({"kind": "simple", "toks": decl})
            if i < n and toks[i].v == ',':
                i += 1
                continue
            if i < n and toks[i].v == ';': break
        else: i += 1
    return vars, assigns

def gen(used):
    chars = [
        '\u03b1', '\u03b2', '\u03b3', '\u03b4', '\u03b5', '\u03b6',
        '\u03b7', '\u03b8', '\u03b9', '\u03ba', '\u03bb', '\u03bc',
        '\u03bd', '\u03be', '\u03bf', '\u03c0', '\u03c1', '\u03c3',
        '\u03c4', '\u03c5', '\u03c6', '\u03c7', '\u03c8', '\u03c9',
        '\u0430', '\u0435', '\u043e', '\u0440', '\u0441', '\u0445',
        '\u0443', '\u0456', '\u0457'
    ]
    idx = len(used)
    res = chars[idx % len(chars)]
    tmp = idx // len(chars)
    while tmp > 0:
        res += chars[tmp % len(chars)]
        tmp = tmp // len(chars)
    while len(res) < 10:
        res += chars[(len(res) + idx) % len(chars)]
    if res in used:
        i = 0
        while res + str(i) in used: i += 1
        res += str(i)
    return res

exclude = {
    'var', 'let', 'const', 'function', 'return', 'if', 'else', 'for',
    'while', 'do', 'switch', 'case', 'break', 'continue', 'default',
    'try', 'catch', 'finally', 'throw', 'new', 'this', 'typeof',
    'instanceof', 'delete', 'void', 'in', 'of', 'class', 'extends',
    'import', 'export', 'debugger', 'true', 'false', 'null', 'undefined',
    'window', 'document', 'console', 'eval', 'arguments', 'Math', 'JSON',
    'Map', 'Set', 'Promise', 'Object', 'Array', 'String', 'Number',
    'Boolean', 'Error', 'setTimeout', 'setInterval', 'clearTimeout',
    'clearInterval', 'process', 'require', 'module', 'exports', 'atob', 'btoa',
    'log', 'warn', 'error', 'info', 'dir', 'table', 'alert', 'prompt',
    'confirm', 'length', 'push', 'pop', 'shift', 'unshift', 'splice',
    'slice', 'indexOf', 'lastIndexOf', 'join', 'split', 'replace',
    'match', 'test', 'exec', 'toString', 'valueOf', 'constructor',
    'prototype', 'apply', 'call', 'bind', 'name', 'keys', 'values',
    'entries', 'forEach', 'map', 'filter', 'reduce', 'some', 'every',
    'globalThis', 'self', 'charCodeAt', 'fromCharCode',
    'GM_xmlhttpRequest', 'GM_setValue', 'GM_getValue', 'GM_deleteValue',
    'GM_listValues', 'GM_addStyle', 'GM_getResourceText', 'GM_getResourceURL',
    'GM_log', 'GM_openInTab', 'GM_registerMenuCommand', 'GM_unregisterMenuCommand',
    'GM_setClipboard', 'GM_info'
}

def parse(tokens, flag=False):
    pos = 0
    size = len(tokens)
    def peek():
        if pos < size: return tokens[pos]
        return None
    def next():
        nonlocal pos
        t = peek()
        pos += 1
        return t
    def match(val):
        t = peek()
        if t and t.v == val: next(); return True
        return False
    def expr(): return assign()
    def assign():
        left = ternary()
        t = peek()
        if t and t.v in {'=', '+=', '-=', '*=', '/=', '%=', '&=', '|=', '^='}:
            op = next().v
            right = assign()
            return {"kind": "assign", "op": op, "left": left, "right": right}
        return left
    def ternary():
        test = logical()
        if match('?'):
            then = expr()
            match(':')
            els = ternary()
            return {"kind": "ternary", "test": test, "then": then, "else": els}
        return test
    def binary(sub, ops):
        left = sub()
        while True:
            t = peek()
            if t and t.v in ops:
                op = next().v
                right = sub()
                left = {"kind": "binary", "op": op, "left": left, "right": right}
            else: break
        return left
    def logical(): return binary(conjunction, {'||', '??'})
    def conjunction(): return binary(disjunction, {'&&'})
    def disjunction(): return binary(exclusion, {'|'})
    def exclusion(): return binary(intersection, {'^'})
    def intersection(): return binary(equality, {'&'})
    def equality(): return binary(relational, {'==', '!=', '===', '!=='})
    def relational(): return binary(shift, {'<', '>', '<=', '>=', 'instanceof', 'in'})
    def shift(): return binary(additive, {'<<', '>>', '>>>'})
    def additive(): return binary(multiplicative, {'+', '-'})
    def multiplicative(): return binary(unary, {'*', '/', '%', '**'})
    def unary():
        t = peek()
        if t and t.v in {'!', '~', '+', '-', 'typeof', 'void', 'delete', '++', '--', 'new', 'await'}:
            op = next().v
            sub = unary()
            return {"kind": "unary", "op": op, "expr": sub, "prefix": True}
        sub = member()
        t = peek()
        if t and t.v in {'++', '--'}:
            op = next().v
            return {"kind": "unary", "op": op, "expr": sub, "prefix": False}
        return sub
    def member():
        sub = primary()
        while True:
            if match('.'):
                t = next()
                prop = {"kind": "lit", "value": t.v, "type": "str"}
                sub = {"kind": "member", "obj": sub, "prop": prop, "computed": False}
            elif match('['):
                prop = expr()
                match(']')
                sub = {"kind": "member", "obj": sub, "prop": prop, "computed": True}
            elif match('('):
                args = []
                while True:
                    t = peek()
                    if not t or t.v == ')': break
                    args.append(expr())
                    if match(','): continue
                match(')')
                sub = {"kind": "call", "callee": sub, "args": args}
            elif match('?.'):
                t = peek()
                if t and t.v == '[':
                    next()
                    prop = expr()
                    match(']')
                    sub = {"kind": "member", "obj": sub, "prop": prop, "computed": True, "optional": True}
                elif t and t.v == '(':
                    next()
                    args = []
                    while True:
                        t = peek()
                        if not t or t.v == ')': break
                        args.append(expr())
                        if match(','): continue
                    match(')')
                    sub = {"kind": "call", "callee": sub, "args": args, "optional": True}
                elif t and t.t == 'id':
                    t = next()
                    prop = {"kind": "lit", "value": t.v, "type": "str"}
                    sub = {"kind": "member", "obj": sub, "prop": prop, "computed": False, "optional": True}
                else:
                    break
            else: break
        return sub
    def primary():
        t = peek()
        if not t: return None
        if t.t == 'str':
            val = next().v
            q = val[0]
            if q == '`':
                parts = chunk(val)
                if not parts:
                    return {"kind": "lit", "value": "", "type": "str"}
                nodes = []
                for kind, data in parts:
                    if kind == 'static':
                        text = style(data)
                        nodes.append({"kind": "lit", "value": text, "type": "str"})
                    else:
                        toks = scan(data)
                        sub = parse(toks)
                        if sub["kind"] == "block" and sub["body"]:
                            stmt = sub["body"][0]
                            if stmt["kind"] == "exprstmt":
                                nodes.append(stmt["expr"])
                            else:
                                nodes.append(stmt)
                        else:
                            nodes.append(sub)
                node = nodes[0]
                for item in nodes[1:]:
                    node = {
                        "kind": "binary",
                        "op": "+",
                        "left": node,
                        "right": item
                    }
                return node
            s = val[1:-1]
            try:
                s = eval(val)
            except: pass
            return {"kind": "lit", "value": s, "type": "str"}
        if t.t == 'num':
            val = next().v
            try: n = int(val, 0)
            except:
                try: n = float(val)
                except: n = val
            return {"kind": "lit", "value": n, "type": "num"}
        if t.t == 'id':
            val = next().v
            if val == 'true': return {"kind": "lit", "value": True, "type": "bool"}
            if val == 'false': return {"kind": "lit", "value": False, "type": "bool"}
            if val == 'null': return {"kind": "lit", "value": None, "type": "null"}
            if val == 'function':
                nonlocal pos
                pos -= 1
                return func()
            if val == 'async' and peek() and peek().v == 'function':
                next()
                node = func()
                node["async"] = True
                return node
            return {"kind": "id", "value": val}
        if match('('):
            sub = expr()
            match(')')
            return sub
        if match('['):
            elements = []
            while True:
                t = peek()
                if not t or t.v == ']': break
                elements.append(expr())
                if match(','): continue
            match(']')
            return {"kind": "array", "elements": elements}
        if match('{'):
            properties = []
            while True:
                t = peek()
                if not t or t.v == '}': break
                k = next()
                if peek() and peek().v == '(':
                    next()
                    args = []
                    while True:
                        t = peek()
                        if not t or t.v == ')': break
                        if t.t == 'id': args.append(next().v)
                        if t.t != 'id': next()
                        if match(','): continue
                    match(')')
                    body = block()
                    v = {"kind": "func", "name": None, "args": args, "body": body}
                    key = {"kind": "lit", "value": k.v, "type": "str"}
                else:
                    key = {"kind": "lit", "value": k.v, "type": "str"}
                    match(':')
                    v = expr()
                properties.append((key, v))
                if match(','): continue
            match('}')
            return {"kind": "object", "properties": properties}
        return {"kind": "id", "value": next().v}
    def block():
        next()
        body = []
        while True:
            t = peek()
            if not t or t.v == '}': break
            s = stmt()
            if s: body.append(s)
        if peek() and peek().v == '}': next()
        return {"kind": "block", "body": body}
    def cond():
        next()
        match('(')
        test = []
        level = 1
        while True:
            t = next()
            if not t: break
            if t.v == '(': level += 1
            if t.v == ')':
                level -= 1
                if level == 0: break
            test.append(t)
        then = stmt()
        els = None
        if match('else'): els = stmt()
        sub = parse(test, flag=True)
        return {"kind": "cond", "test": sub, "then": then, "else": els}
    def loop():
        next()
        match('(')
        test = []
        level = 1
        while True:
            t = next()
            if not t: break
            if t.v == '(': level += 1
            if t.v == ')':
                level -= 1
                if level == 0: break
            test.append(t)
        body = stmt()
        sub = parse(test, flag=True)
        return {"kind": "loop", "test": sub, "body": body}
    def cycle():
        next()
        match('(')
        toks = []
        level = 1
        while True:
            t = next()
            if not t: break
            if t.v == '(': level += 1
            if t.v == ')':
                level -= 1
                if level == 0: break
            toks.append(t)
        body = stmt()
        return {"kind": "for", "test": toks, "body": body}
    def func():
        next()
        name = None
        t = peek()
        if t and t.t == 'id': name = next().v
        match('(')
        args = []
        while True:
            t = peek()
            if not t or t.v == ')': break
            if t.t == 'id': args.append(next().v)
            if t.t != 'id': next()
            if match(','): continue
        match(')')
        body = block()
        return {"kind": "func", "name": name, "args": args, "body": body}
    def attempt():
        next()
        body = block()
        catch = None
        arg = None
        if match('catch'):
            if match('('):
                t = peek()
                if t and t.t == 'id': arg = next().v
                match(')')
            catch = block()
        fin = None
        if match('finally'): fin = block()
        return {"kind": "try", "body": body, "catch": catch, "arg": arg, "finally": fin}
    def simple():
        toks = []
        level = 0
        while True:
            t = peek()
            if not t: break
            if t.v == '{':
                level += 1
            if t.v == '}':
                if level > 0:
                    level -= 1
                else:
                    if not toks:
                        toks.append(next())
                        continue
                    break
            if t.v == ';' and level == 0:
                toks.append(next())
                break
            if t.v in {'if', 'while', 'for', 'function', 'try', 'return', 'var', 'let', 'const'} and level == 0:
                if not toks:
                    toks.append(next())
                    continue
                break
            toks.append(next())
        return {"kind": "simple", "toks": toks}
    def stmt():
        t = peek()
        if not t: return None
        if t.v == '{': return block()
        if t.v == 'if': return cond()
        if t.v == 'while': return loop()
        if t.v == 'for': return cycle()
        if t.v == 'function': return func()
        if t.v == 'async':
            if pos + 1 < size and tokens[pos + 1].v == 'function':
                next()
                node = func()
                node["async"] = True
                return node
        if t.v == 'try': return attempt()
        if t.v == 'return':
            next()
            val = None
            if not match(';'):
                val = expr()
                match(';')
            return {"kind": "ret", "value": val}
        if t.v == 'throw':
            next()
            val = expr()
            match(';')
            return {"kind": "throw", "value": val}
        if t.v in {'var', 'let', 'const'}: return simple()
        val = expr()
        match(';')
        return {"kind": "exprstmt", "expr": val}
    if flag:
        return expr()
    body = []
    while True:
        s = stmt()
        if not s: break
        body.append(s)
    return {"kind": "block", "body": body}

def emit(node):
    if not node: return []
    if isinstance(node, list):
        res = []
        for x in node: res.extend(emit(x))
        return res
    kind = node["kind"]
    if kind == "template": return [token('str', node["value"])]
    if kind == "id": return [token('id', node["value"])]
    if kind == "lit":
        val = node["value"]
        t = node["type"]
        if t == "str":
            escaped = repr(val)
            if escaped.startswith('"') or escaped.startswith("'"): return [token('str', escaped)]
            return [token('str', f"'{val}'")]
        if t == "num": return [token('num', str(val))]
        if t == "bool": return [token('id', 'true' if val else 'false')]
        if t == "null": return [token('id', 'null')]
        return [token('id', str(val))]
    if kind == "binary": return emit(node["left"]) + [token('op', node["op"])] + emit(node["right"])
    if kind == "unary":
        toks = emit(node["expr"])
        if node["expr"] and node["expr"]["kind"] in {"binary", "assign", "ternary"}:
            toks = [token('punc', '(')] + toks + [token('punc', ')')]
        if node["prefix"]: return [token('op', node["op"])] + toks
        return toks + [token('op', node["op"])]
    if kind == "call":
        args = []
        for i, a in enumerate(node["args"]):
            args.extend(emit(a))
            if i < len(node["args"]) - 1: args.append(token('punc', ','))
        callee = emit(node["callee"])
        if node["callee"] and node["callee"]["kind"] == "func":
            callee = [token('punc', '(')] + callee + [token('punc', ')')]
        opt = [token('op', '?.')] if node.get("optional") else []
        return callee + opt + [token('punc', '(')] + args + [token('punc', ')')]
    if kind == "member":
        if node["computed"]:
            opt = [token('op', '?.')] if node.get("optional") else []
            return emit(node["obj"]) + opt + [token('punc', '[')] + emit(node["prop"]) + [token('punc', ']')]
        pv = node["prop"].get("value") if isinstance(node["prop"], dict) else None
        if node.get("optional"):
            return emit(node["obj"]) + [token('op', '?.')] + (emit(node["prop"]) if pv is None else [token('id', pv)])
        return emit(node["obj"]) + [token('punc', '.')] + (emit(node["prop"]) if pv is None else [token('id', pv)])
    if kind == "assign": return emit(node["left"]) + [token('op', node["op"])] + emit(node["right"])
    if kind == "ternary": return emit(node["test"]) + [token('op', '?')] + emit(node["then"]) + [token('op', ':')] + emit(node["else"])
    if kind == "array":
        elements = []
        for i, el in enumerate(node["elements"]):
            elements.extend(emit(el))
            if i < len(node["elements"]) - 1: elements.append(token('punc', ','))
        return [token('punc', '[')] + elements + [token('punc', ']')]
    if kind == "object":
        props = []
        for i, (k, v) in enumerate(node["properties"]):
            toks = emit(k)
            if k["kind"] not in {"lit", "id"}:
                toks = [token('punc', '[')] + toks + [token('punc', ']')]
            props.extend(toks)
            props.append(token('punc', ':'))
            props.extend(emit(v))
            if i < len(node["properties"]) - 1: props.append(token('punc', ','))
        return [token('punc', '{')] + props + [token('punc', '}')]
    if kind == "simple": return node["toks"]
    if kind == "exprstmt": return emit(node["expr"]) + [token('punc', ';')]
    if kind == "block":
        toks = [token('punc', '{')]
        for s in node["body"]: toks.extend(emit(s))
        toks.append(token('punc', '}'))
        return toks
    if kind == "cond":
        toks = [token('id', 'if'), token('punc', '(')] + emit(node["test"]) + [token('punc', ')')]
        toks.extend(emit(node["then"]))
        if node["else"]:
            toks.append(token('id', 'else'))
            toks.extend(emit(node["else"]))
        return toks
    if kind == "loop": return [token('id', 'while'), token('punc', '(')] + emit(node["test"]) + [token('punc', ')')] + emit(node["body"])
    if kind == "for": return [token('id', 'for'), token('punc', '(')] + node["test"] + [token('punc', ')')] + emit(node["body"])
    if kind == "func":
        args = []
        for i, a in enumerate(node["args"]):
            args.append(token('id', a))
            if i < len(node["args"]) - 1: args.append(token('punc', ','))
        name = [token('id', node["name"])] if node["name"] else []
        prefix = [token('id', 'async')] if node.get("async") else []
        return prefix + [token('id', 'function')] + name + [token('punc', '(')] + args + [token('punc', ')')] + emit(node["body"])
    if kind == "try":
        toks = [token('id', 'try')] + emit(node["body"])
        if node["catch"]:
            catch = [token('punc', '('), token('id', node["arg"]), token('punc', ')')] if node["arg"] else []
            toks += [token('id', 'catch')] + catch + emit(node["catch"])
        if node["finally"]: toks += [token('id', 'finally')] + emit(node["finally"])
        return toks
    if kind == "ret":
        val = emit(node["value"]) if node["value"] else []
        return [token('id', 'return')] + val + [token('punc', ';')]
    if kind == "throw":
        val = emit(node["value"])
        return [token('id', 'throw')] + val + [token('punc', ';')]
    return []

def inspect(node, fn):
    if not node: return
    if isinstance(node, list):
        for x in node: inspect(x, fn)
    elif isinstance(node, dict):
        if fn(node) is False: return
        for v in node.values(): inspect(v, fn)

def find(node):
    names = set()
    def fn(n):
        if n.get("kind") == "simple":
            t = n.get("toks")
            if t and t[0].v in {'var', 'let', 'const'}:
                v, _ = extract(t)
                names.update(v)
        if n.get("kind") == "func":
            if n.get("name"): names.add(n["name"])
    inspect(node, fn)
    return names

def local(node):
    names = set()
    def fn(n):
        if n.get("kind") == "simple":
            t = n.get("toks")
            if t and t[0].v in {'var', 'let', 'const'}:
                v, _ = extract(t)
                names.update(v)
        if n.get("kind") == "func":
            return False
    inspect(node, fn)
    return names

def rename(node, env):
    if not node: return None
    if isinstance(node, list): return [rename(x, env) for x in node]
    if isinstance(node, token):
        if node.t == 'id' and node.v in env: return token('id', env[node.v])
        return node
    kind = node["kind"]
    if kind == "id":
        val = node["value"]
        if val in env: return {"kind": "id", "value": env[val]}
        globals = {'console', 'Math', 'window', 'document', 'process', 'global', 'atob', 'btoa', 'setInterval', 'setTimeout', 'clearInterval', 'clearTimeout', 'eval', 'JSON', 'Object', 'Array', 'String', 'Number', 'Boolean', 'Error', 'Promise', 'Map', 'Set', 'Function'}
        if val in globals:
            return {
                "kind": "member",
                "obj": {"kind": "id", "value": "globalThis"},
                "prop": {"kind": "lit", "value": val, "type": "str"},
                "computed": True
            }
        return node
    if kind == "lit": return node
    if kind == "binary":
        return {
            "kind": "binary",
            "op": node["op"],
            "left": rename(node["left"], env),
            "right": rename(node["right"], env)
        }
    if kind == "unary":
        return {
            "kind": "unary",
            "op": node["op"],
            "expr": rename(node["expr"], env),
            "prefix": node["prefix"]
        }
    if kind == "call":
        callee = rename(node["callee"], env)
        args = [rename(a, env) for a in node["args"]]
        return {"kind": "call", "callee": callee, "args": args, "optional": node.get("optional", False)}
    if kind == "member":
        obj = rename(node["obj"], env)
        prop = rename(node["prop"], env)
        return {"kind": "member", "obj": obj, "prop": prop, "computed": node["computed"], "optional": node.get("optional", False)}
    if kind == "assign":
        left = rename(node["left"], env)
        right = rename(node["right"], env)
        return {"kind": "assign", "op": node["op"], "left": left, "right": right}
    if kind == "ternary":
        test = rename(node["test"], env)
        then = rename(node["then"], env)
        els = rename(node["else"], env)
        return {"kind": "ternary", "test": test, "then": then, "else": els}
    if kind == "array":
        elements = [rename(el, env) for el in node["elements"]]
        return {"kind": "array", "elements": elements}
    if kind == "object":
        properties = []
        for k, v in node["properties"]: properties.append((rename(k, env), rename(v, env)))
        return {"kind": "object", "properties": properties}
    if kind == "simple": return {"kind": "simple", "toks": rename(node["toks"], env)}
    if kind == "exprstmt": return {"kind": "exprstmt", "expr": rename(node["expr"], env)}
    if kind == "block":
        body = [rename(s, env) for s in node["body"]]
        return {"kind": "block", "body": body}
    if kind == "cond":
        test = rename(node["test"], env)
        then = rename(node["then"], env)
        els = rename(node["else"], env) if node["else"] else None
        return {"kind": "cond", "test": test, "then": then, "else": els}
    if kind == "loop":
        test = rename(node["test"], env)
        body = rename(node["body"], env)
        return {"kind": "loop", "test": test, "body": body}
    if kind == "for":
        test = rename(node["test"], env)
        body = rename(node["body"], env)
        return {"kind": "for", "test": test, "body": body}
    if kind == "func":
        name = env[node["name"]] if node["name"] in env else node["name"]
        child = env.copy()
        locals = find(node["body"])
        params = node["args"]
        for p in params:
            if p not in exclude:
                sym = gen(child.values())
                child[p] = sym
        for l in locals:
            if l not in exclude:
                sym = gen(child.values())
                child[l] = sym
        args = [child[p] if p in child else p for p in params]
        body = rename(node["body"], child)
        return {"kind": "func", "name": name, "args": args, "body": body, "async": node.get("async")}
    if kind == "try":
        body = rename(node["body"], env)
        catch = None
        arg = node["arg"]
        if node["catch"]:
            child = env.copy()
            if arg and arg not in exclude:
                sym = gen(child.values())
                child[arg] = sym
                arg = sym
            catch = rename(node["catch"], child)
        fin = rename(node["finally"], env) if node["finally"] else None
        return {"kind": "try", "body": body, "catch": catch, "arg": arg, "finally": fin}
    if kind == "ret":
        val = rename(node["value"], env) if node["value"] else None
        return {"kind": "ret", "value": val}
    if kind == "throw":
        val = rename(node["value"], env)
        return {"kind": "throw", "value": val}
    return node

def split(stmt):
    if stmt["kind"] == "block": return stmt["body"]
    return [stmt]

def walk(node, fn):
    if not node: return node
    if isinstance(node, list): return [walk(x, fn) for x in node]
    if isinstance(node, dict):
        node = fn(node)
        if not isinstance(node, dict): return node
        res = {}
        for k, v in node.items():
            res[k] = walk(v, fn)
        return res
    return node

def keys(node):
    def fn(n):
        if n.get("kind") == "object":
            props = []
            for k, v in n["properties"]:
                new = k
                if k.get("kind") == "id":
                    new = {"kind": "lit", "value": k["value"], "type": "str"}
                props.append((keys(new), keys(v)))
            return {"kind": "object", "properties": props}
        return n
    return walk(node, fn)

def logic(node):
    def mark(t):
        if isinstance(t, dict):
            t["logiced"] = True
            for k, v in t.items(): mark(v)
        elif isinstance(t, list):
            for x in t: mark(x)
        return t
    def fn(n):
        if n.get("logiced"): return n
        if n.get("kind") == "binary":
            op = n["op"]
            left = n["left"]
            right = n["right"]
            if op == "&&":
                return mark({
                    "kind": "unary", "op": "!", "prefix": True,
                    "expr": {
                        "kind": "binary", "op": "||",
                        "left": {"kind": "unary", "op": "!", "expr": left, "prefix": True},
                        "right": {"kind": "unary", "op": "!", "expr": right, "prefix": True}
                    }
                })
            if op == "||":
                return mark({
                    "kind": "unary", "op": "!", "prefix": True,
                    "expr": {
                        "kind": "binary", "op": "&&",
                        "left": {"kind": "unary", "op": "!", "expr": left, "prefix": True},
                        "right": {"kind": "unary", "op": "!", "expr": right, "prefix": True}
                    }
                })
            if op == "===":
                return mark({
                    "kind": "unary", "op": "!", "prefix": True,
                    "expr": {"kind": "binary", "op": "!==", "left": left, "right": right}
                })
            if op == "!==":
                return mark({
                    "kind": "unary", "op": "!", "prefix": True,
                    "expr": {"kind": "binary", "op": "===", "left": left, "right": right}
                })
            if op == "<":
                return mark({
                    "kind": "unary", "op": "!", "prefix": True,
                    "expr": {"kind": "binary", "op": ">=", "left": left, "right": right}
                })
            if op == ">":
                return mark({
                    "kind": "unary", "op": "!", "prefix": True,
                    "expr": {"kind": "binary", "op": "<=", "left": left, "right": right}
                })
            if op == "<=":
                return mark({
                    "kind": "unary", "op": "!", "prefix": True,
                    "expr": {"kind": "binary", "op": ">", "left": left, "right": right}
                })
            if op == ">=":
                return mark({
                    "kind": "unary", "op": "!", "prefix": True,
                    "expr": {"kind": "binary", "op": "<", "left": left, "right": right}
                })
        return n
    return walk(node, fn)

def params(node):
    def fn(n):
        if n.get("kind") == "func":
            body = params(n["body"])
            names = n["args"]
            if names:
                toks = [token('id', 'var')]
                for i, name in enumerate(names):
                    toks.extend([
                        token('id', name), token('op', '='),
                        token('id', 'arguments'), token('punc', '['),
                        token('num', hex(i)), token('punc', ']')
                    ])
                    if i < len(names) - 1: toks.append(token('punc', ','))
                toks.append(token('punc', ';'))
                decl = {"kind": "simple", "toks": toks}
                body["body"] = [decl] + body["body"]
            return {"kind": "func", "name": n["name"], "args": [], "body": body, "async": n.get("async")}
        return n
    return walk(node, fn)

def flat(node):
    if node is None: return None
    if isinstance(node, list):
        children = [flat(s) for s in node]
        vars = []
        lines = []
        for s in children:
            if s["kind"] == "simple" and s["toks"] and s["toks"][0].v in {'var', 'let', 'const'}:
                v, a = extract(s["toks"])
                vars.extend(v)
                lines.extend(a)
            if s["kind"] != "simple" or not s["toks"] or s["toks"][0].v not in {'var', 'let', 'const'}:
                lines.extend(split(s))
        states = []
        while len(states) < len(lines) + 1:
            val = str(random.randint(10000, 99999))
            if val not in states: states.append(val)
        used = set()
        s = gen(used)
        used.add(s)
        t = gen(used)
        used.add(t)
        key = random.randint(1000, 9999)
        decl = [token('id', 'var')]
        all = vars + [s, t]
        for i, v in enumerate(all):
            decl.append(token('id', v))
            if i < len(all) - 1: decl.append(token('punc', ','))
        decl.append(token('punc', ';'))
        init = [
            token('id', s), token('op', '='), token('num', str(int(states[0]) ^ key)), token('punc', ','),
            token('id', t), token('op', '='), token('num', str(key)), token('punc', ';')
        ]
        part = []
        for i in range(len(lines)):
            stmt = lines[i]
            toks = emit(stmt)
            nxt = states[i+1]
            new = random.randint(1000, 9999)
            val = int(nxt) ^ new
            move = [
                token('id', s), token('op', '='), token('num', str(val)), token('punc', ','),
                token('id', t), token('op', '='), token('num', str(new)), token('punc', ';'),
                token('id', 'break'), token('punc', ';')
            ]
            block = [
                token('id', 'case'), token('num', states[i]), token('punc', ':')
            ] + toks + move
            part.append(block)
        fakes = []
        while len(fakes) < 5:
            val = str(random.randint(10000, 99999))
            if val not in states and val not in fakes: fakes.append(val)
        trash = []
        for idx, state in enumerate(fakes):
            raw = dead(idx)
            toks = scan(raw)
            goto = str(random.randint(10000, 99999))
            new = random.randint(1000, 9999)
            val = int(goto) ^ new
            move = [
                token('id', s), token('op', '='), token('num', str(val)), token('punc', ','),
                token('id', t), token('op', '='), token('num', str(new)), token('punc', ';'),
                token('id', 'break'), token('punc', ';')
            ]
            block = [
                token('id', 'case'), token('num', state), token('punc', ':')
            ] + toks + move
            trash.append(block)
        other = [
            token('id', 'default'), token('punc', ':'),
            token('id', s), token('op', '='), token('num', str(int(states[-1]) ^ key)), token('punc', ','),
            token('id', t), token('op', '='), token('num', str(key)), token('punc', ';'),
            token('id', 'break'), token('punc', ';')
        ]
        cases = part + trash + [other]
        random.shuffle(cases)
        code = []
        for c in cases: code.extend(c)
        loop = [
            token('id', 'while'), token('punc', '('),
            token('punc', '('), token('id', s), token('op', '^'), token('id', t), token('punc', ')'),
            token('op', '!=='), token('num', states[-1]), token('punc', ')'),
            token('punc', '{'),
            token('id', 'switch'), token('punc', '('),
            token('id', s), token('op', '^'), token('id', t),
            token('punc', ')'), token('punc', '{')
        ] + code + [
            token('punc', '}'),
            token('punc', '}')
        ]
        return [
            {"kind": "simple", "toks": decl},
            {"kind": "simple", "toks": init},
            {"kind": "simple", "toks": loop}
        ]
    def fn(n):
        k = n.get("kind")
        if k in {"block", "cond", "loop", "for", "func", "try"}:
            res = {}
            for key, val in n.items():
                res[key] = val
                if key in {"body", "then", "else", "catch", "finally"}: res[key] = flat(val)
            return res
        return n
    return walk(node, fn)

def p(v): return token('punc', v)
def o(v): return token('op', v)
def n(v): return token('num', v)

def plus(a, b):
    return [
        p('('), p('('), a, o('^'), b, p(')'), o('+'), n('0x2'), o('*'), p('('), a, o('&'), b, p(')'), p(')'), o('&'), n('0xffffffff'), o('|'), p('('), p('('), a, o('|'), b, p(')'), o('+'), p('('), a, o('&'), b, p(')'), p(')'), o('&'), n('0x0')
    ]

def minus(a, b):
    return [
        p('('), a, o('^'), o('~'), b, p(')'), o('-'), n('0x2'), o('*'), p('('), o('~'), a, o('&'), b, p(')'), o('-'), n('0x1')
    ]

def gate(a, b):
    return [
        p('('), a, o('|'), b, p(')'), o('-'), p('('), a, o('&'), b, p(')')
    ]

def fuse(a, b):
    return [
        p('('), a, o('|'), b, p(')'), o('-'), p('('), a, o('^'), b, p(')')
    ]

def mesh(a, b):
    return [
        p('('), a, o('&'), b, p(')'), o('+'), p('('), a, o('^'), b, p(')')
    ]

def mba(node):
    def look(n):
        if not n: return False
        if isinstance(n, dict):
            k = n.get("kind")
            if k == "lit" and n.get("type") == "str": return True
            if k == "call" and n.get("callee", {}).get("kind") == "id" and n.get("callee", {}).get("value") == "_0xdec": return True
            if k == "binary" and n.get("op") == "+":
                return look(n.get("left")) or look(n.get("right"))
        return False
    if not node: return None
    if isinstance(node, list):
        res = []
        n = len(node)
        i = 0
        while i < n:
            if i + 2 < n:
                left = node[i]
                op = node[i+1]
                right = node[i+2]
                if (left.t in {'id', 'num'} and left.v not in exclude) and (op.t == 'op' and op.v in {'+', '-', '^', '&', '|'}) and (right.t in {'id', 'num'} and right.v not in exclude):
                    if i > 0 and node[i-1].v in {'.', '?.'}:
                        pass
                    else:
                        ops = {'+': plus, '-': minus, '^': gate, '&': fuse, '|': mesh}
                        if op.v in ops:
                            res.extend(ops[op.v](left, right))
                            i += 3
                            continue
            res.append(node[i])
            i += 1
        return res
    def fn(n):
        if n.get("mba"): return n
        if n.get("kind") == "binary":
            left = mba(n["left"])
            right = mba(n["right"])
            op = n["op"]
            if op == '+':
                if look(left) or look(right):
                    return {"kind": "binary", "op": "+", "left": left, "right": right, "mba": True}
                return {
                    "kind": "binary", "op": "+", "mba": True,
                    "left": {"kind": "binary", "op": "^", "left": left, "right": right, "mba": True},
                    "right": {"kind": "binary", "op": "*", "left": {"kind": "lit", "value": 2, "type": "num"}, "right": {"kind": "binary", "op": "&", "left": left, "right": right, "mba": True}, "mba": True}
                }
            if op == '-':
                nr = {"kind": "unary", "op": "~", "expr": right, "prefix": True}
                nl = {"kind": "unary", "op": "~", "expr": left, "prefix": True}
                xor = {"kind": "binary", "op": "^", "left": left, "right": nr, "mba": True}
                val = {"kind": "binary", "op": "&", "left": nl, "right": right, "mba": True}
                mul = {"kind": "binary", "op": "*", "left": {"kind": "lit", "value": 2, "type": "num"}, "right": val, "mba": True}
                sub = {"kind": "binary", "op": "-", "left": xor, "right": mul, "mba": True}
                return {"kind": "binary", "op": "-", "left": sub, "right": {"kind": "lit", "value": 1, "type": "num"}, "mba": True}
            if op == '^':
                o = {"kind": "binary", "op": "|", "left": left, "right": right, "mba": True}
                val = {"kind": "binary", "op": "&", "left": left, "right": right, "mba": True}
                return {"kind": "binary", "op": "-", "left": o, "right": val, "mba": True}
            if op == '&':
                o = {"kind": "binary", "op": "|", "left": left, "right": right, "mba": True}
                xor = {"kind": "binary", "op": "^", "left": left, "right": right, "mba": True}
                return {"kind": "binary", "op": "-", "left": o, "right": xor, "mba": True}
            if op == '|':
                val = {"kind": "binary", "op": "&", "left": left, "right": right, "mba": True}
                xor = {"kind": "binary", "op": "^", "left": left, "right": right, "mba": True}
                return {"kind": "binary", "op": "+", "left": val, "right": xor, "mba": True}
            return {"kind": "binary", "op": op, "left": left, "right": right}
        return n
    return walk(node, fn)

def fuck(val):
    if isinstance(val, bool):
        if val: return {"kind": "unary", "op": "!", "expr": {"kind": "array", "elements": []}, "prefix": True}
        return {"kind": "unary", "op": "!", "expr": {"kind": "unary", "op": "!", "expr": {"kind": "array", "elements": []}, "prefix": True}, "prefix": True}
    if isinstance(val, int):
        if val < 0:
            sub = fuck(-val)
            return {"kind": "unary", "op": "-", "expr": sub, "prefix": True}
        if val == 0: return {"kind": "unary", "op": "+", "expr": {"kind": "array", "elements": []}, "prefix": True}
        def jsf(n):
            if n == 0: return {"kind": "unary", "op": "+", "expr": {"kind": "array", "elements": []}, "prefix": True}
            term = {"kind": "unary", "op": "!", "expr": {"kind": "array", "elements": []}, "prefix": True}
            term = {"kind": "unary", "op": "!", "expr": term, "prefix": True}
            expr = term
            for _ in range(n - 1): expr = {"kind": "binary", "op": "+", "left": expr, "right": term}
            return {"kind": "unary", "op": "+", "expr": expr, "prefix": True}
        if val < 10:
            return jsf(val)
        def raw(num):
            digits = [int(c) for c in str(num)]
            parts = []
            for d in digits:
                parts.append({"kind": "array", "elements": [jsf(d)]})
            expr = parts[0]
            for i in range(1, len(parts)): expr = {"kind": "binary", "op": "+", "left": expr, "right": parts[i]}
            return {"kind": "unary", "op": "+", "expr": expr, "prefix": True}
        x1 = random.randint(5, 50)
        y1 = val ^ x1
        xp = {"kind": "binary", "op": "^", "left": raw(x1), "right": raw(y1)}
        x2 = random.randint(5, val - 1 if val > 5 else 5)
        y2 = val - x2
        ap = {"kind": "binary", "op": "+", "left": raw(x2), "right": raw(y2)}
        pos = -~val
        ip = {"kind": "unary", "op": "~", "expr": {"kind": "unary", "op": "-", "expr": raw(pos), "prefix": True}, "prefix": True}
        return {
            "kind": "binary", "op": "^",
            "left": {"kind": "binary", "op": "&", "left": xp, "right": ap},
            "right": {"kind": "binary", "op": "&", "left": ip, "right": {"kind": "lit", "value": 0, "type": "num"}}
        }
    return None

def css(val):
    stash = []
    def rep(m):
        stash.append(m.group(0))
        return f"__STASH_{len(stash)-1}__"
    val = re.sub(r'\$\{[^\}]+\}', rep, val)
    val = re.sub(r'/\*.*?\*/', '', val, flags=re.DOTALL)
    val = re.sub(r'\s*([\{\}:;,])\s*', r'\1', val)
    val = re.sub(r'\s+', ' ', val)
    for i, orig in enumerate(stash):
        val = val.replace(f"__STASH_{i}__", orig)
    return val.strip()

def clean(val):
    val = re.sub(r'(?<!:)\/\/.*$', '', val, flags=re.MULTILINE)
    val = re.sub(r'/\*.*?\*/', '', val, flags=re.DOTALL)
    return val

def style(val):
    if ('{' in val and '}' in val and ':' in val) or any(k in val for k in ['const ', 'let ', 'var ', 'function', 'return ', 'console.']):
        val = clean(val)
        if '{' in val and '}' in val and ':' in val:
            val = css(val)
    return val

def core(val):
    if not isinstance(val, str): return False
    if val.startswith("http://") or val.startswith("https://"): return True
    if len(val) == 32 and all(c in "0123456789abcdefABCDEF" for c in val): return True
    if "cdnjs" in val or "github" in val or "raw_url" in val: return True
    return False

def secure(val):
    east = random.randint(10, 250)
    west = random.randint(10, 250)
    north = random.randint(10, 250)
    head = ((east * 3 + 123) ^ 0x55) & 255
    tail = ((west ^ 0xaa) + 456) & 255
    leaf = ((north + 789) ^ 0xff) & 255
    key = (head ^ tail ^ leaf) & 0xff
    salt = random.randint(1, 0xfe)
    enc = [(ord(c) ^ key ^ ((i * salt + (i >> 2)) & 0xff)) & 0xff for i, c in enumerate(val)]
    data = ",".join(map(str, enc))
    js = f"""(function(){{
        var head = (({east} * 3 + 123) ^ 0x55) & 255;
        var tail = ((({west} ^ 0xaa) + 456) & 255);
        var leaf = (({north} + 789) ^ 0xff) & 255;
        var k = (head ^ tail ^ leaf) & 255;
        var salt = {salt};
        var enc = [{data}];
        var res = "";
        for (var i = 0; i < enc.length; i++) {{
            res += String.fromCharCode(enc[i] ^ k ^ ((i * salt + (i >> 2)) & 255));
        }}
        return res;
    }})()"""
    toks = scan(js)
    ast = parse(toks)
    return ast["body"][0]["expr"]

def pool(node, strings, key):
    if not node: return None
    if isinstance(node, list):
        res = []
        n = len(node)
        i = 0
        while i < n:
            tok = node[i]
            flag = False
            if i > 0 and node[i-1].t == 'id' and node[i-1].v == 'import': flag = True
            if i > 1 and node[i-2].t == 'id' and node[i-2].v == 'require': flag = True
            if tok.t == 'str' and not flag:
                raw = tok.v
                q = raw[0]
                if q == '`':
                    if '${' not in raw:
                        val = raw[1:-1]
                        val = style(val)
                        if core(val):
                            ast = secure(val)
                            dt = emit(ast)
                            ok = i > 0 and node[i-1].v in {"{", ","}
                            if i + 1 < n and node[i+1].v == ':' and ok:
                                res.extend([token('punc', '[')] + dt + [token('punc', ']')])
                            else:
                                res.extend(dt)
                        else:
                            mode = djb(val.encode('utf-8')) % len(encs)
                            payload = encs[mode](val.encode('utf-8'), key)
                            b64 = hide(payload)
                            if b64 not in strings: strings.append(b64)
                            idx = strings.index(b64)
                            args = ",".join([hex(ord(c)) for c in f"return _0xdec({hex(idx)})"])
                            code = f"globalThis.Function('_0xdec', String.fromCharCode({args}))(globalThis._0xdec)"
                            dt = scan(code)
                            ok = i > 0 and node[i-1].v in {"{", ","}
                            if i + 1 < n and node[i+1].v == ':' and ok:
                                res.extend([token('punc', '[')] + dt + [token('punc', ']')])
                            else:
                                res.extend(dt)
                    else:
                        val = raw[1:-1]
                        val = style(val)
                        res.append(token('str', q + val + q))
                    i += 1
                    continue
                val = raw[1:-1]
                try:
                    val = eval(raw)
                except: pass
                val = style(val)
                if core(val):
                    ast = secure(val)
                    dt = emit(ast)
                    ok = i > 0 and node[i-1].v in {"{", ","}
                    if i + 1 < n and node[i+1].v == ':' and ok:
                        res.extend([token('punc', '[')] + dt + [token('punc', ']')])
                    else:
                        res.extend(dt)
                else:
                    mode = djb(val.encode('utf-8')) % len(encs)
                    payload = encs[mode](val.encode('utf-8'), key)
                    b64 = hide(payload)
                    if b64 not in strings: strings.append(b64)
                    idx = strings.index(b64)
                    args = ",".join([hex(ord(c)) for c in f"return _0xdec({hex(idx)})"])
                    code = f"globalThis.Function('_0xdec', String.fromCharCode({args}))(globalThis._0xdec)"
                    dt = scan(code)
                    ok = i > 0 and node[i-1].v in {"{", ","}
                    if i + 1 < n and node[i+1].v == ':' and ok:
                        res.extend([token('punc', '[')] + dt + [token('punc', ']')])
                    else:
                        res.extend(dt)
            if tok.t != 'str' or flag: res.append(tok)
            i += 1
        return res
    def fn(n):
        if n.get("kind") == "lit":
            if n["type"] == "str":
                val = n["value"]
                val = style(val)
                if core(val):
                    return secure(val)
                mode = djb(val.encode('utf-8')) % len(encs)
                payload = encs[mode](val.encode('utf-8'), key)
                b64 = hide(payload)
                if b64 not in strings: strings.append(b64)
                idx = strings.index(b64)
                args = ",".join([hex(ord(c)) for c in f"return _0xdec({hex(idx)})"])
                code = f"globalThis.Function('_0xdec', String.fromCharCode({args}))(globalThis._0xdec)"
                toks = scan(code)
                return {"kind": "simple", "toks": toks}
        if n.get("kind") == "template":
            raw = n["value"]
            if '${' not in raw:
                val = raw[1:-1] if (len(raw) >= 2 and raw[0] in {"'", '"', '`'} and raw[-1] == raw[0]) else raw
                val = style(val)
                if core(val):
                    return secure(val)
                mode = djb(val.encode('utf-8')) % len(encs)
                payload = encs[mode](val.encode('utf-8'), key)
                b64 = hide(payload)
                if b64 not in strings: strings.append(b64)
                idx = strings.index(b64)
                args = ",".join([hex(ord(c)) for c in f"return _0xdec({hex(idx)})"])
                code = f"globalThis.Function('_0xdec', String.fromCharCode({args}))(globalThis._0xdec)"
                toks = scan(code)
                return {"kind": "simple", "toks": toks}
            else:
                q = raw[0] if raw[0] in {"'", '"', '`'} else "'"
                val = raw[1:-1] if (len(raw) >= 2 and raw[0] in {"'", '"', '`'} and raw[-1] == raw[0]) else raw
                val = style(val)
                return {"kind": "template", "value": q + val + q}
        return n
    return walk(node, fn)

def prop(node):
    if not node: return None
    if isinstance(node, list):
        res = []
        n = len(node)
        i = 0
        while i < n:
            if i + 2 < n and node[i].t == 'id' and node[i+1].v == '.' and node[i+2].t == 'id':
                res.extend([node[i], token('punc', '['), token('str', "'" + node[i+2].v + "'"), token('punc', ']')])
                i += 3
            if i + 2 >= n or node[i].t != 'id' or node[i+1].v != '.' or node[i+2].t != 'id':
                res.append(node[i])
                i += 1
        return res
    def fn(n):
        if n.get("kind") == "member":
            if not n["computed"]:
                return {"kind": "member", "obj": n["obj"], "prop": n["prop"], "computed": True, "optional": n.get("optional", False)}
        return n
    return walk(node, fn)

def mask(n):
    y = random.randint(1, 100)
    z = random.randint(1, 0xff)
    return [
        token('punc', '('),
        token('punc', '('),
        token('punc', '('), token('num', hex(n ^ y)), token('op', '^'), token('num', hex(y)), token('punc', ')'),
        token('op', '+'),
        token('punc', '('), token('num', hex(n + z)), token('op', '-'), token('num', hex(z)), token('punc', ')'),
        token('op', '>>'), token('num', '1'),
        token('punc', ')'),
        token('punc', ')')
    ]

def nums(node):
    if not node: return None
    if isinstance(node, list):
        res = []
        for tok in node:
            if tok.t == 'num':
                val = tok.v
                try:
                    if '.' not in val and 'e' not in val.lower():
                        num = int(val, 0)
                        if num > 10:
                            a = random.randint(1, num - 1)
                            b = num - a
                            res.extend([token('punc', '('), token('num', hex(a)), token('op', '+'), token('num', hex(b)), token('punc', ')')])
                        if num <= 10: res.extend(mask(num))
                    if '.' in val or 'e' in val.lower(): res.append(tok)
                except: res.append(tok)
            if tok.t != 'num': res.append(tok)
        return res
    def fn(n):
        if n.get("seen"): return n
        if n.get("kind") == "lit":
            if n["type"] == "num":
                val = n["value"]
                if isinstance(val, int) and not isinstance(val, bool):
                    y = random.randint(1, 100)
                    z = random.randint(1, 0xff)
                    def mark(t):
                        if isinstance(t, dict):
                            t["seen"] = True
                            for k, v in t.items(): mark(v)
                        elif isinstance(t, list):
                            for x in t: mark(x)
                        return t
                    a = {"kind": "binary", "op": "^", "left": {"kind": "lit", "value": val ^ y, "type": "num"}, "right": {"kind": "lit", "value": y, "type": "num"}}
                    b = {"kind": "binary", "op": "-", "left": {"kind": "lit", "value": val + z, "type": "num"}, "right": {"kind": "lit", "value": z, "type": "num"}}
                    res = {
                        "kind": "binary", "op": "&",
                        "left": {"kind": "binary", "op": "|", "left": a, "right": b},
                        "right": {"kind": "binary", "op": "|", "left": b, "right": a}
                    }
                    return mark(res)
        return n
    return walk(node, fn)

def prime(n):
    if n < 2: return False
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0: return False
    return True

def fib(n):
    a, b = 0, 1
    for _ in range(n): a, b = b, a + b
    return a

def arm(n):
    s = str(n)
    k = len(s)
    return sum(int(i)**k for i in s) == n

def pure(n):
    if n < 2: return False
    s = 1
    for i in range(2, int(n**0.5) + 1):
        if n % i == 0:
            s += i
            if i * i != n: s += n // i
    return s == n

def bubble():
    return """
    function bubble(arr) {
        var n = arr.length;
        for (var i = 0; i < n-1; i++) {
            for (var j = 0; j < n-i-1; j++) {
                if (arr[j] > arr[j+1]) {
                    var temp = arr[j]; arr[j] = arr[j+1]; arr[j+1] = temp;
                }
            }
        }
        return arr;
    }
    var sorted = bubble([64, 34, 25, 12, 22, 11, 90]);
    """

def quick():
    return """
    function quick(arr) {
        if (arr.length <= 1) return arr;
        var pivot = arr[0]; var left = []; var right = [];
        for (var i = 1; i < arr.length; i++) {
            if (arr[i] < pivot) left.push(arr[i]);
            if (arr[i] >= pivot) right.push(arr[i]);
        }
        return quick(left).concat(pivot, quick(right));
    }
    var sorted = quick([10, 7, 8, 9, 1, 5]);
    """

def rank():
    return """
    function rank(arr) {
        var n = arr.length;
        for (var i = 1; i < n; i++) {
            var key = arr[i]; var j = i - 1;
            while (j >= 0 && arr[j] > key) {
                arr[j + 1] = arr[j]; j = j - 1;
            }
            arr[j + 1] = key;
        }
        return arr;
    }
    var sorted = rank([12, 11, 13, 5, 6]);
    """

def seek():
    return """
    function seek(arr, x) {
        var l = 0, r = arr.length - 1;
        while (l <= r) {
            var m = Math.floor((l + r) / 2);
            if (arr[m] === x) return m;
            if (arr[m] < x) l = m + 1;
            if (arr[m] >= x) r = m - 1;
        }
        return -1;
    }
    var index = seek([2, 3, 4, 10, 40], 10);
    """

def form():
    return """
    function arm(n) {
        var s = n.toString(); var k = s.length; var sum = 0;
        for (var i = 0; i < k; i++) {
            sum += Math.pow(parseInt(s[i]), k);
        }
        return sum === n;
    }
    var check = arm(153);
    """

def term():
    return """
    function pure(n) {
        if (n < 2) return false;
        var sum = 1;
        for (var i = 2; i * i <= n; i++) {
            if (n % i === 0) {
                sum += i;
                if (i * i !== n) sum += n / i;
            }
        }
        return sum === n;
    }
    var check = pure(28);
    """

def tree():
    return """
    function Node(val) {
        this.val = val; this.left = null; this.right = null;
    }
    function insert(root, val) {
        if (!root) return new Node(val);
        if (val < root.val) root.left = insert(root.left, val);
        if (val >= root.val) root.right = insert(root.right, val);
        return root;
    }
    function inorder(root, res) {
        if (root) {
            inorder(root.left, res); res.push(root.val); inorder(root.right, res);
        }
    }
    var r = new Node(5); insert(r, 3); insert(r, 7);
    var traversal = []; inorder(r, traversal);
    """

def graph():
    return """
    function solve() {
        var graph = {
            A: { B: 1, C: 4 }, B: { A: 1, C: 2, D: 5 },
            C: { A: 4, B: 2, D: 1 }, D: { B: 5, C: 1 }
        };
        var dist = { A: 0, B: Infinity, C: Infinity, D: Infinity };
        var visited = { A: false, B: false, C: false, D: false };
        var u = 'A';
        for (var i = 0; i < 4; i++) {
            visited[u] = true;
            for (var v in graph[u]) {
                if (!visited[v]) {
                    var alt = dist[u] + graph[u][v];
                    if (alt < dist[v]) dist[v] = alt;
                }
            }
            var min = Infinity;
            for (var k in dist) {
                if (!visited[k] && dist[k] < min) {
                    min = dist[k]; u = k;
                }
            }
        }
        return dist;
    }
    var distances = solve();
    """

def sha():
    return """
    function sha(str) {
        var h0 = 0x6a09e667, h1 = 0xbb67ae85, h2 = 0x3c6ef372, h3 = 0xa54ff53a;
        for (var i = 0; i < str.length; i++) {
            var w = str.charCodeAt(i); var a = h0, b = h1, c = h2, d = h3;
            var t1 = (d + ((a << 5) | (a >>> 27)) + ((b & c) ^ (~b & d)) + w) | 0;
            h3 = h2; h2 = h1; h1 = (h0 + t1) | 0; h0 = t1;
        }
        return (h0 >>> 0).toString(16) + (h1 >>> 0).toString(16);
    }
    var val = sha('test');
    """

def md5():
    return """
    function md5(str) {
        var h0 = 0x01234567, h1 = 0x89abcdef, h2 = 0xfedcba98, h3 = 0x76543210;
        for (var i = 0; i < str.length; i++) {
            var w = str.charCodeAt(i); var a = h0, b = h1, c = h2, d = h3;
            var f = ((b & c) | (~b & d)) + w; var t1 = (d + f + a) | 0;
            h3 = h2; h2 = h1; h1 = (h1 + ((t1 << 7) | (t1 >>> 25))) | 0; h0 = t1;
        }
        return (h0 >>> 0).toString(16);
    }
    var val = md5('test');
    """

def aes():
    return """
    function aes(str) {
        var state = [0, 0, 0, 0];
        for (var i = 0; i < str.length && i < 4; i++) state[i] = str.charCodeAt(i);
        for (var round = 0; round < 10; round++) {
            for (var i = 0; i < 4; i++) {
                state[i] = (state[i] ^ 0x3c) & 0xff;
                state[i] = ((state[i] << 3) | (state[i] >>> 5)) & 0xff;
            }
            var temp = state[0]; state[0] = state[1]; state[1] = state[2]; state[2] = state[3]; state[3] = temp;
        }
        return state.join('-');
    }
    var val = aes('test');
    """

def rsa():
    return """
    function rsa(str) {
        var res = []; var n = 3233; var e = 17;
        for (var i = 0; i < str.length; i++) {
            var m = str.charCodeAt(i); var c = 1;
            for (var j = 0; j < e; j++) c = (c * m) % n;
            res.push(c);
        }
        return res.join(',');
    }
    var val = rsa('test');
    """

def primes():
    return """
    function primes(limit) {
        var sieve = [], list = [];
        for (var i = 2; i <= limit; ++i) {
            if (!sieve[i]) {
                list.push(i);
                for (var j = i << 1; j <= limit; j += i) sieve[j] = true;
            }
        }
        return list;
    }
    var val = primes(100);
    """

def dead(idx):
    bag = [sha, md5, aes, rsa, primes, memo, kmp, matrix, sieve, ackermann, levenshtein, dfs, dijkstra, huffman]
    return fuzz(bag[idx % len(bag)](), idx)

def rot(arr, k):
    if not arr: return arr
    k = k % len(arr)
    return arr[-k:] + arr[:-k]

def probe():
    return "(function(){var fn=function(){var fmt=/\\r?\\n( {4}|\\t)/;if(fmt[String.fromCharCode(116,101,115,116)](fn[String.fromCharCode(116,111,83,116,114,105,110,103)]())){try{(function(){})[String.fromCharCode(99,111,110,115,116,114,117,99,116,111,114)](String.fromCharCode(100,101,98,117,103,103,101,114))();}catch(e){}throw new Error('Protected');}};fn();}());"

def snare():
    return "(function(){var last=globalThis[String.fromCharCode(68,97,116,101)][String.fromCharCode(110,111,119)]();var fn=function(){debugger;if(globalThis[String.fromCharCode(68,97,116,101)][String.fromCharCode(110,111,119)]()-last>650){throw new Error('Protected');}last=globalThis[String.fromCharCode(68,97,116,101)][String.fromCharCode(110,111,119)]();try{(function(){})[String.fromCharCode(99,111,110,115,116,114,117,99,116,111,114)](String.fromCharCode(100,101,98,117,103,103,101,114))();}catch(e){}};fn();var tid=globalThis[String.fromCharCode(115,101,116,73,110,116,101,114,118,97,108)](fn,500);if(tid&&tid[String.fromCharCode(117,110,114,101,102)]){tid[String.fromCharCode(117,110,114,101,102)]();}}());"

def guard():
    return "(function(){try{var fn=globalThis[String.fromCharCode(77,97,116,104)][String.fromCharCode(97,98,115)];if(fn[String.fromCharCode(116,111,83,116,114,105,110,103)]()[String.fromCharCode(105,110,100,101,120,79,102)](String.fromCharCode(91,110,97,116,105,118,101,32,99,111,100,101,93))===-1){throw new Error('Protected');}if(globalThis[String.fromCharCode(70,117,110,99,116,105,111,110)][String.fromCharCode(112,114,111,116,111,116,121,112,101)][String.fromCharCode(116,111,83,116,114,105,110,103)][String.fromCharCode(116,111,83,116,114,105,110,103)]()[String.fromCharCode(105,110,100,101,120,79,102)](String.fromCharCode(91,110,97,116,105,118,101,32,99,111,100,101,93))===-1){throw new Error('Protected');}var bl=globalThis[String.fromCharCode(70,117,110,99,116,105,111,110)][String.fromCharCode(112,114,111,116,111,116,121,112,101)][String.fromCharCode(98,105,110,100)][String.fromCharCode(116,111,83,116,114,105,110,103)]()[String.fromCharCode(108,101,110,103,116,104)];if(bl<20||bl>150){throw new Error('Protected');}}catch(e){throw new Error('Protected');}}());"

def cage():
    return "(function(){try{var g=globalThis;if(!g){throw new Error('Protected');}var bl=g[String.fromCharCode(70,117,110,99,116,105,111,110)][String.fromCharCode(112,114,111,116,111,116,121,112,101)][String.fromCharCode(98,105,110,100)][String.fromCharCode(116,111,83,116,114,105,110,103)]()[String.fromCharCode(108,101,110,103,116,104)];if(bl<20||bl>150){throw new Error('Protected');}if(g[String.fromCharCode(70,117,110,99,116,105,111,110)][String.fromCharCode(112,114,111,116,111,116,121,112,101)][String.fromCharCode(116,111,83,116,114,105,110,103)][String.fromCharCode(116,111,83,116,114,105,110,103)]()[String.fromCharCode(105,110,100,101,120,79,102)](String.fromCharCode(91,110,97,116,105,118,101,32,99,111,100,101,93))===-1){throw new Error('Protected');}}catch(e){throw new Error('Protected');}}());"

def leak():
    return "(function(){var recurse=function(){try{recurse();}catch(e){var arr=[];for(var i=0;i<10000;i++){arr.push(i);}}};try{recurse();}catch(e){}}());"

def save():
    return "(function(){try{if(typeof window!=='undefined'){window.addEventListener('keydown',function(e){if(e.keyCode===123){e.preventDefault();}});}}catch(e){}}());"

def wrap(code, strings, key, k):
    shifted = rot(strings, k)
    arr = "[" + ",".join([f"'{s}'" for s in shifted]) + "]"
    hexed = hex(k)
    decoder = f"""
    globalThis._0xabc = __ARRAY__;
    try {{
        var glob = Function("return this")();
        glob._0xabc = globalThis._0xabc;
    }} catch(e) {{}}
    (function(arr, num) {{
        var fn = function(n) {{
            while (--n) {{ arr['push'](arr['shift']()); }}
        }};
        fn(++num);
    }}(globalThis._0xabc, {hexed}));
    globalThis._0xdec = function(idx) {{
        var alphabet = '__ABC__';
        var key = '{key}';
        var b64dec = function(str) {{
            var lookup = [];
            for (var i = 0; i < alphabet.length; i++) lookup[alphabet.charCodeAt(i)] = i;
            var res = '', buf = 0, bits = 0;
            for (var i = 0; i < str.length && str[i] !== '='; i++) {{
                var val = lookup[str.charCodeAt(i)];
                buf = (buf << 6) | val;
                bits += 6;
                if (bits >= 8) {{
                    bits -= 8;
                    res += String.fromCharCode((buf >> bits) & 255);
                }}
            }}
            return res;
        }};
        var raw = b64dec(globalThis._0xabc[idx]);
        var mode = raw.charCodeAt(0);
        var decs = [
            function(raw, key) {{
                var s = [], j = 0;
                for (var i = 0; i < 256; i++) s[i] = i;
                for (var i = 0; i < 256; i++) {{
                    j = (j + s[i] + key.charCodeAt(i % key.length)) % 256;
                    var temp = s[i]; s[i] = s[j]; s[j] = temp;
                }}
                var i = 0, j = 0, res = '';
                for (var y = 1; y < raw.length; y++) {{
                    i = (i + 1) % 256; j = (j + s[i]) % 256;
                    var temp = s[i]; s[i] = s[j]; s[j] = temp;
                    res += String.fromCharCode(raw.charCodeAt(y) ^ s[(s[i] + s[j]) % 256]);
                }}
                return res;
            }},
            function(raw, key) {{
                var res = '';
                for (var y = 1; y < raw.length; y++) res += String.fromCharCode(raw.charCodeAt(y) ^ key.charCodeAt((y - 1) % key.length));
                return res;
            }},
            function(raw, key) {{
                var k = key.charCodeAt(0), res = '';
                for (var y = 1; y < raw.length; y++) res += String.fromCharCode((raw.charCodeAt(y) - k + 256) % 256);
                return res;
            }},
            function(raw, key) {{
                var res = '';
                for (var y = 1; y < raw.length; y++) res += String.fromCharCode((raw.charCodeAt(y) - key.charCodeAt((y - 1) % key.length) + 256) % 256);
                return res;
            }},
            function(raw, key) {{
                var factor = raw.charCodeAt(1), b = raw.charCodeAt(2), res = '';
                for (var y = 3; y < raw.length; y++) res += String.fromCharCode((factor * (raw.charCodeAt(y) - b + 256)) % 256);
                return res;
            }},
            function(raw, key) {{
                var res = '';
                for (var y = 1; y < raw.length; y++) res += String.fromCharCode(255 - raw.charCodeAt(y));
                return res;
            }},
            function(raw, key) {{
                var k = [
                    (key.charCodeAt(0) << 24) | (key.charCodeAt(1) << 16) | (key.charCodeAt(2) << 8) | key.charCodeAt(3),
                    (key.charCodeAt(4) << 24) | (key.charCodeAt(5) << 16) | (key.charCodeAt(6) << 8) | key.charCodeAt(7),
                    (key.charCodeAt(8) << 24) | (key.charCodeAt(9) << 16) | (key.charCodeAt(10) << 8) | key.charCodeAt(11),
                    (key.charCodeAt(12) << 24) | (key.charCodeAt(13) << 16) | (key.charCodeAt(14) << 8) | key.charCodeAt(15)
                ];
                var res = '';
                for (var i = 1; i < raw.length; i += 8) {{
                    var v0 = (raw.charCodeAt(i) << 24) | (raw.charCodeAt(i+1) << 16) | (raw.charCodeAt(i+2) << 8) | raw.charCodeAt(i+3);
                    var v1 = (raw.charCodeAt(i+4) << 24) | (raw.charCodeAt(i+5) << 16) | (raw.charCodeAt(i+6) << 8) | raw.charCodeAt(i+7);
                    var sum = 0xc6ef3720, delta = 0x9e3779b9;
                    for (var r = 0; r < 32; r++) {{
                        v1 = (v1 - (((v0 << 4 ^ v0 >>> 5) + v0) ^ (sum + k[(sum >>> 11) & 3]))) | 0;
                        sum = (sum - delta) | 0;
                        v0 = (v0 - (((v1 << 4 ^ v1 >>> 5) + v1) ^ (sum + k[sum & 3]))) | 0;
                    }}
                    res += String.fromCharCode((v0 >>> 24) & 255, (v0 >>> 16) & 255, (v0 >>> 8) & 255, v0 & 255);
                    res += String.fromCharCode((v1 >>> 24) & 255, (v1 >>> 16) & 255, (v1 >>> 8) & 255, v1 & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 8; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var k = [
                    (key.charCodeAt(0) << 8) | key.charCodeAt(1),
                    (key.charCodeAt(2) << 8) | key.charCodeAt(3),
                    (key.charCodeAt(4) << 8) | key.charCodeAt(5),
                    (key.charCodeAt(6) << 8) | key.charCodeAt(7)
                ];
                var sub = [], l = k.slice(1), a = k[0]; sub.push(a);
                for (var i = 0; i < 21; i++) {{
                    var val = (((l[i] >> 7) | (l[i] << 9)) + a) & 0xffff;
                    val = (val ^ i) & 0xffff;
                    a = (((a << 2) | (a >> 14)) & 0xffff) ^ val;
                    l.push(val); sub.push(a);
                }}
                var res = '';
                for (var i = 1; i < raw.length; i += 4) {{
                    var x = (raw.charCodeAt(i) << 8) | raw.charCodeAt(i+1);
                    var y = (raw.charCodeAt(i+2) << 8) | raw.charCodeAt(i+3);
                    for (var r = sub.length - 1; r >= 0; r--) {{
                        y = (((y ^ x) >> 2) | ((y ^ x) << 14)) & 0xffff;
                        var temp = (x ^ sub[r]) & 0xffff;
                        x = (temp - y + 65536) & 0xffff;
                        x = (((x << 7) | (x >> 9)) & 0xffff);
                    }}
                    res += String.fromCharCode((x >> 8) & 255, x & 255, (y >> 8) & 255, y & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 4; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var k = [
                    (key.charCodeAt(0) << 8) | key.charCodeAt(1),
                    (key.charCodeAt(2) << 8) | key.charCodeAt(3),
                    (key.charCodeAt(4) << 8) | key.charCodeAt(5),
                    (key.charCodeAt(6) << 8) | key.charCodeAt(7)
                ];
                var sub = [];
                for (var i = 0; i < 4; i++) sub.push(k[i]);
                var z = [
                    1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1,
                    0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1,
                    1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1,
                    0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1
                ];
                for (var i = 4; i < 32; i++) {{
                    var temp = (((sub[i-1] >> 3) | (sub[i-1] << 13)) & 0xffff) ^ sub[i-3];
                    temp = temp ^ (((temp >> 1) | (temp << 15)) & 0xffff);
                    sub.push(sub[i-4] ^ temp ^ z[(i-4) % 62] ^ 0xfffc);
                }}
                var res = '';
                for (var i = 1; i < raw.length; i += 4) {{
                    var x = (raw.charCodeAt(i) << 8) | raw.charCodeAt(i+1);
                    var y = (raw.charCodeAt(i+2) << 8) | raw.charCodeAt(i+3);
                    for (var r = sub.length - 1; r >= 0; r--) {{
                        var temp = x; x = y;
                        y = (temp ^ (((((x << 1) | (x >> 15)) & 0xffff) & (((x << 8) | (x >> 8)) & 0xffff) ^ (((x << 2) | (x >> 14)) & 0xffff) ^ sub[r]) & 0xffff)) & 0xffff;
                    }}
                    res += String.fromCharCode((x >> 8) & 255, x & 255, (y >> 8) & 255, y & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 4; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var l = [];
                for (var i = 0; i < 16; i += 4) {{
                    l.push((key.charCodeAt(i) << 24) | (key.charCodeAt(i+1) << 16) | (key.charCodeAt(i+2) << 8) | key.charCodeAt(i+3));
                }}
                var s = []; s.push(0xb7e15163);
                for (var i = 1; i < 26; i++) s.push((s[i-1] + 0x9e3779b9) | 0);
                var a = 0, b = 0, i = 0, j = 0;
                for (var round = 0; round < 78; round++) {{
                    var valS = (s[i] + a + b) | 0;
                    s[i] = a = ((valS << 3) | (valS >>> 29)) | 0;
                    
                    var valL = (l[j] + a + b) | 0;
                    var rot = (a + b) & 31;
                    if (rot === 0) {{
                        l[j] = b = valL;
                    }} else {{
                        l[j] = b = ((valL << rot) | (valL >>> (32 - rot))) | 0;
                    }}
                    i = (i + 1) % 26; j = (j + 1) % 4;
                }}
                var res = '';
                for (var idx = 1; idx < raw.length; idx += 8) {{
                    var x = (raw.charCodeAt(idx) << 24) | (raw.charCodeAt(idx+1) << 16) | (raw.charCodeAt(idx+2) << 8) | raw.charCodeAt(idx+3);
                    var y = (raw.charCodeAt(idx+4) << 24) | (raw.charCodeAt(idx+5) << 16) | (raw.charCodeAt(idx+6) << 8) | raw.charCodeAt(idx+7);
                    for (var r = 12; r >= 1; r--) {{
                        var rot = x & 31;
                        var tempY = (y - s[2*r+1]) | 0;
                        if (rot === 0) {{
                            y = (tempY ^ x) | 0;
                        }} else {{
                            y = (((tempY >>> rot) | (tempY << (32 - rot))) ^ x) | 0;
                        }}
                        
                        rot = y & 31;
                        var tempX = (x - s[2*r]) | 0;
                        if (rot === 0) {{
                            x = (tempX ^ y) | 0;
                        }} else {{
                            x = (((tempX >>> rot) | (tempX << (32 - rot))) ^ y) | 0;
                        }}
                    }}
                    y = (y - s[1]) | 0; x = (x - s[0]) | 0;
                    res += String.fromCharCode((x >>> 24) & 255, (x >>> 16) & 255, (x >>> 8) & 255, x & 255);
                    res += String.fromCharCode((y >>> 24) & 255, (y >>> 16) & 255, (y >>> 8) & 255, y & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 8; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var k = [
                    (key.charCodeAt(0) << 24) | (key.charCodeAt(1) << 16) | (key.charCodeAt(2) << 8) | key.charCodeAt(3),
                    (key.charCodeAt(4) << 24) | (key.charCodeAt(5) << 16) | (key.charCodeAt(6) << 8) | key.charCodeAt(7),
                    (key.charCodeAt(8) << 24) | (key.charCodeAt(9) << 16) | (key.charCodeAt(10) << 8) | key.charCodeAt(11),
                    (key.charCodeAt(12) << 24) | (key.charCodeAt(13) << 16) | (key.charCodeAt(14) << 8) | key.charCodeAt(15)
                ];
                var res = '';
                for (var idx = 1; idx < raw.length; idx += 8) {{
                    var x = (raw.charCodeAt(idx) << 24) | (raw.charCodeAt(idx+1) << 16) | (raw.charCodeAt(idx+2) << 8) | raw.charCodeAt(idx+3);
                    var y = (raw.charCodeAt(idx+4) << 24) | (raw.charCodeAt(idx+5) << 16) | (raw.charCodeAt(idx+6) << 8) | raw.charCodeAt(idx+7);
                    var tempY = (y >>> 12) | (y << 20);
                    y = (tempY ^ x) | 0; x = (x - y) | 0; y = (y ^ x) | 0; x = (x - k[2]) | 0;
                    tempY = (y >>> 16) | (y << 16);
                    y = (tempY ^ x) | 0; x = (x - y) | 0; y = (y ^ k[1]) | 0; x = (x ^ k[0]) | 0;
                    res += String.fromCharCode((x >>> 24) & 255, (x >>> 16) & 255, (x >>> 8) & 255, x & 255);
                    res += String.fromCharCode((y >>> 24) & 255, (y >>> 16) & 255, (y >>> 8) & 255, y & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                if (pad > 0 && pad <= 8) res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var k = [
                    (key.charCodeAt(0) << 24) | (key.charCodeAt(1) << 16) | (key.charCodeAt(2) << 8) | key.charCodeAt(3),
                    (key.charCodeAt(4) << 24) | (key.charCodeAt(5) << 16) | (key.charCodeAt(6) << 8) | key.charCodeAt(7),
                    (key.charCodeAt(8) << 24) | (key.charCodeAt(9) << 16) | (key.charCodeAt(10) << 8) | key.charCodeAt(11),
                    (key.charCodeAt(12) << 24) | (key.charCodeAt(13) << 16) | (key.charCodeAt(14) << 8) | key.charCodeAt(15)
                ];
                var sub = [], l = k.slice(1), a = k[0]; sub.push(a);
                for (var i = 0; i < 26; i++) {{
                    var val = ((((l[i] >>> 8) | (l[i] << 24)) | 0) + a) | 0;
                    val = (val ^ i) | 0; a = (((a << 3) | (a >>> 29)) | 0) ^ val;
                    l.push(val); sub.push(a);
                }}
                var res = '';
                for (var idx = 1; idx < raw.length; idx += 8) {{
                    var x = (raw.charCodeAt(idx) << 24) | (raw.charCodeAt(idx+1) << 16) | (raw.charCodeAt(idx+2) << 8) | raw.charCodeAt(idx+3);
                    var y = (raw.charCodeAt(idx+4) << 24) | (raw.charCodeAt(idx+5) << 16) | (raw.charCodeAt(idx+6) << 8) | raw.charCodeAt(idx+7);
                    for (var r = sub.length - 1; r >= 0; r--) {{
                        y = (((y ^ x) >>> 3) | ((y ^ x) << 29)) | 0;
                        var temp = (x ^ sub[r]) | 0; x = (temp - y) | 0;
                        x = (((x << 8) | (x >>> 24))) | 0;
                    }}
                    res += String.fromCharCode((x >>> 24) & 255, (x >>> 16) & 255, (x >>> 8) & 255, x & 255);
                    res += String.fromCharCode((y >>> 24) & 255, (y >>> 16) & 255, (y >>> 8) & 255, y & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 8; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var k = [
                    (key.charCodeAt(0) << 24) | (key.charCodeAt(1) << 16) | (key.charCodeAt(2) << 8) | key.charCodeAt(3),
                    (key.charCodeAt(4) << 24) | (key.charCodeAt(5) << 16) | (key.charCodeAt(6) << 8) | key.charCodeAt(7),
                    (key.charCodeAt(8) << 24) | (key.charCodeAt(9) << 16) | (key.charCodeAt(10) << 8) | key.charCodeAt(11),
                    (key.charCodeAt(12) << 24) | (key.charCodeAt(13) << 16) | (key.charCodeAt(14) << 8) | key.charCodeAt(15)
                ];
                var sub = [];
                for (var i = 0; i < 4; i++) sub.push(k[i]);
                var z = [
                    1, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1,
                    0, 1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0, 1
                ];
                for (var i = 4; i < 36; i++) {{
                    var temp = (((sub[i-1] >>> 3) | (sub[i-1] << 29)) | 0) ^ sub[i-3];
                    temp = temp ^ (((temp >>> 1) | (temp << 31)) | 0);
                    sub.push(sub[i-4] ^ temp ^ z[(i-4) % 32] ^ 0xfffffffc);
                }}
                var res = '';
                for (var idx = 1; idx < raw.length; idx += 8) {{
                    var x = (raw.charCodeAt(idx) << 24) | (raw.charCodeAt(idx+1) << 16) | (raw.charCodeAt(idx+2) << 8) | raw.charCodeAt(idx+3);
                    var y = (raw.charCodeAt(idx+4) << 24) | (raw.charCodeAt(idx+5) << 16) | (raw.charCodeAt(idx+6) << 8) | raw.charCodeAt(idx+7);
                    for (var r = sub.length - 1; r >= 0; r--) {{
                        var temp = x; x = y;
                        y = (temp ^ (((((x << 1) | (x >>> 31)) & (((x << 8) | (x >>> 24))) ^ ((x << 2) | (x >>> 30))) ^ sub[r]))) | 0;
                    }}
                    res += String.fromCharCode((x >>> 24) & 255, (x >>> 16) & 255, (x >>> 8) & 255, x & 255);
                    res += String.fromCharCode((y >>> 24) & 255, (y >>> 16) & 255, (y >>> 8) & 255, y & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 8; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var k = [
                    (key.charCodeAt(0) << 24) | (key.charCodeAt(1) << 16) | (key.charCodeAt(2) << 8) | key.charCodeAt(3),
                    (key.charCodeAt(4) << 24) | (key.charCodeAt(5) << 16) | (key.charCodeAt(6) << 8) | key.charCodeAt(7),
                    (key.charCodeAt(8) << 24) | (key.charCodeAt(9) << 16) | (key.charCodeAt(10) << 8) | key.charCodeAt(11),
                    (key.charCodeAt(12) << 24) | (key.charCodeAt(13) << 16) | (key.charCodeAt(14) << 8) | key.charCodeAt(15)
                ];
                var res = '';
                for (var i = 1; i < raw.length; i += 16) {{
                    var a = (raw.charCodeAt(i) << 24) | (raw.charCodeAt(i+1) << 16) | (raw.charCodeAt(i+2) << 8) | raw.charCodeAt(i+3);
                    var b = (raw.charCodeAt(i+4) << 24) | (raw.charCodeAt(i+5) << 16) | (raw.charCodeAt(i+6) << 8) | raw.charCodeAt(i+7);
                    var c = (raw.charCodeAt(i+8) << 24) | (raw.charCodeAt(i+9) << 16) | (raw.charCodeAt(i+10) << 8) | raw.charCodeAt(i+11);
                    var d = (raw.charCodeAt(i+12) << 24) | (raw.charCodeAt(i+13) << 16) | (raw.charCodeAt(i+14) << 8) | raw.charCodeAt(i+15);
                    a = (a - k[2]) | 0; c = (c - k[3]) | 0;
                    for (var r = 20; r >= 1; r--) {{
                        var temp = d; d = c; c = b; b = a; a = temp;
                        var t = ((Math.imul(b, b) << 1) + b) | 0; t = (t << 5 | t >>> 27) | 0;
                        var u = ((Math.imul(d, d) << 1) + d) | 0; u = (u << 5 | u >>> 27) | 0;
                        c = (c - k[(2 * r + 1) % 4]) | 0; c = ((c >>> (t & 31)) | (c << (32 - (t & 31)))) ^ u;
                        a = (a - k[(2 * r) % 4]) | 0; a = ((a >>> (u & 31)) | (a << (32 - (u & 31)))) ^ t;
                    }}
                    b = (b - k[0]) | 0; d = (d - k[1]) | 0;
                    res += String.fromCharCode((a >>> 24) & 255, (a >>> 16) & 255, (a >>> 8) & 255, a & 255);
                    res += String.fromCharCode((b >>> 24) & 255, (b >>> 16) & 255, (b >>> 8) & 255, b & 255);
                    res += String.fromCharCode((c >>> 24) & 255, (c >>> 16) & 255, (c >>> 8) & 255, c & 255);
                    res += String.fromCharCode((d >>> 24) & 255, (d >>> 16) & 255, (d >>> 8) & 255, d & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 16; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var seed = 5381;
                for (var i = 0; i < key.length; i++) seed = ((seed << 5) + seed) + key.charCodeAt(i);
                seed = seed & 0xffffffff;
                var val = seed, p = [];
                for (var i = 0; i < 18; i++) {{ val = (Math.imul(1103515245, val) + 12345) | 0; p.push(val >>> 0); }}
                var s = [];
                for (var i = 0; i < 4; i++) {{
                    var box = [];
                    for (var j = 0; j < 256; j++) {{ val = (Math.imul(1103515245, val) + 12345) | 0; box.push(val >>> 0); }}
                    s.push(box);
                }}
                var res = '';
                for (var idx = 1; idx < raw.length; idx += 8) {{
                    var l = (raw.charCodeAt(idx) << 24) | (raw.charCodeAt(idx+1) << 16) | (raw.charCodeAt(idx+2) << 8) | raw.charCodeAt(idx+3);
                    var r = (raw.charCodeAt(idx+4) << 24) | (raw.charCodeAt(idx+5) << 16) | (raw.charCodeAt(idx+6) << 8) | raw.charCodeAt(idx+7);
                    r = r ^ p[16]; l = l ^ p[17];
                    var temp = l; l = r; r = temp;
                    for (var round = 15; round >= 0; round--) {{
                        var d1 = (r >>> 24) & 255, d2 = (r >>> 16) & 255, d3 = (r >>> 8) & 255, d4 = r & 255;
                        var fval = (s[0][d1] + s[1][d2]) | 0;
                        fval = (fval ^ s[2][d3]) | 0; fval = (fval + s[3][d4]) | 0;
                        var tempVal = r;
                        r = l ^ fval;
                        l = tempVal ^ p[round];
                    }}
                    res += String.fromCharCode((l >>> 24) & 255, (l >>> 16) & 255, (l >>> 8) & 255, l & 255);
                    res += String.fromCharCode((r >>> 24) & 255, (r >>> 16) & 255, (r >>> 8) & 255, r & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 8; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var seed = 5381;
                for (var i = 0; i < key.length; i++) seed = ((seed << 5) + seed) + key.charCodeAt(i);
                seed = seed & 0xffffffff;
                var val = seed;
                var rand = function() {{ val = (Math.imul(1103515245, val) + 12345) | 0; return val >>> 0; }};
                var ip = [];
                for (var i = 0; i < 64; i++) ip.push(i);
                for (var i = 63; i > 0; i--) {{
                    var j = (rand() >>> 0) % (i + 1);
                    var temp = ip[i]; ip[i] = ip[j]; ip[j] = temp;
                }}
                var fp = [];
                for (var i = 0; i < 64; i++) fp.push(0);
                for (var i = 0; i < 64; i++) fp[ip[i]] = i;
                var e = [];
                for (var i = 0; i < 48; i++) e.push((rand() >>> 0) % 32);
                var p = [];
                for (var i = 0; i < 32; i++) p.push(i);
                for (var i = 31; i > 0; i--) {{
                    var j = (rand() >>> 0) % (i + 1);
                    var temp = p[i]; p[i] = p[j]; p[j] = temp;
                }}
                var s = [];
                for (var i = 0; i < 8; i++) {{
                    var box = [];
                    for (var j = 0; j < 64; j++) box.push((rand() >>> 0) % 16);
                    s.push(box);
                }}
                var sub = [];
                for (var i = 0; i < 16; i++) {{
                    var kl = rand() & 0xffffff, kr = rand() & 0xffffff;
                    sub.push([kl, kr]);
                }}
                var res = '';
                for (var idx = 1; idx < raw.length; idx += 8) {{
                    var bl = (raw.charCodeAt(idx) << 24) | (raw.charCodeAt(idx+1) << 16) | (raw.charCodeAt(idx+2) << 8) | raw.charCodeAt(idx+3);
                    var br = (raw.charCodeAt(idx+4) << 24) | (raw.charCodeAt(idx+5) << 16) | (raw.charCodeAt(idx+6) << 8) | raw.charCodeAt(idx+7);
                    var pl = 0, pr = 0;
                    for (var i = 0; i < 32; i++) {{
                        var bitpos = ip[i];
                        var bit = bitpos < 32 ? (bl >>> (31 - bitpos)) & 1 : (br >>> (63 - bitpos)) & 1;
                        pl = (pl << 1) | bit;
                    }}
                    for (var i = 32; i < 64; i++) {{
                        var bitpos = ip[i];
                        var bit = bitpos < 32 ? (bl >>> (31 - bitpos)) & 1 : (br >>> (63 - bitpos)) & 1;
                        pr = (pr << 1) | bit;
                    }}
                    var l = pr, r = pl;
                    for (var round = 15; round >= 0; round--) {{
                        var tr = l, kl = sub[round][0], kr = sub[round][1];
                        var el = 0, er = 0;
                        for (var i = 0; i < 24; i++) el = (el << 1) | ((tr >>> (31 - e[i])) & 1);
                        for (var i = 24; i < 48; i++) er = (er << 1) | ((tr >>> (31 - e[i])) & 1);
                        el = el ^ kl; er = er ^ kr;
                        var sval = 0;
                        for (var i = 0; i < 4; i++) {{
                            var chunk = (el >>> (18 - i * 6)) & 0x3f;
                            sval = (sval << 4) | s[i][chunk];
                        }}
                        for (var i = 4; i < 8; i++) {{
                            var chunk = (er >>> (42 - i * 6)) & 0x3f;
                            sval = (sval << 4) | s[i][chunk];
                        }}
                        var pval = 0;
                        for (var i = 0; i < 32; i++) pval = (pval << 1) | ((sval >>> (31 - p[i])) & 1);
                        l = r ^ pval; r = tr;
                    }}
                    var fl = 0, fr = 0;
                    for (var i = 0; i < 32; i++) {{
                        var bitpos = fp[i];
                        var bit = bitpos < 32 ? (l >>> (31 - bitpos)) & 1 : (r >>> (63 - bitpos)) & 1;
                        fl = (fl << 1) | bit;
                    }}
                    for (var i = 32; i < 64; i++) {{
                        var bitpos = fp[i];
                        var bit = bitpos < 32 ? (l >>> (31 - bitpos)) & 1 : (r >>> (63 - bitpos)) & 1;
                        fr = (fr << 1) | bit;
                    }}
                    res += String.fromCharCode((fl >>> 24) & 255, (fl >>> 16) & 255, (fl >>> 8) & 255, fl & 255);
                    res += String.fromCharCode((fr >>> 24) & 255, (fr >>> 16) & 255, (fr >>> 8) & 255, fr & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                if (pad > 0 && pad <= 8) res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var k = [
                    (key.charCodeAt(0) << 24) | (key.charCodeAt(1) << 16) | (key.charCodeAt(2) << 8) | key.charCodeAt(3),
                    (key.charCodeAt(4) << 24) | (key.charCodeAt(5) << 16) | (key.charCodeAt(6) << 8) | key.charCodeAt(7),
                    (key.charCodeAt(8) << 24) | (key.charCodeAt(9) << 16) | (key.charCodeAt(10) << 8) | key.charCodeAt(11),
                    (key.charCodeAt(12) << 24) | (key.charCodeAt(13) << 16) | (key.charCodeAt(14) << 8) | key.charCodeAt(15)
                ];
                var res = '';
                for (var i = 1; i < raw.length; i += 8) {{
                    var v0 = (raw.charCodeAt(i) << 24) | (raw.charCodeAt(i+1) << 16) | (raw.charCodeAt(i+2) << 8) | raw.charCodeAt(i+3);
                    var v1 = (raw.charCodeAt(i+4) << 24) | (raw.charCodeAt(i+5) << 16) | (raw.charCodeAt(i+6) << 8) | raw.charCodeAt(i+7);
                    var sum = 0xc6ef3720, delta = 0x9e3779b9;
                    for (var r = 0; r < 32; r++) {{
                        v1 = (v1 - (((v0 << 4) + k[2]) ^ (v0 + sum) ^ ((v0 >>> 5) + k[3]))) | 0;
                        v0 = (v0 - (((v1 << 4) + k[0]) ^ (v1 + sum) ^ ((v1 >>> 5) + k[1]))) | 0;
                        sum = (sum - delta) | 0;
                    }}
                    res += String.fromCharCode((v0 >>> 24) & 255, (v0 >>> 16) & 255, (v0 >>> 8) & 255, v0 & 255);
                    res += String.fromCharCode((v1 >>> 24) & 255, (v1 >>> 16) & 255, (v1 >>> 8) & 255, v1 & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 8; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var seed = 5381;
                for (var i = 0; i < key.length; i++) seed = (((seed << 5) + seed) + key.charCodeAt(i)) & 0xffffffff;
                var val = seed, sub = [];
                for (var i = 0; i < 16; i++) {{ val = (Math.imul(1103515245, val) + 12345) | 0; sub.push(val >>> 0); }}
                var res = '';
                for (var idx = 1; idx < raw.length; idx += 8) {{
                    var l = (raw.charCodeAt(idx) << 24) | (raw.charCodeAt(idx+1) << 16) | (raw.charCodeAt(idx+2) << 8) | raw.charCodeAt(idx+3);
                    var r = (raw.charCodeAt(idx+4) << 24) | (raw.charCodeAt(idx+5) << 16) | (raw.charCodeAt(idx+6) << 8) | raw.charCodeAt(idx+7);
                    for (var round = 15; round >= 0; round--) {{
                        var temp = r; r = l;
                        var f = (r ^ sub[round]) & 0xffffffff;
                        f = (((f << 7) | (f >>> 25)) & 0xffffffff) ^ 0x9e3779b9;
                        l = temp ^ f;
                    }}
                    res += String.fromCharCode((l >>> 24) & 255, (l >>> 16) & 255, (l >>> 8) & 255, l & 255);
                    res += String.fromCharCode((r >>> 24) & 255, (r >>> 16) & 255, (r >>> 8) & 255, r & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 8; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var seed = 5381;
                for (var i = 0; i < key.length; i++) seed = (((seed << 5) + seed) + key.charCodeAt(i)) & 0xffffffff;
                var val = seed, sub = [];
                for (var i = 0; i < 32; i++) {{ val = ((Math.imul(1103515245, val) + 12345) | 0) & 255; sub.push(val); }}
                var res = '';
                for (var idx = 1; idx < raw.length; idx += 8) {{
                    var state = [];
                    for (var i = 0; i < 8; i++) state.push(raw.charCodeAt(idx + i));
                    for (var round = 31; round >= 0; round--) {{
                        var n = [];
                        n[0] = (state[7] + sub[round]) & 255;
                        n[1] = state[0];
                        n[2] = (state[1] ^ sub[round]) & 255;
                        n[3] = state[2];
                        n[4] = (state[3] + sub[round]) & 255;
                        n[5] = state[4];
                        n[6] = (state[5] ^ sub[round]) & 255;
                        n[7] = state[6];
                        state = n;
                    }}
                    for (var i = 0; i < 8; i++) res += String.fromCharCode(state[i]);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 8; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var seed = 5381;
                for (var i = 0; i < key.length; i++) seed = (((seed << 5) + seed) + key.charCodeAt(i)) & 0xffffffff;
                var val = seed, sub = [];
                for (var i = 0; i < 32; i++) {{ val = (Math.imul(1103515245, val) + 12345) | 0; sub.push(val >>> 0); }}
                var res = '';
                for (var idx = 1; idx < raw.length; idx += 8) {{
                    var l = (raw.charCodeAt(idx) << 24) | (raw.charCodeAt(idx+1) << 16) | (raw.charCodeAt(idx+2) << 8) | raw.charCodeAt(idx+3);
                    var r = (raw.charCodeAt(idx+4) << 24) | (raw.charCodeAt(idx+5) << 16) | (raw.charCodeAt(idx+6) << 8) | raw.charCodeAt(idx+7);
                    for (var round = 30; round >= 0; round--) {{
                        r = ((r >>> 13) | (r << 19)) & 0xffffffff;
                        l = ((l >>> 9) | (l << 23)) & 0xffffffff;
                        r ^= sub[round+1]; l ^= sub[round];
                    }}
                    res += String.fromCharCode((l >>> 24) & 255, (l >>> 16) & 255, (l >>> 8) & 255, l & 255);
                    res += String.fromCharCode((r >>> 24) & 255, (r >>> 16) & 255, (r >>> 8) & 255, r & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 8; res = res.substring(0, res.length - pad);
                return res;
            }},
            function(raw, key) {{
                var seed = 5381;
                for (var i = 0; i < key.length; i++) seed = (((seed << 5) + seed) + key.charCodeAt(i)) & 0xffffffff;
                var val = seed, sub = [];
                for (var i = 0; i < 12; i++) {{ val = (Math.imul(1103515245, val) + 12345) | 0; sub.push(val >>> 0); }}
                var res = '';
                for (var idx = 1; idx < raw.length; idx += 8) {{
                    var l = (raw.charCodeAt(idx) << 24) | (raw.charCodeAt(idx+1) << 16) | (raw.charCodeAt(idx+2) << 8) | raw.charCodeAt(idx+3);
                    var r = (raw.charCodeAt(idx+4) << 24) | (raw.charCodeAt(idx+5) << 16) | (raw.charCodeAt(idx+6) << 8) | raw.charCodeAt(idx+7);
                    for (var round = 11; round >= 0; round--) {{
                        var temp = r; r = l;
                        var k = sub[round];
                        var f = ((r + k) & 0xffffffff) ^ (((r << 5) | (r >>> 27)) & 0xffffffff);
                        l = temp ^ f;
                    }}
                    res += String.fromCharCode((l >>> 24) & 255, (l >>> 16) & 255, (l >>> 8) & 255, l & 255);
                    res += String.fromCharCode((r >>> 24) & 255, (r >>> 16) & 255, (r >>> 8) & 255, r & 255);
                }}
                var pad = res.charCodeAt(res.length - 1);
                pad = pad || 8; res = res.substring(0, res.length - pad);
                return res;
            }}
        ];
        var res = decs[mode](raw, key);
        try {{ return decodeURIComponent(escape(res)); }} catch (e) {{ return res; }}
    }};
    try {{
        var _realGlobal = Function("return this")();
        _realGlobal._0xdec = globalThis._0xdec;
    }} catch(e) {{}}
    """
    decoder = haze(decoder)
    decoder = decoder.replace("__ABC__", abc)
    decoder = decoder.replace("__ARRAY__", arr)
    lines = [line.strip() for line in decoder.split('\n') if line.strip()]
    collapsed = " ".join(lines)
    return escape(collapsed + " " + code)

def gap(a, b):
    def word(c): return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9' or c in '_$' or ord(c) > 127
    if (a.endswith('+') or a.endswith('-')) and (b.startswith('+') or b.startswith('-')): return True
    if a.endswith('/') and (b.startswith('/') or b.startswith('*')): return True
    if not word(b): return False
    ops = {';', ',', '[', '{', '(', ':', '+', '-', '*', '/', '=', '!', '?', '&', '|', '^', '%', '<', '>', '.', '~', '?.'}
    return a not in ops

def escape(code):
    keywords = {
        'var', 'let', 'const', 'function', 'return', 'if', 'else', 'for',
        'while', 'do', 'switch', 'case', 'break', 'continue', 'default',
        'try', 'catch', 'finally', 'throw', 'new', 'this', 'typeof',
        'instanceof', 'delete', 'void', 'in', 'of', 'class', 'extends',
        'import', 'export', 'debugger', 'true', 'false', 'null', 'undefined',
        'async', 'await', 'yield', 'with', 'super',
        'GM_xmlhttpRequest', 'GM_setValue', 'GM_getValue', 'GM_deleteValue',
        'GM_listValues', 'GM_addStyle', 'GM_getResourceText', 'GM_getResourceURL',
        'GM_log', 'GM_openInTab', 'GM_registerMenuCommand', 'GM_unregisterMenuCommand',
        'GM_setClipboard', 'GM_info'
    }
    toks = scan(code)
    out = []
    for t in toks:
        if t.t == 'str':
            q = t.v[0]
            if q == '`':
                val = t.v[1:-1]
                res = ""
                for c in val:
                    o = ord(c)
                    if o > 127: res += f"\\u{o:04x}"
                    else: res += c
                out.append(q + res + q)
            else:
                try:
                    val = eval(t.v)
                except:
                    val = t.v[1:-1]
                res = ""
                for c in val:
                    o = ord(c)
                    res += f"\\u{o:04x}"
                out.append(q + res + q)
        elif t.t == 'id' and t.v not in keywords:
            res = ""
            for c in t.v:
                o = ord(c)
                if o > 127: res += f"\\u{o:04x}"
                if o <= 127: res += c
            out.append(res)
        elif t.t == 'id' and t.v in keywords:
            out.append(t.v)
        else:
            res = ""
            for c in t.v:
                o = ord(c)
                if o > 127: res += f"\\u{o:04x}"
                if o <= 127: res += c
            out.append(res)
    result = ""
    for i, t in enumerate(toks):
        v = out[i]
        if i > 0 and gap(toks[i-1].v[-1], t.v[0]): result += " " + v
        else: result += v
    return result

def memo():
    return """
    function fibm(n, m) {
        if (!m) m = {};
        if (n <= 1) return n;
        if (m[n] !== undefined) return m[n];
        m[n] = fibm(n - 1, m) + fibm(n - 2, m);
        return m[n];
    }
    function fibSeq(limit) {
        var seq = [], a = 0, b = 1, t;
        while (a <= limit) { seq.push(a); t = a + b; a = b; b = t; }
        return seq;
    }
    var fibResult = fibm(30);
    var fibList = fibSeq(1000);
    """

def kmp():
    return """
    function kmpTable(pat) {
        var t = [0], k = 0;
        for (var i = 1; i < pat.length; i++) {
            while (k > 0 && pat[k] !== pat[i]) k = t[k - 1];
            if (pat[k] === pat[i]) k++;
            t.push(k);
        }
        return t;
    }
    function kmpFind(str, pat) {
        var t = kmpTable(pat), k = 0, res = [];
        for (var i = 0; i < str.length; i++) {
            while (k > 0 && str[i] !== pat[k]) k = t[k - 1];
            if (str[i] === pat[k]) k++;
            if (k === pat.length) { res.push(i - k + 1); k = t[k - 1]; }
        }
        return res;
    }
    function kmpCount(str, pat) { return kmpFind(str, pat).length; }
    var kmpResult = kmpFind('abcabcabcabc', 'abc');
    var kmpCount2 = kmpCount('aaaaaaa', 'aa');
    """

def matrix():
    return """
    function matmul(a, b) {
        var n = a.length, r = [], i, j, k;
        for (i = 0; i < n; i++) {
            r[i] = [];
            for (j = 0; j < n; j++) {
                r[i][j] = 0;
                for (k = 0; k < n; k++) r[i][j] += a[i][k] * b[k][j];
            }
        }
        return r;
    }
    function matpow(m, p) {
        var res = [[1, 0], [0, 1]];
        while (p > 0) { if (p & 1) res = matmul(res, m); m = matmul(m, m); p >>= 1; }
        return res;
    }
    function mattrace(a) { var s = 0; for (var i = 0; i < a.length; i++) s += a[i][i]; return s; }
    var matBase = [[1, 1], [1, 0]];
    var matResult = matpow(matBase, 10);
    var matTrace = mattrace(matResult);
    """

def encode():
    return """
    function b64enc(str) {
        var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        var res = '', buf = 0, bits = 0;
        for (var i = 0; i < str.length; i++) {
            buf = (buf << 8) | str.charCodeAt(i); bits += 8;
            while (bits >= 6) { bits -= 6; res += chars[(buf >> bits) & 63]; }
        }
        if (bits > 0) res += chars[(buf << (6 - bits)) & 63];
        while (res.length % 4 !== 0) res += '=';
        return res;
    }
    function b64dec(str) {
        var chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/';
        var res = '', buf = 0, bits = 0;
        for (var i = 0; i < str.length && str[i] !== '='; i++) {
            buf = (buf << 6) | chars.indexOf(str[i]); bits += 6;
            if (bits >= 8) { bits -= 8; res += String.fromCharCode((buf >> bits) & 255); }
        }
        return res;
    }
    var encResult = b64dec(b64enc('hello world'));
    """

def sieve():
    return """
    function sieve(limit) {
        var flag = [], list = [], i, j;
        for (i = 0; i <= limit; i++) flag[i] = true;
        flag[0] = flag[1] = false;
        for (i = 2; i * i <= limit; i++) {
            if (flag[i]) for (j = i * i; j <= limit; j += i) flag[j] = false;
        }
        for (i = 2; i <= limit; i++) if (flag[i]) list.push(i);
        return list;
    }
    function goldbach(n) {
        var primes = sieve(n);
        var set = {};
        for (var i = 0; i < primes.length; i++) set[primes[i]] = true;
        for (var i = 2; i < n; i++) { if (set[i] && set[n - i]) return [i, n - i]; }
        return null;
    }
    var sieveResult = sieve(200);
    var goldbachResult = goldbach(100);
    """

def heap():
    return """
    function heapify(arr, n, i) {
        var max = i, l = 2 * i + 1, r = 2 * i + 2, t;
        if (l < n && arr[l] > arr[max]) max = l;
        if (r < n && arr[r] > arr[max]) max = r;
        if (max !== i) { t = arr[i]; arr[i] = arr[max]; arr[max] = t; heapify(arr, n, max); }
    }
    function heapsort(arr) {
        var n = arr.length, t;
        for (var i = Math.floor(n / 2) - 1; i >= 0; i--) heapify(arr, n, i);
        for (var i = n - 1; i > 0; i--) { t = arr[0]; arr[0] = arr[i]; arr[i] = t; heapify(arr, i, 0); }
        return arr;
    }
    function buildMaxHeap(arr) {
        for (var i = Math.floor(arr.length / 2) - 1; i >= 0; i--) heapify(arr, arr.length, i);
        return arr;
    }
    var heapResult = heapsort([9, 4, 7, 2, 5, 1, 8, 3, 6]);
    var heapMax = buildMaxHeap([3, 1, 4, 1, 5, 9, 2, 6]);
    """

def cipher():
    return """
    function xenc(text, key) {
        var res = '';
        for (var i = 0; i < text.length; i++) {
            res += String.fromCharCode((text.charCodeAt(i) + key.charCodeAt(i % key.length)) % 256);
        }
        return res;
    }
    function xdec(text, key) {
        var res = '';
        for (var i = 0; i < text.length; i++) {
            res += String.fromCharCode((text.charCodeAt(i) - key.charCodeAt(i % key.length) + 256) % 256);
        }
        return res;
    }
    function xhex(text, key) {
        var enc = xenc(text, key), hex = '';
        for (var i = 0; i < enc.length; i++) hex += enc.charCodeAt(i).toString(16).padStart(2, '0');
        return hex;
    }
    var cipherKey = 'secret123';
    var cipherResult = xdec(xenc('hello world', cipherKey), cipherKey);
    """

def link():
    return """
    function ListNode(v) { this.v = v; this.next = null; }
    function makeList(arr) {
        if (!arr.length) return null;
        var head = new ListNode(arr[0]), cur = head;
        for (var i = 1; i < arr.length; i++) { cur.next = new ListNode(arr[i]); cur = cur.next; }
        return head;
    }
    function reverseList(head) {
        var prev = null, cur = head, next;
        while (cur) { next = cur.next; cur.next = prev; prev = cur; cur = next; }
        return prev;
    }
    function listToArr(head) {
        var res = [], cur = head;
        while (cur) { res.push(cur.v); cur = cur.next; }
        return res;
    }
    function mergeSort(head) {
        if (!head || !head.next) return head;
        var slow = head, fast = head.next;
        while (fast && fast.next) { slow = slow.next; fast = fast.next.next; }
        var mid = slow.next; slow.next = null;
        return mergeLists(mergeSort(head), mergeSort(mid));
    }
    function mergeLists(a, b) {
        if (!a) return b; if (!b) return a;
        if (a.v <= b.v) { a.next = mergeLists(a.next, b); return a; }
        b.next = mergeLists(a, b.next); return b;
    }
    var listHead = makeList([5, 3, 8, 1, 9, 2]);
    var listSorted = listToArr(mergeSort(listHead));
    """

def search():
    return """
    function BSTNode(v) { this.v = v; this.left = null; this.right = null; }
    function bstInsert(root, v) {
        if (!root) return new BSTNode(v);
        if (v < root.v) root.left = bstInsert(root.left, v);
        else if (v > root.v) root.right = bstInsert(root.right, v);
        return root;
    }
    function bstInorder(root, res) {
        if (!root) return;
        bstInorder(root.left, res); res.push(root.v); bstInorder(root.right, res);
    }
    function bstHeight(root) {
        if (!root) return 0;
        return 1 + Math.max(bstHeight(root.left), bstHeight(root.right));
    }
    function bstSearch(root, v) {
        if (!root) return false;
        if (root.v === v) return true;
        return v < root.v ? bstSearch(root.left, v) : bstSearch(root.right, v);
    }
    var bstRoot = null;
    [5, 3, 7, 1, 4, 6, 8].forEach(function(v) { bstRoot = bstInsert(bstRoot, v); });
    var bstResult = []; bstInorder(bstRoot, bstResult);
    var bstH = bstHeight(bstRoot);
    """

def count():
    return """
    function countSort(arr, max) {
        var cnt = [], res = [], i;
        for (i = 0; i <= max; i++) cnt[i] = 0;
        for (i = 0; i < arr.length; i++) cnt[arr[i]]++;
        for (i = 0; i <= max; i++) while (cnt[i]-- > 0) res.push(i);
        return res;
    }
    function radixSort(arr) {
        var max = Math.max.apply(null, arr), exp = 1, out, cnt;
        while (Math.floor(max / exp) > 0) {
            out = new Array(arr.length); cnt = new Array(10).fill(0);
            for (var i = 0; i < arr.length; i++) cnt[Math.floor(arr[i] / exp) % 10]++;
            for (var i = 1; i < 10; i++) cnt[i] += cnt[i - 1];
            for (var i = arr.length - 1; i >= 0; i--) out[--cnt[Math.floor(arr[i] / exp) % 10]] = arr[i];
            arr = out; exp *= 10;
        }
        return arr;
    }
    var countResult = countSort([4, 2, 7, 1, 3, 5, 6], 7);
    var radixResult = radixSort([170, 45, 75, 90, 802, 24, 2, 66]);
    """

def luhn():
    return """
    function luhnCheck(num) {
        var str = String(num), sum = 0, alt = false;
        for (var i = str.length - 1; i >= 0; i--) {
            var n = parseInt(str[i], 10);
            if (alt) { n *= 2; if (n > 9) n -= 9; }
            sum += n; alt = !alt;
        }
        return sum % 10 === 0;
    }
    function luhnGen(prefix, length) {
        var partial = String(prefix);
        while (partial.length < length - 1) partial += Math.floor(Math.random() * 10);
        var sum = 0, alt = true;
        for (var i = partial.length - 1; i >= 0; i--) {
            var n = parseInt(partial[i], 10);
            if (alt) { n *= 2; if (n > 9) n -= 9; }
            sum += n; alt = !alt;
        }
        return partial + ((10 - (sum % 10)) % 10);
    }
    var luhnResult = luhnCheck(4532015112830366);
    """

def crc():
    return """
    function crc32(str) {
        var table = [], c, n, k;
        for (n = 0; n < 256; n++) {
            c = n;
            for (k = 0; k < 8; k++) c = ((c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1));
            table[n] = c;
        }
        var crc = 0xFFFFFFFF;
        for (var i = 0; i < str.length; i++) {
            crc = (crc >>> 8) ^ table[(crc ^ str.charCodeAt(i)) & 0xFF];
        }
        return ((crc ^ 0xFFFFFFFF) >>> 0).toString(16);
    }
    function adler32(str) {
        var a = 1, b = 0, MOD = 65521;
        for (var i = 0; i < str.length; i++) { a = (a + str.charCodeAt(i)) % MOD; b = (b + a) % MOD; }
        return ((b << 16) | a) >>> 0;
    }
    var crcResult = crc32('hello world');
    var adlerResult = adler32('hello world');
    """

def game():
    return """
    function gameInit(w, h) {
        var g = [];
        for (var i = 0; i < h; i++) {
            g[i] = [];
            for (var j = 0; j < w; j++) g[i][j] = Math.random() < 0.3 ? 1 : 0;
        }
        return g;
    }
    function gameCount(g, y, x) {
        var w = g[0].length, h = g.length, cnt = 0;
        for (var dy = -1; dy <= 1; dy++) for (var dx = -1; dx <= 1; dx++) {
            if (dy === 0 && dx === 0) continue;
            var ny = (y + dy + h) % h, nx = (x + dx + w) % w;
            cnt += g[ny][nx];
        }
        return cnt;
    }
    function gameStep(g) {
        var h = g.length, w = g[0].length, ng = [];
        for (var i = 0; i < h; i++) {
            ng[i] = [];
            for (var j = 0; j < w; j++) {
                var n = gameCount(g, i, j);
                ng[i][j] = g[i][j] ? (n === 2 || n === 3 ? 1 : 0) : (n === 3 ? 1 : 0);
            }
        }
        return ng;
    }
    var gameGrid = gameInit(20, 20);
    for (var gameIter = 0; gameIter < 5; gameIter++) gameGrid = gameStep(gameGrid);
    """

def ackermann():
    return """
    function ack(m, n) {
        if (m === 0) return n + 1;
        if (n === 0) return ack(m - 1, 1);
        return ack(m - 1, ack(m, n - 1));
    }
    function ackTable(maxM, maxN) {
        var t = [];
        for (var m = 0; m <= maxM; m++) {
            t[m] = [];
            for (var n = 0; n <= maxN; n++) t[m][n] = ack(m, n);
        }
        return t;
    }
    var ackResult = ack(3, 4);
    var ackT = ackTable(3, 3);
    """

def levenshtein():
    return """
    function lev(a, b) {
        var m = a.length, n = b.length;
        var dp = [];
        for (var i = 0; i <= m; i++) {
            dp[i] = [i];
            for (var j = 1; j <= n; j++) {
                dp[i][j] = i === 0 ? j :
                    (a[i-1] === b[j-1] ? dp[i-1][j-1] :
                    1 + Math.min(dp[i-1][j], dp[i][j-1], dp[i-1][j-1]));
            }
        }
        return dp[m][n];
    }
    function similarity(a, b) {
        var d = lev(a, b);
        return 1 - d / Math.max(a.length, b.length);
    }
    var levResult = lev('kitten', 'sitting');
    var simResult = similarity('hello', 'hallo');
    """

def dfs():
    return """
    function Graph(n) { this.n = n; this.adj = {}; for (var i = 0; i < n; i++) this.adj[i] = []; }
    Graph.prototype.addEdge = function(u, v) { this.adj[u].push(v); this.adj[v].push(u); };
    Graph.prototype.dfs = function(start) {
        var visited = {}, order = [], stack = [start];
        while (stack.length) {
            var node = stack.pop();
            if (visited[node]) continue;
            visited[node] = true; order.push(node);
            for (var i = this.adj[node].length - 1; i >= 0; i--) {
                if (!visited[this.adj[node][i]]) stack.push(this.adj[node][i]);
            }
        }
        return order;
    };
    Graph.prototype.bfs = function(start) {
        var visited = {}, order = [], queue = [start];
        visited[start] = true;
        while (queue.length) {
            var node = queue.shift(); order.push(node);
            for (var i = 0; i < this.adj[node].length; i++) {
                if (!visited[this.adj[node][i]]) { visited[this.adj[node][i]] = true; queue.push(this.adj[node][i]); }
            }
        }
        return order;
    };
    var g = new Graph(6);
    g.addEdge(0, 1); g.addEdge(0, 2); g.addEdge(1, 3); g.addEdge(2, 4); g.addEdge(3, 5);
    var dfsOrder = g.dfs(0); var bfsOrder = g.bfs(0);
    """

def dijkstra():
    return """
    function PQueue() { this.heap = []; }
    PQueue.prototype.push = function(item, pri) {
        this.heap.push({item: item, pri: pri});
        this.heap.sort(function(a, b) { return a.pri - b.pri; });
    };
    PQueue.prototype.pop = function() { return this.heap.shift(); };
    PQueue.prototype.empty = function() { return this.heap.length === 0; };
    function dijkstra(graph, src, n) {
        var dist = new Array(n).fill(Infinity), prev = new Array(n).fill(-1);
        dist[src] = 0;
        var pq = new PQueue();
        pq.push(src, 0);
        while (!pq.empty()) {
            var u = pq.pop().item;
            for (var i = 0; i < graph[u].length; i++) {
                var v = graph[u][i][0], w = graph[u][i][1];
                if (dist[u] + w < dist[v]) {
                    dist[v] = dist[u] + w; prev[v] = u;
                    pq.push(v, dist[v]);
                }
            }
        }
        return { dist: dist, prev: prev };
    }
    function buildPath(prev, dst) {
        var path = []; var cur = dst;
        while (cur !== -1) { path.unshift(cur); cur = prev[cur]; }
        return path;
    }
    var dijkGraph = [[[1,4],[2,1]],[[3,1]],[[1,2],[3,5]],[]];
    var dijkResult = dijkstra(dijkGraph, 0, 4);
    var dijkPath = buildPath(dijkResult.prev, 3);
    """

def bops():
    return """
    function countBits(n) {
        var c = 0; while (n) { c += n & 1; n >>= 1; } return c;
    }
    function isPow2(n) { return n > 0 && (n & (n - 1)) === 0; }
    function nextPow2(n) { if (isPow2(n)) return n; var p = 1; while (p < n) p <<= 1; return p; }
    function reverseBits(n, bits) {
        var rev = 0;
        for (var i = 0; i < bits; i++) { rev = (rev << 1) | (n & 1); n >>= 1; }
        return rev;
    }
    function bitRotLeft(n, k, bits) { k = k % bits; return ((n << k) | (n >> (bits - k))) & ((1 << bits) - 1); }
    function bitRotRight(n, k, bits) { k = k % bits; return ((n >> k) | (n << (bits - k))) & ((1 << bits) - 1); }
    function grayCode(n) { return n ^ (n >> 1); }
    function fromGray(g) {
        var n = g; var mask = g >> 1;
        while (mask) { n ^= mask; mask >>= 1; }
        return n;
    }
    var bitResult = reverseBits(0b11001010, 8);
    var grayResult = Array.from({length: 8}, function(_, i) { return grayCode(i); });
    """

def newton():
    return """
    function newtonSqrt(x) {
        if (x < 0) return NaN;
        var guess = x / 2.0;
        for (var i = 0; i < 50; i++) {
            var next = (guess + x / guess) / 2;
            if (Math.abs(next - guess) < 1e-10) break;
            guess = next;
        }
        return guess;
    }
    function newtonCbrt(x) {
        var guess = x / 3.0, sign = x < 0 ? -1 : 1;
        x = Math.abs(x);
        guess = Math.abs(guess);
        for (var i = 0; i < 50; i++) {
            var next = (2 * guess + x / (guess * guess)) / 3;
            if (Math.abs(next - guess) < 1e-10) break;
            guess = next;
        }
        return sign * guess;
    }
    function integrate(f, a, b, n) {
        var h = (b - a) / n, sum = 0;
        for (var i = 0; i < n; i++) sum += f(a + (i + 0.5) * h);
        return sum * h;
    }
    var sqrtResult = newtonSqrt(2.0);
    var cbrtResult = newtonCbrt(27.0);
    var integResult = integrate(function(x) { return x * x; }, 0, 1, 1000);
    """

def huffman():
    return """
    function HNode(ch, freq) { this.ch = ch; this.freq = freq; this.left = null; this.right = null; }
    function huffBuild(freq) {
        var nodes = Object.keys(freq).map(function(ch) { return new HNode(ch, freq[ch]); });
        while (nodes.length > 1) {
            nodes.sort(function(a, b) { return a.freq - b.freq; });
            var left = nodes.shift(), right = nodes.shift();
            var parent = new HNode(null, left.freq + right.freq);
            parent.left = left; parent.right = right;
            nodes.push(parent);
        }
        return nodes[0];
    }
    function huffCodes(node, prefix, codes) {
        if (!prefix) prefix = ''; if (!codes) codes = {};
        if (!node.left && !node.right) { codes[node.ch] = prefix || '0'; return codes; }
        if (node.left) huffCodes(node.left, prefix + '0', codes);
        if (node.right) huffCodes(node.right, prefix + '1', codes);
        return codes;
    }
    function huffEncode(str, codes) { return str.split('').map(function(c) { return codes[c]; }).join(''); }
    function huffFreq(str) {
        var freq = {};
        for (var i = 0; i < str.length; i++) freq[str[i]] = (freq[str[i]] || 0) + 1;
        return freq;
    }
    var huffStr = 'this is an example for huffman encoding';
    var huffF = huffFreq(huffStr);
    var huffTree = huffBuild(huffF);
    var huffC = huffCodes(huffTree);
    var huffEnc = huffEncode(huffStr, huffC);
    """

def opaque():
    a = random.randint(1, 0x7fff)
    b = random.randint(1, 0x7fff)
    c = random.randint(1, 0x7fff)
    d = random.randint(1, 0x7fff)
    x = {"kind": "binary", "op": "===", "left": {"kind": "binary", "op": "^", "left": {"kind": "binary", "op": "^", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "lit", "value": a, "type": "num"}}
    y = {"kind": "binary", "op": "===", "left": {"kind": "binary", "op": "+", "left": {"kind": "binary", "op": "^", "left": {"kind": "lit", "value": c, "type": "num"}, "right": {"kind": "lit", "value": d, "type": "num"}}, "right": {"kind": "binary", "op": "<<", "left": {"kind": "binary", "op": "&", "left": {"kind": "lit", "value": c, "type": "num"}, "right": {"kind": "lit", "value": d, "type": "num"}}, "right": {"kind": "lit", "value": 1, "type": "num"}}}, "right": {"kind": "binary", "op": "-", "left": {"kind": "binary", "op": "<<", "left": {"kind": "binary", "op": "|", "left": {"kind": "lit", "value": c, "type": "num"}, "right": {"kind": "lit", "value": d, "type": "num"}}, "right": {"kind": "lit", "value": 1, "type": "num"}}, "right": {"kind": "binary", "op": "^", "left": {"kind": "binary", "op": "|", "left": {"kind": "lit", "value": c, "type": "num"}, "right": {"kind": "lit", "value": d, "type": "num"}}, "right": {"kind": "binary", "op": "&", "left": {"kind": "lit", "value": c, "type": "num"}, "right": {"kind": "lit", "value": d, "type": "num"}}}}}
    z = {"kind": "binary", "op": "===", "left": {"kind": "binary", "op": "&", "left": {"kind": "lit", "value": d, "type": "num"}, "right": {"kind": "unary", "op": "~", "expr": {"kind": "lit", "value": d, "type": "num"}, "prefix": True}}, "right": {"kind": "lit", "value": 0, "type": "num"}}
    main = {"kind": "binary", "op": "===", "left": {"kind": "binary", "op": "+", "left": {"kind": "binary", "op": "&", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "binary", "op": "|", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}}, "right": {"kind": "binary", "op": "+", "left": {"kind": "binary", "op": "^", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "binary", "op": "<<", "left": {"kind": "binary", "op": "&", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "lit", "value": 1, "type": "num"}}}}
    part = {"kind": "binary", "op": "===", "left": {"kind": "binary", "op": "<<", "left": {"kind": "binary", "op": "^", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "lit", "value": 1, "type": "num"}}, "right": {"kind": "binary", "op": "-", "left": {"kind": "binary", "op": "<<", "left": {"kind": "binary", "op": "|", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "lit", "value": 1, "type": "num"}}, "right": {"kind": "binary", "op": "<<", "left": {"kind": "binary", "op": "&", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "lit", "value": 1, "type": "num"}}}}
    size = {"kind": "binary", "op": "===", "left": {"kind": "binary", "op": "^", "left": {"kind": "binary", "op": "+", "left": {"kind": "unary", "op": "~", "expr": {"kind": "lit", "value": a, "type": "num"}, "prefix": True}, "right": {"kind": "lit", "value": 1, "type": "num"}}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "binary", "op": "^", "left": {"kind": "unary", "op": "-", "expr": {"kind": "lit", "value": a, "type": "num"}, "prefix": True}, "right": {"kind": "lit", "value": b, "type": "num"}}}
    root = {"kind": "binary", "op": "===", "left": {"kind": "binary", "op": "^", "left": {"kind": "binary", "op": "+", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "lit", "value": c, "type": "num"}}, "right": {"kind": "binary", "op": "^", "left": {"kind": "binary", "op": "+", "left": {"kind": "binary", "op": "|", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "binary", "op": "&", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}}, "right": {"kind": "lit", "value": c, "type": "num"}}}
    leaf = {"kind": "binary", "op": "===", "left": {"kind": "binary", "op": "<<", "left": {"kind": "binary", "op": "&", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "unary", "op": "~", "expr": {"kind": "lit", "value": b, "type": "num"}, "prefix": True}}, "right": {"kind": "lit", "value": 2, "type": "num"}}, "right": {"kind": "binary", "op": "<<", "left": {"kind": "binary", "op": "-", "left": {"kind": "binary", "op": "|", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "lit", "value": 2, "type": "num"}}}
    code = {"kind": "binary", "op": "===", "left": {"kind": "binary", "op": "+", "left": {"kind": "binary", "op": "^", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}, "right": {"kind": "binary", "op": "*", "left": {"kind": "lit", "value": 2, "type": "num"}, "right": {"kind": "binary", "op": "&", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}}}, "right": {"kind": "binary", "op": "+", "left": {"kind": "lit", "value": a, "type": "num"}, "right": {"kind": "lit", "value": b, "type": "num"}}}
    nodes = [x, y, z, main, part, size, root, leaf, code]
    res = nodes[-1]
    for n in reversed(nodes[:-1]):
        res = {"kind": "binary", "op": "&&", "left": n, "right": res}
    return res

def skew(node):
    def fn(n):
        if n.get("skewed"): return n
        if n.get("kind") == "lit":
            val = n["value"]
            if n["type"] == "num" and isinstance(val, int) and not isinstance(val, bool):
                a = random.randint(-1000, 1000)
                b = val - a
                return {
                    "kind": "binary", "op": "+",
                    "left": {"kind": "lit", "value": a, "type": "num", "skewed": True},
                    "right": {"kind": "lit", "value": b, "type": "num", "skewed": True},
                    "skewed": True
                }
        return n
    return walk(node, fn)

def hold(node):
    def fn(n):
        if n.get("kind") == "call":
            if n["callee"].get("kind") == "id":
                callee = hold(n["callee"])
                args = [hold(a) for a in n["args"]]
                func = {
                    "kind": "func",
                    "name": None,
                    "args": [],
                    "body": {"kind": "block", "body": [{"kind": "ret", "value": callee}]}
                }
                iife = {"kind": "call", "callee": func, "args": []}
                return {"kind": "call", "callee": iife, "args": args, "optional": n.get("optional", False)}
        return n
    return walk(node, fn)

def swap(node):
    def fn(n):
        if n.get("kind") == "binary":
            if n["op"] in {"===", "==", "!==", "!=", "+", "*", "&", "|", "^"}:
                left = swap(n["right"])
                right = swap(n["left"])
                return {"kind": "binary", "op": n["op"], "left": left, "right": right}
        return n
    return walk(node, fn)

def sift(node):
    if isinstance(node, list):
        res = []
        used = set()
        for s in node:
            if isinstance(s, dict) and s.get("kind") == "block":
                name = gen(used)
                used.add(name)
                func = {
                    "kind": "func",
                    "name": name,
                    "args": [],
                    "body": {"kind": "block", "body": [{"kind": "exprstmt", "expr": {"kind": "lit", "value": random.randint(10, 100), "type": "num"}}]}
                }
                part = [func] + sift(s["body"])
                res.append({"kind": "block", "body": part})
            else:
                res.append(sift(s))
        return res
    return walk(node, lambda n: n)

def root(node):
    seen = set()
    def fn(n):
        if id(n) in seen: return n
        if n.get("kind") == "id":
            val = n["value"]
            if val in {"console", "Math", "eval", "JSON", "process", "document", "window"}:
                obj = {"kind": "id", "value": "window"}
                prop = {"kind": "lit", "value": val, "type": "str"}
                seen.add(id(obj))
                seen.add(id(prop))
                res = {
                    "kind": "member",
                    "obj": obj,
                    "prop": prop,
                    "computed": True
                }
                seen.add(id(res))
                return res
        return n
    return walk(node, fn)

def fake(node):
    if isinstance(node, list):
        res = []
        for s in node:
            if isinstance(s, dict) and s.get("kind") in {"exprstmt", "simple"}:
                pred = opaque()
                v = gen(set())
                n1 = random.randint(10, 100)
                n2 = random.randint(10, 100)
                n3 = random.randint(10, 100)
                raw = f"var {v} = Math.floor(Math.sin({n1}) * {n2}) ^ {n3};"
                toks = scan(raw)
                els = parse(toks)
                fakes = fake(s)
                if fakes["kind"] != "block": fakes = {"kind": "block", "body": [fakes]}
                res.append({"kind": "cond", "test": pred, "then": fakes, "else": els})
            else:
                res.append(fake(s))
        return res
    return walk(node, lambda n: n)

def store(node):
    def fn(n):
        if n.get("stored"): return n
        if n.get("kind") == "func":
            raw = local(n["body"]) - exclude
            aset = set()
            def dive(node):
                if not node: return
                if isinstance(node, list):
                    for x in node: dive(x)
                    return
                if isinstance(node, dict):
                    if node.get("kind") == "simple":
                        toks = node.get("toks", [])
                        if toks and toks[0].v in {'var','let','const'}:
                            for t in toks:
                                if t.v == 'arguments':
                                    vs, _ = extract(toks)
                                    aset.update(vs)
                                    return
                    if node.get("kind") == "func": return
                    for v in node.values(): dive(v)
            dive(n["body"])
            locals = raw - aset
            if not locals:
                return {"kind": "func", "name": n["name"], "args": n["args"], "body": store(n["body"]), "async": n.get("async")}
            body = store(n["body"])
            def convert(nt):
                def run(sn):
                    if sn.get("stored"): return sn
                    k = sn.get("kind")
                    if k == "id":
                        val = sn["value"]
                        if val in locals:
                            return {"kind": "call", "callee": {"kind": "id", "value": val, "stored": True}, "args": [], "stored": True}
                    if k == "assign":
                        left = sn["left"]
                        right = convert(sn["right"])
                        op = sn["op"]
                        if left.get("kind") == "id" and left.get("value") in locals:
                            var = left["value"]
                            if op == "=":
                                return {"kind": "call", "callee": {"kind": "id", "value": var, "stored": True}, "args": [right], "stored": True}
                            else:
                                raw = op[:-1]
                                curr = {"kind": "call", "callee": {"kind": "id", "value": var, "stored": True}, "args": [], "stored": True}
                                expr = {"kind": "binary", "op": raw, "left": curr, "right": right}
                                return {"kind": "call", "callee": {"kind": "id", "value": var, "stored": True}, "args": [expr], "stored": True}
                        return {"kind": "assign", "op": op, "left": convert(left), "right": right}
                    if k == "simple":
                        toks = sn["toks"]
                        if toks and toks[0].v in {'var', 'let', 'const'}:
                            vars, assigns = extract(toks)
                            stmts = []
                            for name in vars:
                                if name in locals:
                                    val = None
                                    for assign in assigns:
                                        if assign["toks"] and assign["toks"][0].v == name:
                                            bits = assign["toks"][2:-1]
                                            if bits:
                                                val = parse(bits)
                                            break
                                    if val:
                                        if val.get("kind") == "block" and len(val["body"]) == 1 and val["body"][0].get("kind") == "exprstmt":
                                            val = val["body"][0]["expr"]
                                        stmts.append({"kind": "exprstmt", "expr": {"kind": "call", "callee": {"kind": "id", "value": name, "stored": True}, "args": [convert(val)], "stored": True}})
                                else:
                                    val = None
                                    for assign in assigns:
                                        if assign["toks"] and assign["toks"][0].v == name:
                                            bits = assign["toks"][2:-1]
                                            if bits:
                                                val = parse(bits)
                                            break
                                    if val:
                                        if val.get("kind") == "block" and len(val["body"]) == 1 and val["body"][0].get("kind") == "exprstmt":
                                            val = val["body"][0]["expr"]
                                        stmts.append({"kind": "simple", "toks": [token('id', toks[0].v), token('id', name), token('op', '='), token('punc', '(')] + emit(val) + [token('punc', ')'), token('punc', ';')]})
                                    else:
                                        stmts.append({"kind": "simple", "toks": [token('id', toks[0].v), token('id', name), token('punc', ';')]})
                            if stmts:
                                if len(stmts) == 1: return stmts[0]
                                return {"kind": "block", "body": stmts}
                            return {"kind": "simple", "toks": []}
                        else:
                            items = []
                            i = 0
                            while i < len(toks):
                                t = toks[i]
                                if t.t == 'id' and t.v in locals:
                                    items.extend([token('id', t.v), token('punc', '('), token('punc', ')')])
                                else:
                                    items.append(t)
                                i += 1
                            return {"kind": "simple", "toks": items}
                    return sn
                return walk(nt, run)
            inner = convert(body)
            toks = [token('id', 'var')]
            for idx, name in enumerate(locals):
                sub = [
                    token('id', name), token('op', '='),
                    token('punc', '('), token('id', 'function'), token('punc', '('), token('id', 'val'), token('punc', ')'),
                    token('punc', '{'), token('id', 'return'), token('id', 'function'), token('punc', '('), token('id', 'newval'), token('punc', ')'),
                    token('punc', '{'), token('id', 'if'), token('punc', '('), token('id', 'arguments'), token('punc', '.'), token('id', 'length'), token('punc', ')'),
                    token('id', 'val'), token('op', '='), token('id', 'newval'), token('punc', ';'),
                    token('id', 'return'), token('id', 'val'), token('punc', ';'),
                    token('punc', '}'), token('punc', ';'), token('punc', '}'), token('punc', ')'),
                    token('punc', '('), token('id', 'undefined'), token('punc', ')')
                ]
                toks.extend(sub)
                if idx < len(locals) - 1: toks.append(token('punc', ','))
            toks.append(token('punc', ';'))
            decl = {"kind": "simple", "toks": toks}
            inner["body"].insert(0, decl)
            return {"kind": "func", "name": n["name"], "args": n["args"], "body": inner, "async": n.get("async"), "stored": True}
        return n
    return walk(node, fn)

def calc(node):
    global maps
    def fn(n):
        if n.get("calced"): return n
        if n.get("kind") == "binary":
            op = n["op"]
            if op in maps:
                return {
                    "kind": "call",
                    "callee": {"kind": "id", "value": maps[op], "calced": True},
                    "args": [calc(n["left"]), calc(n["right"])],
                    "calced": True
                }
        return n
    return walk(node, fn)

def fold(node):
    def fn(n):
        if n.get("folded"): return n
        if n.get("kind") == "lit":
            val = n["value"]
            t = n["type"]
            if t in {"num", "bool"}:
                def mark(target):
                    if isinstance(target, dict):
                        target["folded"] = True
                        for v in target.values(): mark(v)
                    elif isinstance(target, list):
                        for x in target: mark(x)
                    return target
                pred = mark(opaque())
                alt = None
                if t == "num" and isinstance(val, int):
                    alt = {"kind": "lit", "value": val + random.randint(0x10000, 0xffffff), "type": "num", "folded": True}
                elif t == "bool":
                    alt = {"kind": "lit", "value": not val, "type": "bool", "folded": True}
                if alt:
                    n["folded"] = True
                    return {
                        "kind": "ternary",
                        "test": pred,
                        "then": n,
                        "else": alt,
                        "folded": True
                    }
        return n
    return walk(node, fn)

def spin(node):
    if isinstance(node, list):
        res = []
        used = set()
        for s in node:
            if isinstance(s, dict) and s.get("kind") in {"exprstmt", "simple"}:
                flag = gen(used)
                used.add(flag)
                decl = {"kind": "simple", "toks": [
                    token('id', 'var'), token('id', flag), token('op', '='), token('id', 'true'), token('punc', ';')
                ]}
                assign = {"kind": "exprstmt", "expr": {
                    "kind": "assign", "op": "=",
                    "left": {"kind": "id", "value": flag},
                    "right": {"kind": "unary", "op": "!", "expr": opaque(), "prefix": True}
                }}
                body = {"kind": "block", "body": [spin(s), assign]}
                loop = {"kind": "loop", "test": {"kind": "id", "value": flag}, "body": body}
                res.extend([decl, loop])
            else:
                res.append(spin(s))
        return res
    return walk(node, lambda n: n)

def inject(node):
    def mark(t):
        if isinstance(t, dict):
            t["injected"] = True
            for k, v in t.items(): mark(v)
        elif isinstance(t, list):
            for x in t: mark(x)
        return t
    def fn(n):
        if n.get("injected"): return n
        k = n.get("kind")
        if k == "block":
            body = []
            for s in n["body"]:
                if s.get("kind") in {"exprstmt", "simple"}:
                    pred = mark(opaque())
                    branch = inject(s)
                    if branch.get("kind") != "block": branch = mark({"kind": "block", "body": [branch]})
                    body.append(mark({"kind": "cond", "test": pred, "then": branch, "else": None}))
                else:
                    body.append(inject(s))
            return {"kind": "block", "body": body, "injected": True}
        if k == "cond":
            test = n["test"]
            if test.get("kind") == "id" and test.get("value") == "true": test = mark(opaque())
            return {"kind": "cond", "test": test, "then": inject(n["then"]), "else": inject(n["else"]) if n["else"] else None, "injected": True}
        if k == "loop":
            test = n["test"]
            if test.get("kind") == "id" and test.get("value") == "true": test = mark(opaque())
            return {"kind": "loop", "test": test, "body": inject(n["body"]), "injected": True}
        return n
    return walk(node, fn)

def junk(node):
    def fn(n):
        if n.get("junked"): return n
        if n.get("kind") == "block":
            body = []
            used = set()
            for s in n["body"]:
                body.append(junk(s))
                v = gen(used)
                used.add(v)
                na = random.randint(1, 0xffff)
                nb = random.randint(1, 0xffff)
                nc = random.randint(1, 0xffff)
                right = {"kind":"binary","op":"^","left":{"kind":"binary","op":"&","left":{"kind":"lit","value":na,"type":"num"},"right":{"kind":"lit","value":nb,"type":"num"}},"right":{"kind":"binary","op":"+","left":{"kind":"binary","op":"-","left":{"kind":"binary","op":"|","left":{"kind":"lit","value":na,"type":"num"},"right":{"kind":"lit","value":nb,"type":"num"}},"right":{"kind":"binary","op":"^","left":{"kind":"lit","value":nb,"type":"num"},"right":{"kind":"lit","value":nc,"type":"num"}}},"right":{"kind":"lit","value":nc,"type":"num"}}}
                toks = [token('id','var'),token('id',v),token('op','=')] + emit(right) + [token('punc',';')]
                body.append({"kind":"simple","toks":toks})
            return {"kind":"block","body":body, "junked": True}
        return n
    return walk(node, fn)

def trap(node):
    def mark(t):
        if isinstance(t, dict):
            t["trapped"] = True
            for k, v in t.items(): mark(v)
        elif isinstance(t, list):
            for x in t: mark(x)
        return t
    def fn(n):
        if n.get("trapped"): return n
        if n.get("kind") == "block":
            body = []
            i = 0
            lst = n["body"]
            while i < len(lst):
                s = lst[i]
                if s.get("kind") == "exprstmt" and i + 1 < len(lst):
                    j = min(i + 2, len(lst))
                    grp = [trap(x) for x in lst[i:j]]
                    inner = {"kind":"block","body":grp}
                    used = set()
                    arg = gen(used)
                    v = gen(used)
                    val = random.randint(1, 0xffff)
                    out = [{"kind": "simple", "toks": [token('id', 'var'), token('id', v), token('op', '='), token('num', str(val)), token('punc', ';')]}]
                    body.append(mark({"kind":"try","body":inner,"catch":{"kind":"block","body":out},"arg":arg,"finally":None}))
                    i = j
                else:
                    body.append(trap(s))
                    i += 1
            return {"kind":"block","body":body, "trapped": True}
        return n
    return walk(node, fn)

def ghost(node):
    def mark(t):
        if isinstance(t, dict):
            t["ghosted"] = True
            for k, v in t.items(): mark(v)
        elif isinstance(t, list):
            for x in t: mark(x)
        return t
    def fn(n):
        if n.get("ghosted"): return n
        if n.get("kind") == "block":
            body = []
            for s in n["body"]:
                if s.get("kind") == "exprstmt" and s.get("expr",{}).get("kind") == "assign":
                    pred = mark(opaque())
                    null = mark({"kind":"unary","op":"void","expr":{"kind":"lit","value":0,"type":"num"},"prefix":True})
                    alt = mark({"kind":"exprstmt","expr":null})
                    branch = ghost(s)
                    if branch.get("kind") != "block": branch = mark({"kind": "block", "body": [branch]})
                    body.append(mark({"kind": "cond", "test": pred, "then": branch, "else": alt}))
                else:
                    body.append(ghost(s))
            return {"kind": "block", "body": body, "ghosted": True}
        return n
    return walk(node, fn)

def proxy(node):
    def fn(n):
        if n.get("proxied"): return n
        if n.get("kind") == "call":
            callee = proxy(n["callee"])
            args = [proxy(a) for a in n["args"]]
            ctx = {"kind": "id", "value": "undefined"}
            if callee.get("kind") == "member":
                ctx = callee["obj"]
            return {
                "kind": "call",
                "callee": {
                    "kind": "member",
                    "obj": {"kind": "id", "value": "Reflect"},
                    "prop": {"kind": "lit", "value": "apply", "type": "str"},
                    "computed": False
                },
                "args": [
                    callee,
                    ctx,
                    {"kind": "array", "elements": args}
                ],
                "proxied": True
            }
        return n
    return walk(node, fn)

def scramble(node):
    def fn(n):
        if n.get("scrambled"): return n
        if n.get("kind") == "object":
            props = [(scramble(k), scramble(v)) for k, v in n["properties"]]
            random.shuffle(props)
            return {"kind":"object","properties":props, "scrambled": True}
        return n
    return walk(node, fn)

def check(node):
    def fn(n):
        if n.get("checked"): return n
        if n.get("kind") == "lit":
            val = n["value"]
            if isinstance(val, (bool, int)):
                ast = fuck(val)
                if ast:
                    def mark(target):
                        if isinstance(target, dict):
                            target["checked"] = True
                            for v in target.values(): mark(v)
                        elif isinstance(target, list):
                            for x in target: mark(x)
                        return target
                    return mark(ast)
        return n
    return walk(node, fn)

def fuzz(js, idx=0):
    keep = {'var','let','const','function','return','if','else','while','for','do','break','continue','new','delete','typeof','instanceof','in','of','switch','case','default','throw','try','catch','finally','class','extends','super','this','import','export','from','as','async','await','yield','null','undefined','true','false','void','with','debugger','Object','Array','Function','String','Number','Boolean','Symbol','Math','Date','RegExp','Error','Promise','Map','Set','WeakMap','WeakSet','JSON','console','window','document','globalThis','global','self','process','parseInt','parseFloat','isNaN','isFinite','Infinity','NaN','eval','alert','confirm','prompt','setTimeout','setInterval','clearTimeout','clearInterval','atob','btoa','encodeURIComponent','decodeURIComponent','push','pop','shift','unshift','splice','slice','concat','join','reverse','sort','indexOf','lastIndexOf','includes','find','findIndex','every','some','filter','map','reduce','forEach','keys','values','entries','from','fill','flat','flatMap','at','charAt','charCodeAt','fromCharCode','codePointAt','fromCodePoint','substring','substr','replace','replaceAll','match','matchAll','search','split','trim','trimStart','trimEnd','padStart','padEnd','repeat','toLowerCase','toUpperCase','toString','valueOf','normalize','assign','create','freeze','seal','isFrozen','isSealed','hasOwnProperty','isPrototypeOf','propertyIsEnumerable','getPrototypeOf','defineProperty','getOwnPropertyNames','setPrototypeOf','floor','ceil','round','abs','sqrt','cbrt','pow','exp','log','log2','log10','max','min','random','sign','trunc','hypot','sin','cos','tan','asin','acos','atan','atan2','sinh','cosh','tanh','PI','E','LN2','SQRT2','GM_xmlhttpRequest','GM_setValue','GM_getValue','GM_deleteValue','GM_listValues','GM_addStyle','GM_getResourceText','GM_getResourceURL','GM_log','GM_openInTab','GM_registerMenuCommand','GM_unregisterMenuCommand','GM_setClipboard','GM_info','length','prototype','constructor','name','apply','call','bind','next','done','value','then','catch','resolve','reject','all','race','any','allSettled','add','get','set','has','clear','size','Uint8Array','Int8Array','Uint16Array','Int32Array','Float32Array','Float64Array','ArrayBuffer','DataView','TextEncoder','TextDecoder','performance','now','mark','measure'}
    defined = set(re.findall(r'function\s+([a-zA-Z_$][a-zA-Z0-9_$]*)\s*\(', js))
    defined |= set(re.findall(r'(?:var|let|const)\s+([a-zA-Z_$][a-zA-Z0-9_$]*)', js))
    defined -= keep
    mp = {}
    u = set()
    for nm in defined:
        x = f"_0x{idx:02x}{len(u):03x}"
        mp[nm] = x
        u.add(x)
    for old, nw in mp.items():
        js = re.sub(r'\b' + re.escape(old) + r'\b', nw, js)
    return js

def obf(code):
    global abc
    chars = list('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/')
    random.shuffle(chars)
    abc = "".join(chars)
    exclude.update(re.findall(r'\$\{([a-zA-Z_$][a-zA-Z0-9_$]*)\}', code))
    val = gcd(random.randint(10, 50), random.randint(10, 50))
    p = prime(random.randint(10, 100))
    f = fib(random.randint(5, 15))
    a = arm(random.randint(100, 999))
    pu = pure(random.randint(1, 100))
    key = "".join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=16))
    h = djb(key.encode('utf-8'))
    d = sdbm(key.encode('utf-8'))
    k = (random.randint(10, 100) + val + f + (h ^ d)) % 150
    if p: k += 1
    if a: k += 2
    if pu: k += 3
    toks = scan(code)
    i = 0
    while i < len(toks):
        if toks[i].v == '=>':
            if i > 0 and toks[i-1].v == ')':
                depth = 0
                j = i - 1
                while j >= 0:
                    if toks[j].v == ')': depth += 1
                    if toks[j].v == '(': depth -= 1
                    if depth == 0:
                        toks.insert(j, token('id', 'function'))
                        i += 1
                        toks.pop(i)
                        i -= 1
                        break
                    j -= 1
            elif i > 0 and toks[i-1].t == 'id':
                name = toks[i-1].v
                toks[i-1] = token('id', 'function')
                toks.insert(i, token('punc', '('))
                toks.insert(i+1, token('id', name))
                toks.insert(i+2, token('punc', ')'))
                toks.pop(i+3)
        i += 1
    base = """
    function _0xadd(a, b) { return a + b; }
    function _0xsub(a, b) { return a - b; }
    function _0xxor(a, b) { return a ^ b; }
    function _0xand(a, b) { return a & b; }
    """
    parts = scan(base)
    ast = parse(parts)
    tree = parse(toks)
    tree["body"] = ast["body"] + tree["body"]
    env = {}
    locals = find(tree)
    for l in locals:
        if l not in exclude: env[l] = gen(env.values())
    tree = rename(tree, env)
    global maps
    maps = {
        "+": env["_0xadd"],
        "-": env["_0xsub"],
        "^": env["_0xxor"],
        "&": env["_0xand"]
    }
    for step in [
        prop, keys, logic, params, calc, fold, mba, fake, spin, sift,
        flat, store, inject, junk, trap, ghost, proxy, scramble, skew, hold,
        swap, root, check
    ]:
        tree = step(tree)
    strings = []
    raw = key.encode('utf-8')
    tree = pool(tree, strings, raw)
    tree = nums(tree)
    final = emit(tree)
    out = []
    for tok in final: out.append(tok.v)
    result = ""
    for v in out:
        if not v: continue
        if result and gap(result[-1], v[0]): result += " " + v
        if not (result and gap(result[-1], v[0])): result += v
    funcs = [probe(), snare(), guard(), cage(), leak(), save()]
    random.shuffle(funcs)
    if strings: result = wrap(result, strings, key, k)
    else: result = escape(result)
    xk = [random.randint(1, 0xfe) for _ in range(32)]
    rk = [random.randint(1, 0xff) for _ in range(32)]
    seed = djb(key.encode('utf-8')) & 0xffffffff
    enc = bytearray()
    for i, c in enumerate(result.encode('utf-8')):
        h = (seed >> ((i % 8) * 4)) & 0xff
        enc.append(((c + i) % 256) ^ xk[i % 32] ^ rk[i % 32] ^ h)
    b64 = hide(bytes(enc))
    xp = "[" + ",".join(f"({hex(xk[i]^rk[i])}^{hex(rk[i])})" for i in range(32)) + "]"
    rp = "[" + ",".join(hex(v) for v in rk) + "]"
    hx = hex(seed)
    body = r"""
    function run(d, k, r, s) {
        var get = function(a) { return a.map(function(x){ return String["\x66\x72\x6f\x6d\x43\x68\x61\x72\x43\x6f\x64\x65"](x ^ 127); }).join(''); };
        var fn = run.toString().replace(/\s+/g,'');
        var sign = __HASH__;
        var size = __LEN__;
        var tmp = fn.replace(sign.toString(),'0').replace(size.toString(),'0');
        var h = 5381;
        for(var i=0;i<tmp.length;i++) h=((h<<5)+h)+tmp.charCodeAt(i);
        h = h>>>0;
        if(tmp.length!==size||h!==sign){ globalThis[get([28,16,17,12,16,19,26])][get([26,13,13,16,13])]('Protected'); return; }
        var alp = "__ABC__";
        var lk = [];
        for(var i=0;i<alp.length;i++) lk[alp.charCodeAt(i)]=i;
        var raw='',buf=0,bits=0;
        for(var i=0;i<d.length&&d[i]!=='=';i++){
            buf=(buf<<6)|lk[d.charCodeAt(i)];
            bits+=6;
            if(bits>=8){bits-=8;raw+=globalThis[get([44,11,13,22,17,24])][get([25,13,16,18,60,23,30,13,60,16,27,26])]((buf>>bits)&255);}
        }
        if(new(globalThis[get([45,26,24,58,7,15])])(get([117,87,95,4,75,2,3,118,86]))[get([11,26,12,11])](run.toString())){
            globalThis[get([28,16,17,12,16,19,26])][get([26,13,13,16,13])]('Protected'); return;
        }
        var u='';
        for(var i=0;i<raw.length;i++){
            var b=raw.charCodeAt(i);
            var hv=(s>>(((i&7)*4)))&255;
            u+=globalThis[get([44,11,13,22,17,24])][get([25,13,16,18,60,23,30,13,60,16,27,26])](((b^k[i&31]^r[i&31]^hv)-i%256+256)%256);
        }
        try{ u=globalThis[get([27,26,28,16,27,26,42,45,54,60,16,18,15,16,17,26,17,11])](globalThis[get([26,12,28,30,15,26])](u)); }catch(e){}
        eval(u);
    }
    """
    body = haze(body)
    body = body.replace("__ABC__", abc)
    body = "".join(f"\\u{ord(c):04x}" if ord(c) > 127 else c for c in body)
    tmp2 = body.replace("__HASH__", "0").replace("__LEN__", "0")
    slim = re.sub(r'\s+', '', tmp2)
    mark = 5381
    for c in slim:
        mark = ((mark << 5) + mark) + ord(c)
    mark = mark & 0xffffffff
    body = body.replace("__HASH__", str(mark)).replace("__LEN__", str(len(slim)))
    lines = [line.strip() for line in body.split('\n') if line.strip()]
    plain = " ".join(lines)
    shell = f"({plain})('{b64}',{xp},{rp},{hx});"
    anchor = "if(false){GM_xmlhttpRequest({});}"
    res = " ".join(funcs) + " " + anchor + " " + shell
    return "".join(f"\\u{ord(c):04x}" if ord(c) > 127 else c for c in res)

def read(path):
    with open(path, "r", encoding="utf-8") as f: return f.read()

def write(path, data):
    with open(path, "w", encoding="utf-8") as f: f.write(data)

def strip(code):
    m = re.match(r'(// ==UserScript==.*?// ==/UserScript==\s*)', code, re.DOTALL)
    if m: return m.group(1), code[m.end():]
    return '', code

def main():
    if len(sys.argv) < 2: sys.exit(1)
    inp = sys.argv[1]
    if len(sys.argv) >= 3:
        out = sys.argv[2]
    else:
        out = inp
        if inp.endswith('.js'): out = inp[:-3]
        out = out + '_obf.js'
    code = read(inp)
    header, body = strip(code)
    res = obf(body)
    write(out, header + res)

if __name__ == '__main__':
    main()