"use strict";
const N0=0;
const P1=5;
const P2=(-7);
const P3=3.14159;
const P4=6.02e23;
const P5=1.0e-6;
const P6=((0.1+0.2));
const P7=((1/3));
const HX=0xDEADBEEF;
const HC=0xC0FFEE;
const BN=0b1011010110;
const OC=0o777;
const US=1_000_000;
const LD=9007199254740991;
const LS=9007199254740991n;
const BI=12345678901234567890n;
const NB=(-0);
const ZD=0.5;
const TD=5.0;
const HUGESAFE=2147483647;
const SPL=([]);
for (let i=0;(i<60);i++)(SPL.push((i*37)));
function clamp(v,lo,hi){return ((((v<lo))?lo:((((v>hi))?hi:v))));
}
function flatten(obj,pre=""){let o=({});
for (const k of (Object.keys(obj))){const v=(obj[k]);
(((o[(pre+k)])=(((((((typeof v)==="object"))&&((v!==null))))?(flatten(v,(((pre+k))+"."))):v))));
}
return o;
}
function memo1(fn){const cache=(new Map());
return ((x)=>{if((cache.has(x)))return (cache.get(x));
const r=(fn(x));
(cache.set(x,r));
return r;
});
}
function mkFact(){const f=((n)=>(((n<=1))?1:((n*(f((n-1)))))));
return f;
}
const factN=(mkFact());
const factMem=(memo1(factN));
function twin(){let a=0;
let b=1;
return (()=>{const t=a;
((a=b));
((b=((t+b))));
return ({a:a,b:b});
});
}
const fibPair=(twin());
const fibonacci=(([fibPair(),fibPair(),fibPair(),fibPair(),fibPair(),fibPair(),fibPair(),fibPair(),fibPair(),fibPair()]).map((r)=>r.a));
function freshCount(){let n=0;
return ({inc(times){for (let k=0;(k<times);k++)((n+=1));
return (++n);
}});
}
const fct=(freshCount());
const counter=([fct.inc(0),fct.inc(1),fct.inc(2),fct.inc(0)]);
function destructureMe({x:x,y=11,z:{deep=3,deeper:[w1=1,w2]=([])}=({}),...other}){return ({x:x,y:y,deep:deep,w1:w1,w2:w2,other:other});
}
const dm1=(destructureMe({x:1,z:({deep:9,deeper:([7,8,9])}),q:"qq",w:42}));
const dm2=(destructureMe({x:2,extra:true}));
const dm3=(destructureMe({x:3,z:5}));
function arrDestr([a,b=5,...rest],{p:p,q=9}=({p:0})){return ({a:a,b:b,rest:rest,p:p,q:q});
}
const am1=(arrDestr([1,undefined,3,4,5],{p:"pp",q:12}));
const am2=(arrDestr([7]));
const am3=(arrDestr([9,8,7],undefined));
function defaults(a=1,b=((a+1)),c=((a+b)),d=((()=>(((a+b))+c))())){return ({a:a,b:b,c:c,d:d});
}
const dfl=(defaults());
const dfl2=(defaults(10,20,30,40));
function* multiGen(stop){let n=0;
outer:while(((n<stop))){(n++);
for (let k=0;(k<n);k++){if(((k===0)))continue;
}
(yield n);
}
}
const genA=([...(multiGen(6))]);
const genB=([]);
for (const v of (multiGen(4)))(genB.push((v*10)));
const compose=((...fns)=>(v)=>fns.reduce((acc,fn)=>fn(acc),v));
const pipeline=(compose((x)=>(x+1),(x)=>(x*2),(x)=>(x-5),Math.abs,(x)=>Math.floor((x/2))));
const pipeOut=(pipeline(-3));
const idfn=((x)=>x);
const obj=({base:10,arr:([1,2,[3,[4,[5]]]]),fn:(function me(){return "me";
}),arrow:((x)=>(x*x)),get half(){return (((this.base)/2));
},set half(v){(((this.base)=((v*2))));
},m(a,b){return ({sum:((a+b)),diff:((a-b)),prod:((a*b)),quot:((a/b))});
}});
(((obj.half)=20));
const OM=(obj.m(9,4));
class Animal{static kingdom(){return "animalia";
}
constructor(name){(((this.name)=name));
(((this.legs)=0));
}
speak(){return (((this.name)+" makes a sound"));
}
describe(){return (((((((this.speak())+" with "))+(this.legs)))+" legs"));
}
}
class Dog extends Animal{static kingdom(){return (((super.kingdom())+" / canidae"));
}
constructor(name){(super(name));
(((this.legs)=4));
}
speak(){return (((this.name)+" barks"));
}
}
class Puppy extends Dog{constructor(name){(super(name));
(((this.cute)=true));
}
describe(){return (((((super.describe())+" and is "))+(((this.cute)?"cute":"not"))));
}
}
class Sigmoid{#a
#b
constructor(a,b){(((this.#a)=a));
(((this.#b)=b));
}
get sum(){return (((this.#a)+(this.#b)));
}
swap(){const t=(this.#a);
(((this.#a)=(this.#b)));
(((this.#b)=t));
return this;
}
static make(a,b){return (new Sigmoid(a,b));
}
}
const sig=(((Sigmoid.make(3,4)).swap()).swap());
const sigSum=(sig.sum);
const doge=(new Puppy("Rex"));
const dDesc=(doge.describe());
const dKhu=(Dog.kingdom());
class WithField{static MAX=100
tag="tag"
#priv=7
constructor(){(((this.extra)="x"));
}
read(){return (((((((this.tag)+(this.#priv)))+(WithField.MAX)))+(this.extra)));
}
}
const wf=(new WithField());
const wfOut=(wf.read());
function deepSwitch(x){let out="start";
switch(x){case 1:{((out="one"));
break;}case "two":{((out="two"));
break;}case (1+1):{((out="two-num"));
break;}case ([3,4]).join(","):{((out="arr"));
break;}default:{((out="other"));}}
if(((x==="two")))return out;
const n=(((((typeof x)==="number"))?x:(x.length)));
switch(true){case (n>10):{return ((out+":big"));}case (n===2):{return ((out+":small"));}default:{return ((out+":mid"));}}
}
const dsw=([deepSwitch(1),deepSwitch("two"),deepSwitch(2),deepSwitch([1,2]),deepSwitch(99),deepSwitch("hello")]);
function tryNest(v){const log=([]);
try{try{if(((v==="rn")))throw (new RangeError("bad"));
if(((v==="re")))return "early";
if(((v===0)))throw 0;
if(((v==="nul")))throw null;
if(((v==="obj")))throw ({code:5});
if(((v==="err")))throw (new TypeError("type"));
(log.push("ok"));
}finally{(log.push("inner-finally"));
if(((v==="re")))return "early+finally";
}
}catch(e){(log.push(("inner-catch:"+((((e&&(((e.message)!==undefined))))?(e.message):(String(e)))))));
if(((v==="err")))throw e;
}finally{(log.push("outer-finally"));
}
return (log.join("|"));
}
const tns=([tryNest("rn"),tryNest("re"),tryNest(0),tryNest("nul"),tryNest("obj"),tryNest("ok")]);
function tryErr(){try{throw (new Error("boom"));
}catch(e){return ((((e instanceof Error))&&(((e.message)==="boom"))));
}
}
const isErr=(tryErr());
function loops(){const r=([]);
let i=0;
outer:while(((i<5))){(i++);
for (let j=0;(j<5);j++){if(((j===i)))continue outer;
if(((((i===4))&&((j===2)))))break outer;
(r.push((((i+":"))+j)));
}
}
return r;
}
const lps=(loops());
function combos(){let acc=0;
for (let a=0;(a<3);a++){for (let b=0;(b<3);b++){for (let c=0;(c<3);c++){if(((((((((((a+b))+c))%3))===0))&&(!((((a===1))&&((b===1))))))))((acc+=((((((a*100))+((b*10))))+c))));
}
}
}
return acc;
}
const cbo=(combos());
function trickyBool(){const vals=(["",0,-0,NaN,null,undefined,false,[],{},"0","false"," "]);
return (vals.map((v)=>({v:v,t:(!(!v)),eq:((v==0)),se:((v===0)),nul:((v==null)),nan:((v!==v))})));
}
const tbv=(trickyBool());
const NEG=(-0);
function castOps(){const s="7";
const x=3;
return ({plus:((s+x)),concat:((((""+x))+s)),num:(+s),bit:((s|0)),str:(String(x)),bool:(Boolean(s)),raw:(`${x}${s}`),back:(`a${("b"+s)}c`)});
}
const cast=(castOps());
const teng=(`t${"0"}`);
const tpl=((a,b)=>`sum=${(a+b)};prod=${(a*b)};both=${`${a}${b}`}`);
const tplOut=(tpl(3,4));
const tricky=(`\${not}`);
const tricky2=(`$${"{"}bracket`);
const escapes3="back\\slash\\newline and lots more";
const strMix=({single:"it's a \"quote\"",double:"back\\slash and 'quote'",escaped:"\\u0041 \\x42 \\0 \\v \\f",nulbyte:"a\u0000b",oct:"ab",unicode:"A⚓",backticks:"`tick` and ${notex}",long:"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam.",long2:"æ•²å‡»æ±‰å­—æµ‹è¯•ï¼ŒåŒ…å«è¹‡è‰°å­—ä¸Žæ ‡ç‚¹ç¬¦å·ï¼ï¼ ï¼ƒï¿¥â€¦â€¦&*ï¼ˆï¼‰â€”â€”+=ã€ã€‘ï¼šï¼›â€œâ€â€˜â€™ã€Šã€‹ï¼Œã€‚ã€ï¼Ÿï½œï¼",long3:"base64AAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==BBBBBBBBBBBBBBBB"});
const regexes=([/ab+c/gi,/^[\w-]+@[\w-]+\.[a-z]{2,}$/i,/\d{2,4}[-/]\d{2}[-/]\d{2,4}/,/[a-z]+@[a-z]+/g,/(\d+)(\s*)([a-z]+)/,/\u{1F600}-\u{1F64F}/u,/(?<name>\w+):(?<value>\d+)/,/a.b.*c?d+e{2,3}/s,/(?=lookahead)\w+/,/(?!x)x|(y)/y]);
function regexFx(){const text="abbbc ABBC xabyc 123-45-6789 contact@example.com 42 units camel34Case";
const mail="user.name+tag@sub.domain.co";
return ({matchA:(text.match(regexes[0])),matchM:(mail.match(regexes[3])),matchAddr:(text.match(regexes[1])),matchRep:("Abc xyZ".match(regexes[3])),exec1:((regexes[2]).exec("2024-03-30")),named:(((regexes[6]).exec("key:123")).groups),unicode:((((String.fromCodePoint(0x1F600)).match(regexes[5]))!==null)),sticky:((regexes[9]).exec("xxxy")),replace:(text.replace(/[\\/]/g,"_")),split:("a,b,c,,d".split(",")),idx:("banana".indexOf("na")),last:("banana".lastIndexOf("na")),slice:("abcdef".slice(1,4)),sub:("abcdef".substring(3)),pad:((("7".padStart(3,"0"))+("8".padEnd(3,".")))),rep:("ab".repeat(4)),inc:("hello world".includes("lo w")),sw:("hello".startsWith("he")),ew:("hello".endsWith("lo")),trim:("  x  ".trim()),up:("abc".toUpperCase()),low:("XYZ".toLowerCase()),chr:("a".charCodeAt(0)),code:(String.fromCharCode(97,98,99)),cp:((String.fromCodePoint(0x1F600)).codePointAt(0)),at:("abcdef".at(-1))});
}
const rfx=(regexFx());
const arrays=({map:(([1,2,3]).map((x)=>(x*x))),filter:(([1,2,3,4,5]).filter((x)=>(((x%2))===1))),reduce:(([1,2,3,4]).reduce((a,b)=>(a+b),0)),reduceR:(([1,2,3,4]).reduceRight((a,b)=>(((a*10))+b),0)),flat:(([1,[2,[3,[4]]]]).flat(2)),flatM:(([1,2,3,4]).flatMap((x)=>[x,(x*2)])),sort:(([3,1,2]).sort((a,b)=>(a-b))),sortS:((["b","A","a","B"]).sort()),someAE:(([1,2,3]).some((x)=>(x>2))),every:(([2,4,6]).every((x)=>(((x%2))===0))),find:(([5,12,8,130,44]).find((x)=>(x>10))),findIdx:(([5,12,8,130,44]).findIndex((x)=>(x>100))),incl:(([1,2,3]).includes(2)),iof:((["a","b"]).indexOf("b")),join:(([1,2,3]).join("-")),slice:(([1,2,3,4,5]).slice(1,4)),splice:((()=>{const a=([1,2,3,4,5]);
(a.splice(1,2,9,8,7));
return a;
})()),from:(Array.from("abc")),of:(Array.of(1,2,3)),fill:((new Array(3)).fill(7)),key:(Object.keys({a:1,b:2})),val:(Object.values({a:1,b:2})),ent:(Object.entries({a:1,b:2})),fromE:(Object.fromEntries([["a",1],["b",2]])),assign:(Object.assign({},{a:1},{b:2})),is:(Array.isArray([]))});
const objOps=({keys:(Object.keys(destructureMe)),vals:((Object.keys(obj)).length),freeze:((()=>{const o=({a:1});
(Object.freeze(o));
return (Object.isFrozen(o));
})()),seal:((()=>{const o=({a:1});
(Object.seal(o));
return (Object.isSealed(o));
})()),getOwn:(Object.getOwnPropertyNames(Dog.prototype)),proto:(((Object.getPrototypeOf(Puppy.prototype))===(Dog.prototype)))});
function equality(){return ({loose:((1=="1")),strict:((1==="1")),notLoose:((1!="2")),notStrict:((1!=="1")),lt:((3<4)),lte:((4<=4)),gt:((3>2)),gte:((2>=3)),and:((true&&"x")),or:((""||"fallback")),nul:(("a"??"b")),not:(!0),dblNot:(!(!1)),tern:((((5>4))?"y":"n"))});
}
const eq=(equality());
const ovf=({add:((HUGESAFE+1)),mul:((HUGESAFE*3)),div:(((-1)/0)),mod:((7%3)),pow:((2**10)),neg:(-((2**2))),inv:((1/4)),and:((0b1100&0b1010)),or:((0b1100|0b0011)),xor:((0b1100^0b1010)),not:(~0),shl:((1<<5)),shr:((256>>3)),ushr:(((-1)>>>28)),u32:((0xFFFFFFFF>>>0))});
function closures(){let total=0;
const adders=([]);
for (let i=0;(i<4);i++){(((j)=>{(adders.push((v)=>{((total+=((j*v))));
return total;
}));
})(i));
}
return ({totalAfter:(adders.map((a)=>a(2))),final:total});
}
const clo=(closures());
function modulePattern(priv){const cache=(new Map());
function get(k){if((cache.has(k)))return (cache.get(k));
const v=(priv(k));
(cache.set(k,v));
return v;
}
return ({get:get,size:(()=>cache.size)});
}
const lookup=(modulePattern((k)=>k.toUpperCase()));
const lookupOut=([lookup.get("a"),lookup.get("a"),lookup.get("b"),lookup.size()]);
function protoChain(){const base=({hi(){return "base-hi";
}});
const mid=(Object.create(base,{extra:({value:42,enumerable:true})}));
(((mid.hi)=(function(){return (("mid:"+(((Object.getPrototypeOf(mid)).hi).call(this))));
})));
const child=(Object.create(mid));
return ({base:(base.hi()),mid:(mid.hi()),child:(child.hi()),extra:(child.extra),own:(((Object.prototype).hasOwnProperty).call(mid,"extra")),constructorIs:((child instanceof Object))});
}
const pro=(protoChain());
function spreadDestructure(){const base=({a:1,b:2,c:3});
const {a:a,...rest}=base;
const merged=({...base,d:4,b:99});
const arrBase=([1,2,3]);
const [head,...tail]=arrBase;
const arrMerged=([...arrBase,,4,...tail]);
const fnSpread=((x,y,z)=>(((x+y))+z));
return ({a:a,rest:rest,merged:merged,head:head,tail:tail,arrMerged:arrMerged,spreadArg:(fnSpread(...arrBase))});
}
const sprd=(spreadDestructure());
function regexReplaceCallbacks(){return ("one two three four".replace(/(\w+)/g,(m)=>(m[0]).toUpperCase()));
}
const rrc=(regexReplaceCallbacks());
function trickyNumbers(){const results=({intDiv:(Math.floor((7/2))),ceil:(Math.ceil((7/2))),round:(Math.round(2.5)),round2:(Math.round(-2.5)),trunc:(Math.trunc(-2.7)),abs:(Math.abs(-3)),max:(Math.max(1,5,3)),min:(Math.min(1,5,3)),pow:(Math.pow(2,8)),sqrt:(Math.sqrt(81)),cbrt:(Math.cbrt(27)),sign:([Math.sign(-5),Math.sign(0),Math.sign(5)]),floorDiv:((((17-((17%5))))/5)),minZero:(Math.min(1,-0))});
for (const k in results){const v=(results[k]);
(((results[k])=((((v===undefined))?"undef":v))));
}
return results;
}
const tnu=(trickyNumbers());
const guardInit=((()=>{let n=0;
const f=(()=>++n);
return ([f(),f(),f()]);
})());
const gsp=((()=>{const s=(new Set([1,2,3,2]));
const m=(new Map([["a",1],["b",2],["c",3]]));
return ({sArr:([...s]),sLen:(s.size),mArr:([...m]),mGet:(m.get("b")),mHas:(m.has("z")),mDel:((()=>{const x=(new Map(m));
(x.delete("a"));
return (x.size);
})())});
})());
const NUMS=([0,1,-1,2,-2,7,8,15,16,31,32,127,128,255,256,512,1000,1024,32767,32768,65535,65536,2147483647,-2147483648,4294967295]);
const DEC=([0.5,-0.5,1.25,-1.25,3.14159,2.71828,1e-5,1e5,1e21,123.456,-0.001,(0.1+0.2),9007199254740992]);
const BITS=({add:((2147483647+1)),sub:(((-2147483648)-1)),mul:((4294967295*3)),xor:((0x0f^0xf0)),shl31:((1<<31)),shlN:(((-1)<<1)),shrN:(((-8)>>1)),ushrN:(((-1)>>>0)),ushr28:(((-1)>>>28)),not5:(~5),band:((0xff&0x0f)),bor:((8|3)),combine:((((0b1010<<4))|0b0101)),mask:((((0xffff0000>>>16))&0x00ff)),swapb:((((((0x1234&0x00ff))<<8))|((((0x1234&0xff00))>>8)))),mul2:((123456789*987654321)),addF:((0.1+0.2)),mulF:((1.1*100)),divs:((22/7)),modNeg:(((-7)%3)),modF:((5.5%2)),powNeg:(Math.pow(-2,3)),powF:((2**0.5)),root:(Math.sqrt(-1)),ln1:(Math.log(-1)),asin2:(Math.asin(2)),huge:(((Number.MAX_VALUE)*2)),tiny:(((Number.MIN_VALUE)/2)),ep1:((1+(Number.EPSILON))),ep0:((1+(((Number.EPSILON)/2)))),safeHi:(Number.MAX_SAFE_INTEGER),safeLo:(-(Number.MAX_SAFE_INTEGER)),isInt:(Number.isInteger(1.0)),isIntBig:(Number.isInteger(1e100)),z1:((0.30000000000000004===((0.1+0.2)))),z2:((((((((((((((((0.1+0.2))+0.3))+0.4))+0.5))+0.6))+0.7))+0.8))+0.9)),neg0a:(((-0)===0)),neg0b:(Object.is(-0,0)),neg0c:(Object.is(-0,-0)),inc1:((1+1)),dec1:((5-1)),twoPow:((2**10)),gold:((((1+(Math.sqrt(5))))/2)),tau:(((Math.PI)*2)),deg:((((180*(Math.PI)))/180)),euler:(Math.exp(1)),cubic:((((5**3))%7))});
const MATHS=({sin:(Math.sin(0.5)),cos:(Math.cos(0.5)),tan:(Math.tan(0)),asin1:(Math.asin(1)),acos1:(Math.acos(-1)),atan2:(Math.atan2(1,1)),atan1:(Math.atan(1)),sinh1:(Math.sinh(1)),cosh1:(Math.cosh(1)),tanh1:(Math.tanh(0)),asinh1:(Math.asinh(1)),acosh2:(Math.acosh(2)),atanh05:(Math.atanh(0.5)),exp3:(Math.exp(2)),expm1:(Math.expm1(1)),log2g:(Math.log2(8)),log10g:(Math.log10(1000)),log1p:(Math.log1p(((Math.E)-1))),cbrt64:(Math.cbrt(64)),cbrtN:(Math.cbrt(-8)),hypot34:(Math.hypot(3,4)),imul3:(Math.imul(0x7fffffff,3)),clz32:(Math.clz32(0x80000000)),fround2:(Math.fround(1.337)),trunc2:(Math.trunc(-1.9)),ceil2:(Math.ceil(-0.9)),floor2:(Math.floor(-0.1)),roundP:(Math.round(1.5)),roundM:(Math.round(-0.5)),roundS:(Math.round(-1.5)),roundZ:(Math.round(0.4)),min0:(Math.min(1,-0)),max0:(Math.max(1,-0)),signA:([Math.sign(-5),Math.sign(-0),Math.sign(0),Math.sign(0.001),Math.sign(NaN)]),pi:(Math.PI),e:(Math.E),ln2:(Math.LN2),ln10:(Math.LN10),log2e:(Math.LOG2E),log10e:(Math.LOG10E),sqrt2:(Math.SQRT2),sqrthalf:(Math.SQRT1_2),max3:(Math.max(-1,-5,3,10,-2)),min3:(Math.min(-1,-5,3,10,-2)),sum1k:((()=>{let s=0;
for (let i=1;(i<1000);i++)((s+=((1/((i*i))))));
return s;
})()),fact20:((()=>{let p=1;
for (let i=2;(i<=20);i++)((p*=i));
return p;
})()),lei:((()=>{let s=0;
for (let i=0;(i<30);i++)((s+=(((Math.sin(i))*(Math.cos(i))))));
return s;
})())});
const BIGS=({a:(((2n**100n)).toString()),b:(((12345678901234567890n*9876543210n)).toString()),c:(((7n%3n)).toString()),d:(((((((2n**64n))-9n))>>2n)).toString()),e:((((BigInt("0x1fffffffffffff"))>>1n)).toString()),f:(((9007199254740991n/3n)).toString()),g:(((9007199254740991n+1n)).toString()),i:(((((10n**30n))/7n)).toString()),as8:((BigInt.asIntN(8,200n)).toString()),asu8:((BigInt.asUintN(8,200n)).toString()),as16:((BigInt.asIntN(16,-1n)).toString()),as64:((BigInt.asUintN(64,-1n)).toString()),mix:(((Number(9007199254740993n))*0.5)),neg:((-123n).toString()),zero:((0n).toString()),bits:(((((1n<<80n))|((3n<<4n)))).toString()),sq:(((299792458n**2n)).toString()),cmplx:(((((((2n+3n))*4n))-5n)).toString())});
const CNV=({num:(Number("123.45")),parseHex:(Number.parseInt("ff",16)),parseInt2:(parseInt("10px")),parseFloat3:(parseFloat("3.14abc")),parseBin:(Number("0b1011")),parseOct:(Number("0o17")),parseExp:(Number("1e3")),nanNum:(Number("abc")),blank:(Number("")),plusStr:(+"42"),minusStr:(-"1.5"),isNaNum:(Number.isNaN("x")),isNaStr:(isNaN("x")),isFin:(Number.isFinite(Infinity)),isFinS:(Number.isFinite(0.5)),intSel:([Number.isInteger(1),Number.isInteger(1.5),Number.isInteger(NaN),Number.isInteger(1e308)]),safeSel:([Number.isSafeInteger((((2**53))-1)),Number.isSafeInteger((2**53))]),toStr16:((255).toString(16)),toStr2:((5).toString(2)),toStr36:((1234567).toString(36)),toFix:((3.14159).toFixed(2)),toFixZ:((3).toFixed(4)),toPre:((3.14159).toPrecision(3)),toExp:((12345).toExponential(2)),bStr:([String(123),String(null),String(undefined),String([1,2]),String({a:1}),true.toString()]),bNum:([Boolean(0),Boolean(""),Boolean("0"),Boolean(NaN),Boolean([]),Boolean(" "),Boolean(-0)]),ctor:([((Number("10"))+5),+"010",Number("0x10")]),unplus:(((+"a")+1)),hexid:0xDEADBEEF,binhuge:0b11111111111111111111111111111111,octhuge:0o7777777});
const STRFX=({len:("ðŸ¶ðŸ±".length),cplen:(([..."ðŸ¶ðŸ±"]).length),cat:(((((((("a"+"b"))+7))+true))+null)),up:("hÃ©llo WÃ–RLD".toUpperCase()),low:("HÃ‰LLO wÃ¶rld".toLowerCase()),sl:("abcdefghij".slice(-3)),sb:("abcdefghij".substr(2,3)),sw:("prefix-x".startsWith("pre")),ew:("x-suffix".endsWith("suf")),inc3:("lena".includes("na")),idx3:("ababab".lastIndexOf("ab")),spi:("a-b-c".split("-")),spr:("a1b22c333".split(/\d+/)),sprKeep:("a1b22c333".split(/(\d+)/)),mat:("x1y2z3".match(/\d/g)),mall:(([...("k1v9j2".matchAll(/[a-z](\d)/g))]).map((m)=>((((m[0])+":"))+(m[1])))),spy:("a-b_c.d".replace(/_/g," X ")),spyFn:("abc123".replace(/\d+/g,(d)=>((Number(d))*2))),scy:("a=b=c".replace("=","+")),rep2:("ab".repeat(3)),padS:("4".padStart(3,"0")),padE:("8".padEnd(2,".")),chAt:("fÃ¶Ã¶".charAt(1)),code:("ABC".charCodeAt(1)),codeP:("ðŸ˜€a".codePointAt(1)),fromCode:(String.fromCharCode(72,105)),fromCP:(String.fromCodePoint(0x1F600,0x200D,0x1F525)),at:("abcdef".at(1)),atNeg:("abcdef".at(-2)),trim:(" \t a b \n".trim()),trimL:("  x  ".trimStart()),trimR:("  x  ".trimEnd()),normNFD:(("Ã…".normalize("NFD")).length),normNFC:((("Å".normalize("NFC"))==="Ã…")),normNKF:("é".normalize("NFKC")),cc:("a".concat("b","c")),lc2:("AbCd".toLowerCase()),uc2:("AbCd".toUpperCase()),olderIdx:("x".indexOf("y")),noEnd:("sun".endsWith("uns")),noStart:("gun".startsWith("g")),sedg:("edge case".endsWith(" case")),zws:("a​B​C".split("​")),nullCh:("abc".charCodeAt(99)),emptyS:("".padStart(2,"xy")),wrap:"ABCmili",octal:"AB",hextab:(("\tA\r\n"+"b")),fillV:((("x".repeat(2))+("y".repeat(3)))),idxStar:("**ab".indexOf("*")),lidxNof:("abc".lastIndexOf("z"))});
const RGX=({date:(/^\d{4}-\d{2}-\d{2}$/.test("2024-13-99")),email:(/^[^@]+@[^@]+\.[^@]+$/.test("a@b.co")),emailB:(/^[^@]+@[^@]+\.[^@]+$/.test("nope")),group:((/(?<y>\d{4})-(?<m>\d{2})-(?<d>\d{2})/.exec("2024-05-06")).groups),flaggy:(/hello/i.test("HELLO")),unicode2:(/^\p{Emoji_Presentation}$/u.test("ðŸ˜€")),sflag:(/a.b/s.test("a\nb")),backref:(/^(a+)(b+)\1$/.test("aabbaa")),namedBack:(/^(?<w>ab)\k<w>$/.test("abab")),zero:((/a|b/.exec("b"))[0]),multiline:(/^world$/m.test("hello\nworld")),sticky2:((()=>{const r=/a/y;
(((r.lastIndex)=1));
const m=(r.exec("baa"));
return ((m?(m[0]):null));
})()),greek:(/^[\u0370-\u03FF]+$/.test("Î±Î²Î³")),quant:(/^[0-9]{2,4}$/.test("123")),quantNg:(/^[0-9]{2,4}$/.test("12345")),lookA:((/foo(?=bar)/.exec("foobar"))[0]),lookB:((/foo(?!bar)/.exec("foo!"))[0]),allSplit:("a1b2c".split(/\d/)),toStringR:(/x/g.toString()),flagsR:(/ab+c/gi.flags),sourceR:(/a[b-d]e/.source),lastIdxR:((()=>{const r=/o/g;
(r.exec("foo"));
return (r.lastIndex);
})()),idxArr:((/(\d+)/.exec("12ab"))[1]),greedy:(("aaa".match(/a*/))[0]),lazy:(("aaa".match(/a*?/))[0]),dotAll:(/./s.test("\n")),noDot:(/./.test("\n")),word:(/^\w+$/.test("foo_1")),space:(/^\s*$/.test(" \n\t")),digit:(/^\d$/.test("5")),pub:(/^(?:ab|cd)+$/.test("abcdab")),anchor:("A B".replace(/\b/g,"|")),emoji2:(/^\p{L}+$/u.test("hÃ©llo")),quant2:("abbbb".match(/ab{2,4}c/)),negClass:(/^[^x]+$/.test("yyyy")),raww:/\\/,flagY:(/a/y.flags),complex:(/^(\d{1,3}\.){3}\d{1,3}$/.test("192.168.1.1")),complexBAD:(/^(\d{1,3}\.){3}\d{1,3}$/.test("999.1.1.1")),splitSub:(("a-b-c".split(/-/)).join("_"))});
const ARRX=({map:(([1,2,3,4]).map((x,i)=>(((x*10))+i))),flt:(([1,2,3,4,5,6]).filter((x)=>(((x%3))===0))),fltIdx:(([1,2,3,4]).filter((x,i)=>(((i%2))===0))),red:(([1,2,3,4]).reduce((a,b,i)=>(a+((b*((10**i))))),0)),redRn:(([1,2,3]).reduceRight((a,b)=>(a-b),0)),flat3:(([1,[2,[3,[4,[5]]]]]).flat(3)),flatDf:(([1,[2,[3]]]).flat()),flatMap1:(([1,2,3]).flatMap((x)=>[x,-x])),sort:(([9,2,5,1,7]).sort((a,b)=>(a-b))),sortStr:((["b","B","a","A"]).sort((a,b)=>a.localeCompare(b))),rev:(([...([1,2,3])]).reverse()),some:(([1,2,3]).some((x)=>(((x%2))===0))),every:(([2,4]).every((x)=>(((x%2))===0))),find:(([1,2,3,4,5]).find((x)=>(x>3))),findI:((["a","b","c"]).findIndex((x)=>(x==="c"))),findL:(([1,2,3,4]).findLast((x)=>(((x%2))===1))),findLi:(([1,2,3,4]).findLastIndex((x)=>(((x%2))===1))),incl:(([1,2,NaN]).includes(NaN)),inclF:(([1,2,3]).includes(4)),idx:((["a","b","a"]).indexOf("a")),lidx:((["a","b","a"]).lastIndexOf("a")),join:(([1,"a",true,null]).join("|")),con:(([1,2]).concat([3],4,[5,[6]])),sla:(([1,2,3,4,5]).slice(1,-1)),sp:((()=>{const a=([1,2,3,4,5]);
(a.splice(1,2,"x"));
return a;
})()),spr:((()=>{const a=([1,2,3,4,5]);
const r=(a.splice(1,2));
return ([r,a]);
})()),sh:((()=>{const a=([1,2,3]);
return ([a.shift(),a]);
})()),unsh:((()=>{const a=([2,3]);
(a.unshift(0,1));
return a;
})()),pop:((()=>{const a=([1]);
return ([a.pop(),a]);
})()),push:((()=>{const a=([]);
const l=(a.push(1,2));
return ([l,a]);
})()),copyW:((()=>{const a=([1,2,3,4]);
(a.copyWithin(0,2));
return a;
})()),fillA:((()=>((Array(5)).fill(7)).map((v,i)=>(v+i)))()),atIdx:(([10,20,30]).at(-1)),keysA:([...(([10,20]).keys())]),valsA:([...(([10,20]).values())]),entA:([...(([10,20]).entries())]),withA:(([1,2,3]).with(1,9)),toS:(([3,1,2]).toSorted()),toR:(([1,2,3]).toReversed()),toSp:(([1,2,3,4,5]).toSpliced(1,2,8)),group:((()=>{const o=(Object.groupBy([1,2,3,4,5],(x)=>(((x%2))?"odd":"even")));
return ([o.odd,o.even]);
})()),idxParam:(([1,2,3]).map((v,i,arr)=>(((v+i))+(arr.length)))),cmpr:((["3",3,30]).sort()),lex:(("10 9 8".split(" ")).sort()),node:(([1,[2]]).length),del:((()=>{const a=([1,2,3]);
(delete (a[1]));
return ([a.length,a[1],(1 in a)]);
})()),expand:([0,...([1,2]),,3,...([4])]),spliceAdd:((()=>{const a=([1,5]);
(a.splice(1,0,2,3,4));
return a;
})()),twoDim:(([[1,2],[3,4]]).map((row)=>(row.map((x)=>(x*10))).join("-"))),reverse2:((["a","b","c"]).reverse()),stable:(([1,3,2,2,1]).sort())});
const COLL=({setArr:([...(new Set([3,1,2,1]))]),setSz:((new Set("aab")).size),setHas:((new Set([1])).has(1)),setAdd:((()=>{const s=(new Set());
(((s.add(1)).add(1)).add(2));
return ([...s]);
})()),setDel:((()=>{const s=(new Set(["a","b"]));
(s.delete("a"));
return ([...s]);
})()),setIter:((()=>{const s=(new Set(["x","y"]));
let acc="";
for (const v of s)((acc+=v));
return acc;
})()),sKeys:([...((new Set([5,6])).keys())]),sVals:([...((new Set([5,6])).values())]),sEnts:([...((new Set([5,6])).entries())]),mapArr:([...(new Map([["a",1],["b",2]]))]),mapGet:((new Map([["x",9]])).get("x")),mapMiss:((new Map()).get("z")),mapHas:((new Map([["a",1]])).has("a")),mapSet:((()=>{const m=(new Map());
(((m.set("k",1)).set("k",2)).set("j",3));
return ([m.get("k"),[...m]]);
})()),mapDel:((()=>{const m=(new Map([["a",1],["b",2]]));
(m.delete("a"));
return ([...m]);
})()),wm:((()=>{const w=(new WeakMap());
const o=({});
(w.set(o,5));
return (((w.has(o))&&(((w.get(o))===5))));
})()),ws:((()=>{const w=(new WeakSet());
const o=({});
(w.add(o));
return (w.has(o));
})()),mapSize:((new Map([["a",1],["b",2],["c",3]])).size),mapLoop:((()=>{const m=(new Map([["a",1],["b",2]]));
let s="";
for (const [k,v] of m)((s+=((k+v))));
return s;
})()),chain:(((new Map()).set(1,"one")).get(1)),mapKeyObj:((()=>{const o=({id:1});
const m=(new Map());
(m.set(o,"found"));
return (m.get(o));
})()),setClear:((()=>{const s=(new Set([1,2]));
(s.clear());
return (s.size);
})()),mapValues:([...((new Map([["a",1],["b",2]])).values())])});
const TARR=((()=>{const u8=(new Uint8Array([3,1,4,1,5,9]));
const i16=(new Int16Array([-1,0,1,32767,-32768]));
const i8=(new Int8Array([127,-128,-1,1]));
const u16=(new Uint16Array([65535,0,256]));
const u32=(new Uint32Array([0,4294967295,123456]));
const f32=(new Float32Array([0.1,0.2,(1/3)]));
const f64=(new Float64Array([1.5,-2.5]));
const u8c=(new Uint8ClampedArray([-5,0,255,300]));
const bi64=(new BigInt64Array([1n,-1n,9007199254740993n]));
const ubi64=(new BigUint64Array([1n,18446744073709551615n]));
const a=(new Uint8Array([1,2,3,4]));
const sub=(a.subarray(1,3));
(((sub[0])=9));
const f=(new Float64Array(3));
(f.fill(2.5));
const cp=(new Int32Array([1,2,3,4,5]));
(cp.copyWithin(1,3));
return ({u8:([...u8]),i16:([...i16]),i8:([...i8]),u16:([...u16]),u32:([...u32]),f32:([...f32]),f64:([...f64]),u8c:([...u8c]),bi64:(([...bi64]).map(String)),ubi64:(([...ubi64]).map(String)),len:(((((u8.length)+":"))+(u8.byteLength))),sub:([...a,,...sub]),fill:([...f]),cp:([...cp]),set:((()=>{const x=(new Uint8Array(4));
(x.set([9,8],1));
return ([...x]);
})()),sorted:(([...(new Float32Array([3.5,1.25,2.0]))]).sort()),reverse:(([...(new Int8Array([1,-2,3]))]).reverse()),index:((new Int8Array([4,5,6])).indexOf(5)),sum:(([...u8]).reduce((a,b)=>(a+b),0)),cplen:(([...(new Uint8Array([1,2]))]).length)});
})());
const ABV=((()=>{const ab=(new ArrayBuffer(16));
const dv=(new DataView(ab));
(dv.setUint8(0,255));
(dv.setInt16(2,-1234,true));
(dv.setUint32(4,0xDEADBEEF,true));
(dv.setFloat64(8,Math.PI,true));
const back=(new Uint8Array(ab));
const d2=(new DataView(new ArrayBuffer(2)));
(d2.setInt16(0,-1,false));
return ({abLen:(ab.byteLength),u8:(dv.getUint8(0)),i16:(dv.getInt16(2,true)),u32:(dv.getUint32(4,true)),f64:(dv.getFloat64(8,true)),be:(d2.getInt16(0,false)),t00:(dv.getFloat32(4,true)),slice:([...(back.slice(4,8))]),bytes:([...back])});
})());
const BUF=((()=>{const b=(Buffer.from([1,2,3,4]));
const s=(Buffer.from("hiðŸ˜€"));
return ({u32be:(b.readUInt32BE(0)),u16le:(b.readUInt16LE(2)),sw:([...(b.swap16())]),cat:((Buffer.concat([Buffer.from([9]),Buffer.from([8])])).toString("hex")),str:(s.toString("utf8")),hex:((Buffer.from("ff0080","hex")).toString("hex")),b64:((Buffer.from("yo")).toString("base64")),json:((Buffer.from([104,105])).toString()),alloc:([...(Buffer.alloc(3,5))]),fill:([...((Buffer.from([1,2,3])).fill(7,1))]),lens:((((((Buffer.from("abc")).length)+":"))+((Buffer.from("abc")).byteLength)))});
})());
const OBD=((()=>{const o=({});
(Object.defineProperty(o,"hidden",{value:99,enumerable:false,configurable:false,writable:false}));
(Object.defineProperty(o,"access",{get(){return (((this.xstore)*2));
},set(v){(((this.xstore)=v));
},enumerable:true}));
(((o.access)=21));
const dh=(Object.getOwnPropertyDescriptor(o,"hidden"));
(Object.freeze({}));
(Object.seal({}));
return ({hidden:(o.hidden),acc:(o.access),names:(Object.getOwnPropertyNames(o)),keys:(Object.keys(o)),hasOwn:(o.hasOwnProperty("hidden")),inProto:(("toString" in o)),proto:((Object.prototype).isPrototypeOf(o)),descr:({value:(dh.value),en:(dh.enumerable),cfg:(dh.configurable),wr:(dh.writable)}),getDesc:((()=>{const d=(Object.getOwnPropertyDescriptor(o,"access"));
return (typeof (d.get));
})()),entries:(Object.entries({x:1,y:2})),values:(Object.values({x:1,y:2})),from:(Object.fromEntries([["a",1],["b",2]])),assign:(Object.assign({base:1},{mid:2},{base:3,last:4})),spread:({...({a:1}),...({b:2,a:9})}),keys2:(Object.keys(Object.create(null))),isFrozen:(Object.isFrozen(o)),isSealed:(Object.isSealed(o)),isExt:(Object.isExtensible(o)),precoping:(((Object.preventExtensions({})) instanceof Object)),stringtag:(((((((Object.prototype).toString).call([]))+"|"))+(((Object.prototype).toString).call(null)))),createProto:((Object.create({q:1})).q),own:((Object.getOwnPropertySymbols([])).length),lookup:((((o.hasOwnProperty).bind)?(o.hasOwnProperty("hidden")):false))});
})());
const DELX=((()=>{const o=({a:1,b:2});
(delete (o.a));
return ([o.a,o.b,("a" in o)]);
})());
const TSOF=({typeofs:([typeof "s",typeof 1,typeof true,typeof undefined,typeof ({}),typeof ([]),typeof (()=>{
}),typeof null,typeof (Symbol()),typeof (new Date())])});
const ERRS=((()=>{const mk=((fn)=>{try{const v=(fn());
return (("none:"+v));
}catch(e){return ((((((e.constructor).name)+":"))+(e.message)));
}
});
return ({type:(mk(()=>{const a=null;
return (a.x);
})),ref:(mk(()=>{return undeclaredzz;
})),syn:(mk(()=>{throw (new SyntaxError("bad syntax"));
})),range:(mk(()=>{return ((new Array((2**32))).slice(0));
})),tofix:(mk(()=>{return ((123).toFixed(101));
})),circ:(mk(()=>{const o=({a:1});
(((o.self)=o));
return (JSON.stringify(o));
})),finn:(mk(()=>{let ran=false;
try{throw (new Error("b"));
}finally{((ran=true));
}
return ran;
})),nest:(mk(()=>{try{try{throw (new Error("inner"));
}finally{
}
}catch(e){return (e.message);
}
})),errCls:(mk(()=>{class MyE extends Error{}
throw (new MyE("mine"));
})),eor:(mk(()=>{throw ({code:1});
})),protoErr:(mk(()=>{return ((TypeError.prototype).name);
})),strictim:(mk(()=>{const obj=({});
(Object.defineProperty(obj,"r",{value:1,writable:false}));
try{(((obj.r)=2));
return "ok";
}catch(e){return ((e.constructor).name);
}
}))});
})());
const PROX=((()=>{const target=({a:1,b:2});
const seen=([]);
const p=(new Proxy(target,{get(t,k,r){(seen.push(("get:"+(String(k)))));
return (t[k]);
},set(t,k,v){(seen.push(("set:"+(String(k)))));
(((t[k])=((v*2))));
return true;
},has(t,k){(seen.push(("has:"+(String(k)))));
return ((k in t));
}}));
(((p.c)=3));
const got=(p.a);
return ({got:got,a2:(p.a),hasB:(("b" in p)),tgt:target,seen:seen});
})());
const SYMS=((()=>{const s1=(Symbol("s1"));
const s2=(Symbol("s2"));
const o=({[s1]:"one",[s2]:"two"});
(((o[s2])="TWO"));
const iterable=({});
(((iterable[Symbol.iterator])=(function* iterfn(){(yield 1);
(yield 2);
})));
const desc=((Object.getOwnPropertySymbols(o))[0]);
return ({s1:(o[s1]),s2:(o[s2]),fromIter:([...iterable]),desc:(String(desc)),keys:((((((Object.getOwnPropertySymbols(o)).length)+":"))+((Object.keys(o)).length))),named:(((Symbol.for("x"))===(Symbol.for("x")))),keyFor:(Symbol.keyFor(Symbol.for("x"))),descr:((Object.getOwnPropertyDescriptor(o,s1)).value),well:((Symbol.iterator).toString()),typeofSym:(typeof (Symbol("q")))});
})());
const GITZ=((()=>{function* naturals(){let i=0;
while(true){(yield (i++));
}
}
function* skip(stop){let n=0;
while(((n<stop))){(yield n);
((n+=2));
}
}
function* nest(){(yield 1);
(yield* (skip(4)));
(yield 9);
}
const g=(naturals());
(g.next());
(g.next());
(g.next());
return ({next:((g.next()).value),skip:([...(skip(7))]),nest:([...(nest())]),first:(((((((naturals()).next()).value)===0))?"ok":"bad")),back:((()=>{const it=(skip(10));
const a=(it.next());
const b=(it.return(99));
return ([a.done,a.value,b.done,b.value]);
})()),manual:((()=>{const iter=(skip(5));
const vals=([]);
let r;
while((!(((r=(iter.next()))).done)))(vals.push(r.value));
return vals;
})()),near:((()=>{const it=(naturals());
(it.next());
(it.next());
return ((it.next()).value);
})())});
})());
function RECN(n){if(((n<=1)))return n;
return (((RECN((n-1)))+(RECN((n-2)))));
}
function MUTA(n){return ((((n===0))?0:(MUTB((n-1)))));
}
function MUTB(n){return ((((n===0))?1:(MUTA((n-1)))));
}
function ARGX(){return ([...arguments]);
}
function TAG(strings,...vals){return ((strings.map((s,i)=>(s+((((i<(vals.length)))?(((("{"+(vals[i])))+"}")):""))))).join(""));
}
const RECS=({fib:(RECN(18)),mut:([MUTA(10),MUTB(10)]),arg:(ARGX(1,"two",true))});
function NTC(){return (((((typeof new.target)==="function"))?"constructed":"plain"));
}
class ChildN{constructor(){(((this.v)=((((new.target===ChildN))?"child":"other"))));
}
}
class Mother2{static count=0
constructor(name){(((this.name)=name));
((Mother2.count)++);
}
greet(){return (("hi "+(this.name)));
}
static feed(){return "food";
}
}
class Daughter2 extends Mother2{#seed
constructor(name,seed){(super(name));
(((this.#seed)=seed));
}
get secret(){return (this.#seed);
}
set secret(v){(((this.#seed)=v));
}
static feed(){return (((super.feed())+"!"));
}
greetings(){return (((super.greet())+"!!!"));
}
get [(Symbol.toStringTag)](){return "D2";
}
}
const motherx=(new Mother2("m"));
const daughterx=(new Daughter2("d",42));
(((daughterx.secret)=99));
const CLSX=({cnt:(Mother2.count),greetM:(motherx.greet()),greetD:(daughterx.greet()),greetings:(daughterx.greetings()),secret:(daughterx.secret),feedD:(Daughter2.feed()),inst:((((daughterx instanceof Mother2))&&(!((motherx instanceof Daughter2))))),tag:(((Object.prototype).toString).call(daughterx)),ntd:({plain:(NTC()),constructed:(new NTC()),child:((new ChildN()).v)})});
const DTS=((()=>{const d0=(new Date(0));
const d1=(new Date("2024-01-02T03:04:05.678Z"));
const d2=(new Date(Date.UTC(2023,5,15,10,20,30,40)));
return ({t0:(d0.getTime()),iso:(d1.toISOString()),utc:(d1.toUTCString()),y:(d1.getUTCFullYear()),mo:(d1.getUTCMonth()),da:(d1.getUTCDate()),h:(d1.getUTCHours()),mi:(d1.getUTCMinutes()),se:(d1.getUTCSeconds()),ms:(d1.getUTCMilliseconds()),wk:(d1.getUTCDay()),parse:(Date.parse("2024-01-02T03:04:05.678Z")),epoch:(Date.UTC(2000,0,1)),leaps:((((((new Date(2024,1,29)).getDate())+":"))+((new Date(2023,1,29)).getMonth()))),d2:(d2.getTime()),milli:((new Date(1704150245678)).getTime())});
})());
const URLX=((()=>{const u=(new URL("https://user:pass@example.com:8080/a/b?x=1&y=2#frag"));
const u2=(new URL("/rel","https://base.example/p/q?z=9"));
return ({proto:(u.protocol),host:(u.host),hostname:(u.hostname),port:(u.port),path:(u.pathname),q:(u.search),qp:((u.searchParams).get("x")),qs:([...(u.searchParams)]),hash:(u.hash),user:(u.username),pass:(u.password),toString:(u.href),rel:(u2.href)});
})());
const ENCD=((()=>{const te=(new TextEncoder());
const td=(new TextDecoder());
const b=(te.encode("hÃ©llo"));
return ({bytes:([...b]),back:(td.decode(b)),astral:(([...(td.decode(te.encode("ðŸ˜€")))]).length),b64:((Buffer.from("hiðŸ˜€")).toString("base64")),b64d:((Buffer.from("aGk=","base64")).toString("utf8")),b64dd:((Buffer.from("aGk=","base64")).toString("hex")),hex:((Buffer.from([255,0,128])).toString("hex")),uni:(String.fromCodePoint(0x1F600,0x1F680)),len:("aðŸ˜€b".length),clen:(([..."aðŸ˜€b"]).length),atob1:(atob("aGVsbG8=")),btoa1:(btoa("hello")),codeunits:((te.encode("aðŸ˜€b")).length)});
})());
const TAGG=({tag:(TAG`a${1}d${2}c${"x"}`),tagRaw:(String.raw`a\nb`),cooked:(((((`a\nb`)==="a\nb"))?"cooked":"raw")),expr:(`${("x"+1)}${(2*3)}`),nest:(`${`${`inner`}`}`),multiline:(`line1\nline2`),many:(`${"a"}${"b"}${"c"}`)});
const FLOW=((()=>{const r=([]);
outer:for (let i=0;(i<4);i++){for (let j=0;(j<4);j++){if(((j===1)))continue;
if(((((i===2))&&((j===2)))))break outer;
if(((i===3)))continue outer;
(r.push((((i+":"))+j)));
}
}
for (let i=0;(i<10);i++){if(((i===3)))continue;
if(((i===7)))break;
switch(i){case 0:{(r.push("zero"));
break;}case 1:{}case 2:{(r.push("low"));
break;}default:{(r.push(i));}}
}
let n=0;
while(((n<3))){(r.push(("w"+n)));
(n++);
}
return r;
})());
const DOW=((()=>{const r=([]);
let n=0;
do{(r.push(n));
(n++);
}while(((n<3)))
const r2=([]);
do{(r2.push("once"));
}while(false)
const dbl=((()=>{let x=0;
do{(x++);
}while(((x<(-5))))
return x;
})());
return ({r:r,r2:r2,dbl:dbl});
})());
const OPTCH=({q:((()=>{const o=({x:({y:1})});
return ((o?.x)?.y);
})()),miss:((()=>{const o=({});
return ((o?.a)?.b);
})()),call:((()=>{const o=({f:((x)=>(x*2))});
return ((o.f)?.(21));
})()),nullCall:((()=>{const o=({});
return ((o.f)?.());
})()),idx:((()=>{const o=({a:({b:5})});
return ((o?.["a"])?.["b"]);
})()),orEq:((()=>{let a=null;
((a??="filled"));
let b="";
((b||="else"));
let c="x";
((c&&="and"));
return ([a,b,c]);
})()),deep:((()=>{const o=({a:({b:({c:({d:42})})})});
return ((((o.a)?.b)?.c)?.d);
})()),mix:((()=>{const o=({arr:([1,{v:9}])});
return (((o?.arr)?.[1])?.v);
})())});
const FORX=((()=>{const r=([]);
for (const [k,v] of (new Map([["a",1],["b",2]])))(r.push((k+v)));
for (const i of ([1,2,3]))(r.push(i));
for (const c of "abc")(r.push(c));
for (const x of (new Set([1,1,2])))(r.push(x));
return r;
})());
const FAW=((async ()=>{const out=([]);
async function* tick(){(yield 1);
(yield 2);
(yield 3);
}
for await (const v of (tick()))(out.push((v*10)));
for await (const v of ([4,5]))(out.push(v));
return out;
})());
const PASY=((async ()=>{const all=(await (Promise.all([Promise.resolve(1),Promise.resolve(2)])));
const settled=(await (Promise.allSettled([Promise.resolve("ok"),Promise.reject("no")])));
const any=(await (Promise.any([Promise.reject(1),Promise.resolve(2)])));
const race=(await (Promise.race([Promise.resolve(1),Promise.resolve("later")])));
const fin=(await ((((Promise.resolve(5)).then((x)=>(x+1))).catch(()=>0)).finally(()=>{
})));
const rej=(await ((Promise.reject("bad")).catch((e)=>("caught:"+e))));
const up=(await ((Promise.resolve(21)).then(async (v)=>{const w=(await (Promise.resolve((v*2))));
return w;
})));
const when=(await ((new Promise((r)=>setTimeout(r,1))).then(()=>"tick")));
return ({all:all,settled:(settled.map((s)=>((s.status)+(((((s.value)!==undefined))?((":"+(s.value))):((":"+(s.reason)))))))),any:any,race:race,fin:fin,rej:rej,up:up,when:when,asyncObj:(await ((async ()=>{const a=(await (Promise.resolve(5)));
const b=(await (Promise.resolve(7)));
return ({a:a,b:b,sum:((a+b))});
})()))});
})());
const JSONX=({parse:(JSON.parse(JSON.stringify({a:([1,2,{b:"x"}])}))),deep:(JSON.parse("[[1,2],[3,4]]")),str:(JSON.stringify({x:([1,"a",true,null])})),num:(JSON.stringify(1e21)),bool:(JSON.stringify({u:undefined,f:(function ident(){
}),n:null})),repl:(JSON.stringify({a:1,b:2},["a"])),keysOrd:(Object.keys(JSON.parse("{\"b\":1,\"a\":2,\"c\":3}")))});
const RGXS2=({reDot:(/a+/.exec("aaa"))});
const GZLN=((((1024*2))+256));
const SIEVE=((()=>{const n=200;
const marks=((new Uint8Array((n+1))).fill(1));
(((marks[0])=0));
(((marks[1])=0));
for (let i=2;(((i*i))<=n);i++){if((marks[i])){for (let j=((i*i));(j<=n);(j+=i))(((marks[j])=0));
}
}
const primes=([]);
for (let i=0;(i<=n);i++)if((marks[i]))(primes.push(i));
return ({primes:primes,count:(primes.length),last:(primes[((primes.length)-1)])});
})());
function HASHZ(s){let h=2166136261;
for (let i=0;(i<(s.length));i++){((h^=(s.charCodeAt(i))));
((h=(Math.imul(h,16777619))));
}
return (((h>>>0)).toString(16));
}
const HASHR=({a:(HASHZ("")),b:(HASHZ("hello")),c:(HASHZ("a".repeat(100)))});
function BNode(v){(((this.v)=v));
(((this.l)=null));
(((this.r)=null));
}
function BIns(root,v){if((!root))return (new BNode(v));
if(((v<(root.v))))(((root.l)=(BIns(root.l,v))));else if(((v>(root.v))))(((root.r)=(BIns(root.r,v))));
return root;
}
function BCollect(n,acc){if((!n))return acc;
(BCollect(n.l,acc));
(acc.push(n.v));
(BCollect(n.r,acc));
return acc;
}
function BHeight(n){if((!n))return 0;
return ((1+(Math.max(BHeight(n.l),BHeight(n.r)))));
}
const TREE=((()=>{let root=null;
const seed=([5,3,8,1,4,7,9,2,6,0]);
for (const v of seed)((root=(BIns(root,v))));
return ({sorted:(BCollect(root,[])),height:(BHeight(root)),rootv:(root.v)});
})());
function BSort(a){const b=([...a]);
for (let i=0;(i<(b.length));i++){for (let j=((i+1));(j<(b.length));j++){if((((b[j])<(b[i])))){const t=(b[i]);
(((b[i])=(b[j])));
(((b[j])=t));
}
}
}
return b;
}
const SORTS=({bubble:(BSort([9,4,7,1,8,3,2,5,6,0]))});
const CHAIN=(((([1,2,3,4,5,6,7,8,9,10]).filter((x)=>(((x%2))===0))).map((x)=>(x*x))).reduce((a,x)=>(a+(("-"+x))),""));
const FCOUN=((()=>{const s="the quick brown fox jumps over the lazy dog";
const m=(new Map());
for (const c of s)(m.set(c,((((m.get(c))||0))+1)));
return ((([...m]).map(([c,n])=>(c+n))).join(" "));
})());
const MATRIX=((()=>{const A=([[1,2],[3,4]]);
const B=([[5,6],[7,8]]);
return (A.map((row,i)=>(B[0]).map((z,j)=>row.reduce((s,x,k)=>(s+((x*((B[k])[j])))),0))));
})());
const AMEM=((()=>{const m=(new Map());
function ak(a,b){const k=((((a+":"))+b));
if((m.has(k)))return (m.get(k));
let r;
if(((a===0)))((r=((b+1))));else if(((b===0)))((r=(ak((a-1),1))));else ((r=(ak((a-1),ak(a,(b-1))))));
(m.set(k,r));
return r;
}
return ([ak(1,5),ak(2,3),ak(3,2)]);
})());
const CURRY=((()=>{const add=((a)=>(b)=>(c)=>(((a+b))+c));
return (((add(1))(2))(3));
})());
const comp2=((f,g)=>(x)=>f(g(x)));
const COMP=([(comp2((x)=>(x*2),(x)=>(x+1)))(5),([1,2,3]).map(comp2((x)=>(x+1),(x)=>(x*2)))]);
const BASE=((()=>{function toB(n,b){if(((n===0)))return "";
const d=((n%b));
return (((toB(Math.floor((n/b)),b))+((((d<10))?d:(String.fromCharCode((((65+d))-10)))))));
}
return ({b2:(toB(255,2)),b16:(toB(2559,16))});
})());
const PARSEB=((()=>{const words=(("one two three".split(" ")).map((w)=>({w:w,len:(w.length)})));
return ((words.map((o)=>((((o.w)+":"))+(o.len)))).join("|"));
})());
function MULT(a,b){return ((a*b));
}
const BINDS=({call:(MULT.call(null,6,7)),apply:(MULT.apply(null,[6,7])),bound:((MULT.bind(null,6))(7)),ctx:((function(){return (this.x);
}).call({x:42})),partial:((((a,b,c)=>(((a+b))+c)).bind(null,1,2))(3))});
const BIGSTR=((()=>{let s="";
for (let i=0;(i<64);i++)((s+=i));
return s;
})());
const FRZ=((()=>{const o=({a:1});
(Object.freeze(o));
try{(((o.a)=2));
return ([o.a,Object.isFrozen(o)]);
}catch(e){return (["throw",Object.isFrozen(o)]);
}
})());
function REST(first,...rest){return ((((first+":"))+(rest.join("+"))));
}
const RESTR=([REST(1,2,3,4),REST(9)]);
const DEST=((()=>{const {a:a,b:{c:c},arr:[x,,y]}=({a:1,b:({c:2}),arr:([3,4,5])});
const [p,...tail]=([1,2,3,4]);
return ({a:a,c:c,x:x,y:y,p:p,tail:tail});
})());
const DEF3=((()=>{function w(a=5,b=((a*2))){return ((a+b));
}
const arrow=((a=10)=>(a+1));
return ({w0:(w()),w1:(w(1)),w2:(w(1,undefined)),arr:(arrow())});
})());
const OBJACC=((()=>{const o=({vx:1,get v(){return (this.vx);
},set v(n){(((this.vx)=((n*10))));
},inc(){((this.vx)++);
}});
(((o.v)=9));
(o.inc());
return ({v:(o.v),raw:(o.vx)});
})());
const CF=((()=>{const mk=((acc)=>{let n=acc;
return ({up(){(n++);
return this;
},val(){return n;
}});
});
const c=(mk(0));
(((c.up()).up()).up());
return (c.val());
})());
const ITER=((()=>{const o=({a:1});
(((o.b)=2));
const ks=([]);
for (const k in o)(ks.push(k));
return ks;
})());
const COER=({n2s:([(1+"1"),(((1+1))+"2"),("3"-1),("3"*2),("10"/"2"),("a"*1)]),bool2:([("1"==1),("1"===1),(""==0),(""===0),(null==undefined),(null===undefined),(([])==""),(([])==0)]),strORD:([("10">"9"),("10">9),(10>"9")]),plusArr:([(1+([])),(1+([2])),(1+({}))]),eqArr:((((((""+({})))==(("1"+1))))?"x":"n"))});
const NN=({same:((NaN===NaN)),self:(Object.is(NaN,NaN)),eq:((NaN==NaN)),bot:(Number.isNaN((0/0))),pow:(Math.pow(NaN,0))});
const INF=({a:((Infinity-Infinity)),b:((Infinity/Infinity)),c:((1/Infinity)),d:((Infinity*0)),e:((5%Infinity)),f:(((-Infinity)+5)),g:((Infinity<Infinity))});
((async ()=>{const asyncR=(await ((Promise.resolve(42)).then((x)=>(x*2))));
const asyncOut=(await ((async ()=>{const a=(await (Promise.resolve(5)));
const b=(await (Promise.resolve(7)));
return ({a:a,b:b,sum:((a+b))});
})()));
const fawR=(await FAW);
const pasyR=(await PASY);
const ens=({t0:N0,p1:P1,p2:P2,p3:P3,p4:P4,p5:P5,p6:P6,p7:P7,hx:HX,hc:HC,bn:BN,oc:OC,us:US,ld:LD,ls:(LS.toString()),bi:(BI.toString()),nb:NB,zd:ZD,td:TD,spLen:(SPL.length),splHead:(SPL.slice(0,8)),splTail:(SPL.slice(52)),clamp:(clamp(15,0,10)),cl2:(clamp(-4,0,10)),idfn:(idfn(7)),fact:(factMem(5)),fib:fibonacci,dm1:dm1,dm2:dm2,dm3:dm3,am1:am1,am2:am2,am3:am3,dfl:dfl,dfl2:dfl2,genA:genA,genB:genB,pipeOut:pipeOut,om:OM,oname:(obj.fn()),oa:(obj.arrow(6)),ohalf:(obj.half),doge:dDesc,khu:dKhu,animal:(Animal.kingdom()),sigSum:sigSum,counter:counter,wfOut:wfOut,dsw:dsw,tns:tns,isErr:isErr,lps:lps,cbo:cbo,tbv:tbv,neg:NEG,cast:cast,teng:teng,tplOut:tplOut,tricky:tricky,tricky2:tricky2,escapes3:escapes3,strMix:strMix,rfx:rfx,arrays:arrays,objOps:objOps,eq:eq,ovf:ovf,clo:clo,lookupOut:lookupOut,pro:pro,sprd:sprd,rrc:rrc,tnu:tnu,guardInit:guardInit,gsp:gsp,asyncR:asyncR,asyncOut:asyncOut,nums:NUMS,dec:DEC,bits:BITS,maths:MATHS,bigs:BIGS,cnv:CNV,strfx:STRFX,rgx:RGX,arrx:ARRX,coll:COLL,tarr:TARR,abv:ABV,buf:BUF,obd:OBD,delx:DELX,tsof:TSOF,errs:ERRS,prox:PROX,syms:SYMS,gitz:GITZ,recs:RECS,clsx:CLSX,dts:DTS,urlx:URLX,encd:ENCD,tagg:TAGG,flow:FLOW,dow:DOW,optch:OPTCH,forx:FORX,faw:fawR,pasy:pasyR,jsonx:JSONX,sieve:SIEVE,hashr:HASHR,tree:TREE,sorts:SORTS,chain:CHAIN,fcount:FCOUN,matrix:MATRIX,amem:AMEM,curry:CURRY,comp:COMP,base:BASE,parseb:PARSEB,binds:BINDS,bigstr:BIGSTR,frz:FRZ,restr:RESTR,dest:DEST,def3:DEF3,objacc:OBJACC,cf:CF,iter2:ITER,coer:COER,nn:NN,inf:INF,rgxs2:((RGXS2.reDot)[0]),gzln:((GZLN+1)),lcg:LCG,mtable:MTABLE,caes:CAES,collatz:COLLATZ,pascal:PASCAL,evt:EVT,pal:PAL,grow:GROW,words:WORDS,tern:TERN,packed:PACKED,node2:NODE2,rgx3:RGX3,grid:GRID,big2:BIG2,flat2:FLAT2,cmp2:CMP2,pfact:PFACT,deepobj:DEEPOBJ,selfref:SELFREF,valchain:VALCHAIN,tryret:TRYRET,recur2:RECUR2,mapch:MAPCH,spls:SPLS,asctbl:ASCTBL,chrloop:CHRLOOP,reps:REPS,seq:SEQ,sqrdif:SQRDIF,nestloop:NESTLOOP,subseq:SUBSEQ,zip:ZIP,interleave:INTERLEAVE,rotl:ROTL,stack:STACK,q:Q,fibarr:FIBARR,tri:TRI,doc:DOC,branch:BRANCH,opcode:OPCODE,nop:NOP,three:THREE,modfn:MODFN,swapped:SWAPPED,avg:AVG,hist:HIST});
(console.log(JSON.stringify(ens)));
})());
const LCG=((()=>{let s=12345;
const out=([]);
for (let i=0;(i<100);i++){((s=((((((s*1103515245))+12345))%2147483648))));
(out.push((((s>>16))&0x7fff)));
}
return out;
})());
const MTABLE=((()=>{const rows=([]);
for (let i=1;(i<=9);i++){const row=([]);
for (let j=1;(j<=9);j++)(row.push((i*j)));
(rows.push(row));
}
return rows;
})());
const CAES=((()=>{const enc=((s,k)=>(([...s]).map((c)=>{const cc=(c.charCodeAt(0));
if(((((cc>=97))&&((cc<=122)))))return (String.fromCharCode((97+((((((((((cc-97))+k))%26))+26))%26)))));
if(((((cc>=65))&&((cc<=90)))))return (String.fromCharCode((65+((((((((((cc-65))+k))%26))+26))%26)))));
return c;
})).join(""));
return ({e:(enc("Hello World!",3)),d:(enc("Khoor Zruog!",-3))});
})());
const COLLATZ=((()=>{const fn=((n)=>{const seq=([n]);
while(((n!==1))){((n=((((n%2))?((((3*n))+1)):((n/2))))));
(seq.push(n));
}
return seq;
});
return ({s27:((fn(27)).length),s13:(fn(13)),s6:(fn(6))});
})());
const PASCAL=((()=>{const n=10;
const rows=([]);
let prev=([]);
for (let i=0;(i<n);i++){const row=([]);
for (let j=0;(j<=i);j++)(row.push((((((j===0))||((j===i))))?1:(((prev[(j-1)])+(prev[j]))))));
(rows.push(row));
((prev=row));
}
return rows;
})());
const EVT=((()=>{const h=(new Map());
const api=({on(k,fn){if((!(h.has(k))))(h.set(k,[]));
((h.get(k)).push(fn));
return api;
},emit(k,x){const a=(((h.get(k))||([])));
const r=([]);
for (const fn of a)(r.push(fn(x)));
return r;
},count(k){return ((((h.get(k))||([]))).length);
}});
(((api.on("x",(v)=>(v+1))).on("x",(v)=>(v*2))).on("y",(v)=>v));
return ({onx:(api.emit("x",5)),ony:(api.emit("y",9)),cnt:(api.count("x"))});
})());
const PAL=((()=>{const rev=((s)=>(([...s]).reverse()).join(""));
return ({rev:(rev("abcdef")),pal:(((rev("racecar"))==="racecar"))});
})());
const GROW=((()=>{let v=1;
for (let i=0;(i<20);i++)((v=((((v*3))+i))));
return v;
})());
const WORDS=(((n)=>{const ones=(["zero","one","two","three","four","five"]);
if(((n<6)))return (ones[n]);
return "many";
})(5000));
const TERN=((()=>{const f=((x)=>(((x>10))?((((x>20))?"big":((((x===15))?"fifteen":"mid")))):((((x>0))?"pos":((((x===0))?"zero":"neg"))))));
return ([f(25),f(15),f(5),f(0),f(-1)]);
})());
const PACKED=((()=>{const bits=0b0101100001;
return ({lo:((bits&0b111)),mid:((((bits>>3))&0b111)),hi:((((bits>>6))&0b11))});
})());
const NODE2=((()=>{function el(tag,attrs,kids){const a=(((Object.entries((attrs||({})))).map(([k,v])=>(((((" "+k))+"="))+v))).join(""));
return (((((((((((((("<"+tag))+a))+">"))+(((kids||([]))).join(""))))+"</"))+tag))+">"));
}
return ({p:(el("p",{class:"x",id:"y"},["hi"])),deep:(el("div",null,[el("span",{},["a"]),el("span",{},["b"])]))});
})());
const RGX3=({hexOK:(/^#[0-9a-fA-F]{3,8}$/.test("#abc123")),hexNo:(/^#[0-9a-fA-F]{3,8}$/.test("#ggg")),words:((("one two  three".split(/\s+/)).filter(Boolean)).length),dig:("a1b2c3".replace(/[0-9]/g,"#")),lwrap:("hello world".replace(/l+/g,"[l]")),border:("match me".match(/\b\w+\b/g)),keepCase:("aBc".replace(/b/i,"B"))});
const GRID=((()=>{const g=([]);
for (let r=0;(r<4);r++){const row=([]);
for (let c=0;(c<4);c++)(row.push((((r*4))+c)));
(g.push(row.join(" ")));
}
return g;
})());
const BIG2=((()=>{let s=0n;
for (let i=1n;(i<=64n);i++)((s+=((i*i))));
return (s.toString());
})());
const FLAT2=((()=>{let a=1;
(a++);
((a+=2));
((a*=3));
((a-=1));
((a=((a/2))));
((a%=10));
((a**=2));
((a<<=1));
((a|=8));
((a&=7));
((a>>=1));
return a;
})());
const CMP2=((()=>{const a=([1,"1",true,null,0,"","a"]);
const m=([]);
for (const x of a){const row=([]);
for (const y of a)(row.push((((x==y))?1:0)));
(m.push(row));
}
return m;
})());
const PFACT=((()=>{const fn=((n)=>{const out=([]);
let d=2;
while(((n>1))){if(((((n%d))===0))){(out.push(d));
((n/=d));
}else {(d++);
}
}
return out;
});
return ({one:(fn(1260)),two:(fn(97)),three:(fn(1))});
})());
const DEEPOBJ=((()=>{const o=({a:({b:({c:({d:({e:({f:([1,2,{g:"deep"}])}),h:([0])})})})}),i:([])});
return (((((JSON.stringify(o))+"|"))+(JSON.stringify((((((((o.a).b).c).d).e).f)[2]).g))));
})());
const SELFREF=((()=>{const o=({name:"self"});
(((o.self)=o));
return ((((((o.self).name)+":"))+(((o.self)===o))));
})());
const VALCHAIN=((()=>{let x=1;
for (let i=0;(i<10);i++){((x=((x+1))));
((x=((x*2))));
((x=((x-3))));
}
return x;
})());
const TRYRET=((()=>{let r="";
try{try{((r+="a"));
throw "e1";
}catch(e){((r+=(("b"+e))));
}finally{((r+="c"));
}
((r+="d"));
}catch(e){((r+="e"));
}
return r;
})());
const RECUR2=((()=>{const fib=((n,a=0,b=1)=>(((n===0))?a:(fib((n-1),b,(a+b)))));
return ({f30:(fib(30)),f40:(fib(40))});
})());
const MAPCH=((()=>{const m=(new Map());
const o1=({tag:1});
const o2=({tag:2});
(m.set(o1,"first"));
(m.set(o2,"second"));
(m.get(o1));
(m.delete(o2));
return ({a:(m.get(o1)),b:(m.get(o2)),c:(m.size),d:((([...(m.keys())])[0]).tag)});
})());
const SPLS=((()=>{const s="a,b;|c";
const r=([]);
(r.push(...((s.split(",")).flatMap((x)=>x.split(";")))));
return (r.flatMap((x)=>x.split("|")));
})());
const ASCTBL=((()=>{const r=([]);
for (let i=65;(i<=90);i++)(r.push(String.fromCharCode(i)));
return (r.join(""));
})());
const CHRLOOP=((()=>{let s="";
for (let i=0;(i<5);i++){((s=((s+(String.fromCharCode((97+i)))))));
}
return s;
})());
const REPS=((()=>{const s="xy";
let acc="";
for (let i=0;(i<8);i++)((acc+=((((i%2))?(s.toUpperCase()):s))));
return acc;
})());
const SEQ=((()=>{const a=([]);
for (let i=0;(i<20);i++)(a.push((((((i*i))<10))?i:((i*i)))));
return a;
})());
const SQRDIF=((()=>{const s1=([]);
const s2=([]);
for (let i=0;(i<5);i++){(s1.push(i));
(s2.push(i));
}
return ([s1,s2]);
})());
const NESTLOOP=((()=>{let c=0;
for (let i=0;(i<3);i++){for (let j=0;(j<3);j++){for (let k=0;(k<3);k++){if(((((((i+j))+k))===2)))(c++);
}
}
}
return c;
})());
const SUBSEQ=((()=>{let c=0;
for (let a=0;(a<5);a++){for (let b=a;(b<5);b++){for (let s=a;(s<=b);s++)((c+=s));
}
}
return c;
})());
const ZIP=((()=>{const a=([1,2,3]);
const b=(["x","y","z"]);
return ((a.map((v,i)=>(v+(b[i])))).join("-"));
})());
const INTERLEAVE=((()=>{const a=([1,2,3]);
const b=([10,20,30]);
const out=([]);
for (let i=0;(i<(a.length));i++)(out.push(a[i],b[i]));
return out;
})());
const ROTL=((()=>{const a=([1,2,3,4]);
const t=(a.shift());
(a.push(t));
return a;
})());
const STACK=((()=>{const box=([]);
(box.push(1));
(box.push(2));
const top1=(box.pop());
(box.push(3));
return ([top1,box]);
})());
const Q=((()=>{const q=([]);
(q.push({v:1,t:"a"}));
(q.push({v:2,t:"b"}));
const first=(q.shift());
(q.push({v:3,t:"c"}));
return ([first.v,first.t,q.map((o)=>o.v)]);
})());
const FIBARR=((()=>{const a=([0,1]);
for (let i=2;(i<15);i++)(a.push(((a[(i-1)])+(a[(i-2)]))));
return a;
})());
const TRI=((()=>{const n=10;
return (Array.from({length:n},(_,i)=>(((i*((i+1))))/2)));
})());
const DOC=((()=>{const conf=({off:0,on:1,auto:2});
const sel="on";
return (conf[sel]);
})());
const BRANCH=((()=>{const f=((code)=>{if(((code===200)))return "ok";
if(((code===404)))return "missing";
if(((code===500)))return "broken";
return "unknown";
});
return ([f(200),f(404),f(500),f(1)]);
})());
const OPCODE=((()=>{const ops=(new Map());
(ops.set(1,"add"));
(ops.set(2,"sub"));
(ops.set(3,"mul"));
(ops.set(4,"div"));
const run=((s)=>{const parts=(s.split(" "));
const x=(parseInt(parts[1],10));
const y=(parseInt(parts[2],10));
switch((parts[0])){case "add":{return ((x+y));}case "sub":{return ((x-y));}case "mul":{return ((x*y));}case "div":{return ((x/y));}default:{return NaN;}}
});
return ({m:(ops.get(3)),r:([run("add 4 5"),run("mul 3 7"),run("wat 1 1")])});
})());
const NOP=((()=>{let x=0;
if(x){((x=((x+1))));
}else {((x=((x+2))));
}
((x=((x?10:20))));
return x;
})());
const THREE=((()=>{const a=([]);
let i=0;
while(((i<5))){(a.push(i++));
if(((i===2)))continue;
if(((i===4)))break;
}
return a;
})());
const MODFN=((()=>{const mod2=((n)=>(n%2));
const mod3=((n)=>(n%3));
return (([1,2,3,4,5,6,7,8,9]).map((x)=>((mod2(x))+(mod3(x)))));
})());
const SWAPPED=((()=>{let x=1;
let y=2;
const t=x;
((x=y));
((y=t));
return ([x,y]);
})());
const AVG=((()=>{const a=([10,20,30,40,50]);
return (((a.reduce((s,v)=>(s+v),0))/(a.length)));
})());
const HIST=((()=>{const counts=(new Map());
for (const c of "banana")(counts.set(c,((((counts.get(c))||0))+1)));
return ((([...counts]).map(([c,n])=>(((c+":"))+n))).join(" "));
})());
