'use strict';

const passed = []; const failed = [];
function check(name, got, want) {
    const ok = JSON.stringify(got) === JSON.stringify(want);
    if (ok) { passed.push(name); }
    else { failed.push({ name, got: JSON.stringify(got), want: JSON.stringify(want) }); console.error('FAIL [' + name + '] got=' + JSON.stringify(got) + ' want=' + JSON.stringify(want)); }
}
function throws(name, fn) {
    try { fn(); failed.push({ name, got: 'no throw', want: 'throw' }); console.error('FAIL [' + name + '] expected throw'); }
    catch(e) { passed.push(name); }
}

const MSG = 'Hello World';
const KEY = 'obfuscator-test-key-2024';
const CODES = [72, 101, 108, 108, 111];

check('str-concat', MSG.slice(0,5) + ' ' + MSG.slice(6), 'Hello World');
check('str-upper', MSG.toUpperCase(), 'HELLO WORLD');
check('str-lower', MSG.toLowerCase(), 'hello world');
check('str-methods', KEY.split('-').join('_').toUpperCase(), 'OBFUSCATOR_TEST_KEY_2024');
check('str-template', `Result: ${1 + 2 + 3}`, 'Result: 6');
check('str-charcode', CODES.map(c => String.fromCharCode(c)).join(''), 'Hello');
check('str-match', 'abc123def456'.match(/\d+/g), ['123', '456']);
check('str-replace', 'foo bar baz'.replace(/\b\w/g, c => c.toUpperCase()), 'Foo Bar Baz');
check('str-pad', '7'.padStart(4, '0'), '0007');
check('str-padend', 'hi'.padEnd(5, '.'), 'hi...');
check('str-trim', '  hello  '.trim(), 'hello');
check('str-includes', 'hello world'.includes('world'), true);
check('str-starts', 'hello'.startsWith('hel'), true);
check('str-repeat', 'ab'.repeat(3), 'ababab');
check('str-at', 'abcde'.at(-1), 'e');

check('num-mba', ((0x42 ^ 0x1f) ^ 0x1f) | 0, 66);
check('num-bits', (0xff & 0x55) | (0xaa & 0xff), 255);
check('num-shift', ((1 << 8) >>> 1) | 0, 128);
check('num-float', Math.round((1.2 + 2.3 + 3.5) * 10) / 10, 7.0);
check('num-hex', 0xdeadbeef >>> 16, 0xdead);
check('num-pow', 2 ** 10, 1024);
check('num-inf', Number.isFinite(1/0), false);
check('num-nan', Number.isNaN(0/0), true);
check('num-parse', parseInt('0xff', 16), 255);
check('num-abs', Math.abs(-42), 42);
check('num-clamp', Math.min(Math.max(-5, 0), 100), 0);

const obj = { name: 'test', value: 42, tags: ['a', 'b', 'c'] };
check('obj-prop', obj.name + '-' + obj.value, 'test-42');
check('obj-nested', obj.tags.join(','), 'a,b,c');
check('obj-spread', { ...obj, extra: true }.extra, true);
check('obj-destruct', (({ name: n, value: v }) => n + v)(obj), 'test42');
check('obj-json', JSON.parse(JSON.stringify({ x: 1, y: [2, 3] })), { x: 1, y: [2, 3] });
check('obj-keys', Object.keys(obj).sort(), ['name', 'tags', 'value']);
check('obj-values', Object.values({ a: 1, b: 2, c: 3 }), [1, 2, 3]);
check('obj-entries', Object.entries({ x: 1, y: 2 }), [['x', 1], ['y', 2]]);
check('obj-assign', Object.assign({}, { a: 1 }, { b: 2 }).a, 1);
check('obj-freeze', (() => { const o = Object.freeze({ x: 1 }); try { o.x = 2; } catch(e){} return o.x; })(), 1);
check('obj-hasown', Object.hasOwn({ a: 1 }, 'a'), true);

const arr = [9, 3, 7, 1, 5, 8, 2, 6, 4, 0];
check('arr-sort', [...arr].sort((a, b) => a - b), [0,1,2,3,4,5,6,7,8,9]);
check('arr-map', arr.slice(0,5).map(x => x * 2), [18,6,14,2,10]);
check('arr-filter', arr.filter(x => x % 2 === 0), [8,2,6,4,0]);
check('arr-reduce', arr.reduce((s, x) => s + x, 0), 45);
check('arr-flat', [[1,2],[3,[4,5]]].flat(Infinity), [1,2,3,4,5]);
check('arr-find', arr.find(x => x > 7), 9);
check('arr-findindex', arr.findIndex(x => x > 7), 0);
check('arr-every', [2,4,6,8].every(x => x % 2 === 0), true);
check('arr-some', [1,3,5,6].some(x => x % 2 === 0), true);
check('arr-includes', [1,2,3].includes(2), true);
check('arr-from', Array.from({length: 4}, (_, i) => i * i), [0,1,4,9]);
check('arr-fill', new Array(4).fill(0).map((_, i) => i), [0,1,2,3]);
check('arr-slice', [1,2,3,4,5].slice(1,4), [2,3,4]);
check('arr-splice', (() => { const a=[1,2,3,4]; a.splice(1,2,'x'); return a; })(), [1,'x',4]);
check('arr-flat2', [1,[2,[3,[4]]]].flat(2), [1,2,3,[4]]);

function fib(n) {
    if (n <= 1) return n;
    const a = fib(n - 1);
    const b = fib(n - 2);
    return a + b;
}
check('fib', fib(12), 144);

function mergeSort(arr) {
    if (arr.length <= 1) return arr;
    const mid = Math.floor(arr.length / 2);
    const left = mergeSort(arr.slice(0, mid));
    const right = mergeSort(arr.slice(mid));
    const result = [];
    let i = 0, j = 0;
    while (i < left.length && j < right.length) {
        if (left[i] <= right[j]) result.push(left[i++]);
        else result.push(right[j++]);
    }
    return result.concat(left.slice(i)).concat(right.slice(j));
}
check('mergesort', mergeSort([5,3,8,1,9,2,7,4,6]), [1,2,3,4,5,6,7,8,9]);

function memoize(fn) {
    const cache = new Map();
    return function(...args) {
        const key = JSON.stringify(args);
        if (cache.has(key)) return cache.get(key);
        const result = fn.apply(this, args);
        cache.set(key, result);
        return result;
    };
}
const mfib = memoize(function f(n) {
    if (n === undefined) n = 0;
    return n <= 1 ? n : mfib(n-1) + mfib(n-2);
});
check('memo-fib', mfib(20), 6765);

function counter(init) {
    let n = init;
    const ops = {
        inc: (x) => { if (x === undefined) x = 1; n += x; return ops; },
        dec: (x) => { if (x === undefined) x = 1; n -= x; return ops; },
        mul: (x) => { n *= x; return ops; },
        get: () => n
    };
    return ops;
}
check('fluent', counter(5).inc(3).mul(2).dec(4).get(), 12);

class Vec {
    constructor(x, y) { this.x = x; this.y = y; }
    add(other) { return new Vec(this.x + other.x, this.y + other.y); }
    scale(s) { return new Vec(this.x * s, this.y * s); }
    dot(other) { return this.x * other.x + this.y * other.y; }
    len() { return Math.sqrt(this.x ** 2 + this.y ** 2); }
    toString() { return '(' + this.x + ',' + this.y + ')'; }
}
const v1 = new Vec(3, 4);
const v2 = new Vec(1, 2);
check('class-len', v1.len(), 5);
check('class-add', v1.add(v2).toString(), '(4,6)');
check('class-dot', v1.dot(v2), 11);
check('class-chain', v1.scale(2).add(v2).toString(), '(7,10)');

class Queue {
    constructor() { this.items = []; }
    enqueue(x) { this.items.push(x); return this; }
    dequeue() { return this.items.shift(); }
    peek() { return this.items[0]; }
    size() { return this.items.length; }
    empty() { return this.items.length === 0; }
}
const q = new Queue();
q.enqueue(1).enqueue(2).enqueue(3);
check('class-queue-size', q.size(), 3);
check('class-queue-deq', q.dequeue(), 1);
check('class-queue-peek', q.peek(), 2);

function pipe(...fns) { return x => fns.reduce((v, f) => f(v), x); }
const process = pipe(
    s => s.trim(),
    s => s.toLowerCase(),
    s => s.replace(/\s+/g, '_'),
    s => s.replace(/[^a-z0-9_]/g, ''),
    s => s.slice(0, 20)
);
check('pipe', process('  Hello World! Test 123  '), 'hello_world_test_123');

function trampoline(fn) {
    return function(...args) {
        let result = fn(...args);
        while (typeof result === 'function') result = result();
        return result;
    };
}
const sum = trampoline(function go(n, acc) {
    if (acc === undefined) acc = 0;
    return n <= 0 ? acc : () => go(n - 1, acc + n);
});
check('trampoline', sum(100), 5050);

try {
    null.property;
    check('try-no-catch', false, true);
} catch(e) {
    check('try-catch', e instanceof TypeError, true);
}
check('try-finally', (() => {
    let x = 0;
    try { x = 1; throw 0; } catch { x = 2; } finally { x += 10; }
    return x;
})(), 12);

throws('throws-null', () => null.x);
throws('throws-type', () => { const n = null; return n(); });

const evens = (function* gen(n) {
    let i = 0;
    while (i <= n) { yield i; i += 2; }
})(10);
check('generator', [...evens], [0,2,4,6,8,10]);

function* range(start, end, step) {
    if (step === undefined) step = 1;
    for (let i = start; i < end; i += step) yield i;
}
check('generator-range', [...range(0, 10, 2)], [0,2,4,6,8]);

const primes = Array.from({length: 30}, (_, i) => i + 2).filter(n => {
    for (let i = 2; i <= Math.sqrt(n); i++) if (n % i === 0) return false;
    return true;
});
check('primes', primes, [2,3,5,7,11,13,17,19,23,29,31]);

const enc = btoa('hello world');
check('btoa', enc, 'aGVsbG8gd29ybGQ=');
check('atob', atob(enc), 'hello world');

check('date-type', typeof Date.now(), 'number');
check('date-valid', Date.now() > 0, true);

check('map-basic', (() => { const m = new Map([[1,'a'],[2,'b']]); return m.get(1) + m.get(2); })(), 'ab');
check('map-size', new Map([['x',1],['y',2],['z',3]]).size, 3);
check('set-basic', (() => { const s = new Set([1,2,3,2,1]); return s.size; })(), 3);
check('set-has', new Set([1,2,3]).has(2), true);

check('promise-resolve', await Promise.resolve(42), 42);
check('promise-all', await Promise.all([Promise.resolve(1), Promise.resolve(2), Promise.resolve(3)]), [1,2,3]);

check('regex-named', 'John 30'.match(/(?<name>\w+) (?<age>\d+)/).groups, { name: 'John', age: '30' });
check('regex-replace', 'hello world'.replace(/(\w+)/g, w => w[0].toUpperCase() + w.slice(1)), 'Hello World');
check('regex-split', 'a,b,,c'.split(/,+/), ['a','b','c']);

const weakmap = new WeakMap();
const obj2 = {};
weakmap.set(obj2, 42);
check('weakmap', weakmap.get(obj2), 42);

check('symbol', (() => { const s = Symbol('test'); return typeof s === 'symbol' && s.toString() === 'Symbol(test)'; })(), true);

check('nullish', null ?? 'default', 'default');
check('optional', null?.x?.y, undefined);
check('logical-and', 1 && 2, 2);
check('logical-or', 0 || 3, 3);
check('logical-assign', (() => { let x = null; x ??= 5; return x; })(), 5);

check('spread-args', Math.max(...[3,1,4,1,5,9,2,6]), 9);
check('destructure-arr', (() => { const [a,,b] = [1,2,3]; return a+b; })(), 4);
check('destructure-rest', (() => { const [h,...t] = [1,2,3,4]; return t; })(), [2,3,4]);
check('object-shorthand', (() => { const x=1,y=2; return {a:x, b:y}; })(), {a:1,b:2});
check('computed-key', (() => { const k='foo'; return {[k]:42}; })(), {foo:42});

check('array-buffer', (() => {
    const buf = new ArrayBuffer(4);
    const view = new Int32Array(buf);
    view[0] = 0x12345678;
    return view[0] === 0x12345678;
})(), true);

check('string-iter', [...'hello'], ['h','e','l','l','o']);
check('entries-iter', Object.fromEntries([['a',1],['b',2]]), {a:1,b:2});

const dp = (() => {
    const memo = {};
    function coins(amount, denominations) {
        if (amount === 0) return 0;
        if (amount < 0) return Infinity;
        const key = amount + ':' + denominations.join(',');
        if (memo[key] !== undefined) return memo[key];
        let min = Infinity;
        for (const d of denominations) {
            const res = coins(amount - d, denominations);
            if (res + 1 < min) min = res + 1;
        }
        return (memo[key] = min);
    }
    return coins;
})();
check('dp-coins', dp(11, [1,5,6,9]), 2);

console.log('\n--- Results ---');
console.log('PASS: ' + passed.length + '  FAIL: ' + failed.length);
if (failed.length > 0) {
    console.error('\nFailed tests:');
    failed.forEach(f => console.error('  FAIL [' + f.name + '] got=' + f.got + ' want=' + f.want));
    throw new Error('tests failed: ' + failed.length + ' failures');
}
console.log('ALL TESTS PASSED');
