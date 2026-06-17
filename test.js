const GISTS = {
    "v1":     "ca4e3c7fec042fe7beccd25659e7c6a9",
    "v1.0.1": "62efef9b57125303355325ee406b6e1",
    "v1.0.4": "753f452a23ae4671c420b889aeff31a2",
};
const loadedLibs = {};
function loadLib(src) {
    return new Promise((resolve) => {
        if (loadedLibs[src]) return resolve();
        loadedLibs[src] = true;
        const s = document.createElement("script");
        s.src = src;
        s.onload = resolve;
        document.head.appendChild(s);
    });
}
// REQUIRE
async function loadDependencies(version) {
    if (["v1", "v1.0.1", "v1.0.4"].includes(version)) { // require for these version
        await loadLib("https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js");
        await loadLib("https://cdnjs.cloudflare.com/ajax/libs/msgpack-lite/0.1.26/msgpack.min.js");
    }
}
// loader
function showLoader(version) {
    const old = document.getElementById("moonlight-loader");
    if (old) old.remove();
    const loader = document.createElement("div");
    loader.id = "moonlight-loader";
    loader.innerHTML = `
        <div class="ml-spinner"></div>
<div class="ml-text">Loading Moonlight ${version.toUpperCase()}</div>
        <div class="ml-sub">Injecting modules...</div>
    `;
    loader.style.cssText = `
        position:fixed;
        inset:0;
        background:
            radial-gradient(circle at top, rgba(120,120,255,.18), transparent 60%),
            radial-gradient(circle at bottom, rgba(192,132,252,.18), transparent 60%),
            rgba(0,0,0,.92);

        display:flex;
        flex-direction:column;
        justify-content:center;
        align-items:center;

        gap:10px;

        color:white;
        font-family:Arial;
        z-index:999999;
    `;

    document.body.appendChild(loader);
    return loader;
}
// load script
function loadVersion(version) {
    const gistId = GISTS[version];
    if (!gistId) return alert("This version not found");
    const loader = showLoader(version);
    loadDependencies(version).then(() => {
        GM_xmlhttpRequest({
            method: "GET",
            url: `https://gist.githubusercontent.com/raw/${gistId}`,
            onload(codeRes) {
                try {
                    const script = document.createElement("script");
                    script.textContent = codeRes.responseText;
                    document.head.appendChild(script);
                    script.remove();
                } catch (e) {
                    loader.remove();
                }
            },
            onerror() {
                loader.remove();
            }
        });
    });
}
// close menu
function closeMenu() {
    document.getElementById("moonlight-wrapper")?.remove();
   document.getElementById("moonlight-bg")?.remove();

}
//star

// menu
function createMenu() {

  const font = document.createElement("link");
font.rel = "stylesheet";
font.href = "https://fonts.googleapis.com/css2?family=Lilita+One&display=swap";
document.head.appendChild(font);
    const style = document.createElement("style");
    style.textContent = `
        * { box-sizing: border-box; }

        @keyframes float {
            0%,100% { transform: translateY(0); }
            50% { transform: translateY(-8px); }
        }

        @keyframes gradientMove {
            0% { background-position: 0%; }
            100% { background-position: 200%; }
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        @keyframes twinkle {
    0%,100% {
        opacity:.15;
        transform:scale(1);
    }

    50% {
        opacity:1;
        transform:scale(1.5);
    }
}
#moonlight-tilt{
    transform-style:preserve-3d;
    transition:transform .12s ease-out;
    will-change:transform;
}
        #moonlight-bg {
            position: fixed;
            inset: 0;
            background:
                radial-gradient(circle at top, rgba(120,120,255,.15), transparent 60%),
                radial-gradient(circle at bottom, rgba(192,132,252,.12), transparent 60%),
                linear-gradient(rgba(0,0,0,.65), rgba(0,0,0,.9)),
                url("https://tse1.mm.bing.net/th/id/OIP.flMS2UfIR5H-07Os_EuOoAHaEK?r=0&cb=thfvnextfalcon2&rs=1&pid=ImgDetMain&o=7&rm=3");
            background-size: cover;
            background-position: center;
            z-index: 999997;
            position:fixed; /*idk why add*/
            inset:0;
            overflow:hidden;
        }


        #moonlight-wrapper {
            position: fixed;
            inset: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            z-index: 999999;
        }

    #moonlight-menu {
            width: 430px;
            padding: 26px;

            background: rgba(18,18,28,.65);
            backdrop-filter: blur(22px);

            border-radius: 26px;

            border: 1px solid rgba(255,255,255,.08);

            color: white;

            font-family: Arial;
            text-align: center;

            animation: float 3s ease-in-out infinite;
    position: relative;

    background: rgba(15,15,25,.75);
    backdrop-filter: blur(30px);

    border: 1px solid rgba(255,255,255,.08);

    overflow: hidden;
    transform-style:preserve-3d;
    transition:transform .15s ease-out;

}
#moonlight-menu::after{
    content:"";

    position:absolute;
    inset:0;

    border-radius:30px;

    padding:2px;

    background:
        linear-gradient(
            90deg,
            #7aa2ff,
            #c084fc,
            #7aa2ff
        );

    background-size:300%;

    animation:gradientMove 4s linear infinite;

    -webkit-mask:
        linear-gradient(#fff 0 0) content-box,
        linear-gradient(#fff 0 0);

    -webkit-mask-composite:xor;

    pointer-events:none;
}

        .moonlight-header {
            display:flex;
            flex-direction:column;
            align-items:center;
        }
  #moonlight-logo {
            width: 92px;
            height: 92px;
            display:flex;
            justify-content:center;
            align-items:center;

            font-size: 52px;

            border-radius: 50%;

            background: linear-gradient(135deg, rgba(120,120,255,.35), rgba(192,132,252,.35));

            box-shadow: 0 0 40px rgba(120,120,255,.25);
        }

#moonlight-title {
    font-family: "Lilita One", cursive;
    font-size: 58px;
    letter-spacing: 2px;

    background: linear-gradient(
        90deg,
        #7aa2ff,
        #ffffff,
        #c084fc,
        #7aa2ff
    );

    background-size: 300%;
    animation: gradientMove 5s linear infinite;
-webkit-background-clip:text;
    -webkit-text-fill-color:transparent;

    filter: drop-shadow(0 0 20px rgba(122,162,255,.5));
}

        #moonlight-sub {
            margin-top: 8px;
            margin-bottom: 18px;

            font-size: 12px;
            color: rgba(255,255,255,.55);
        }
 .moonlight-btn::before {
    content:"";

    position:absolute;
    top:0;
    left:-120%;

    width:100%;
    height:100%;

    background:linear-gradient(
        90deg,
        transparent,
        rgba(255,255,255,.25),
        transparent
    );

    transition:.5s;
}
        .moonlight-btn {
            width: 100%;
            padding: 14px;
            margin-top: 10px;

            border-radius: 14px;
            border: 1px solid rgba(255,255,255,.08);

            cursor: pointer;
            font-weight: 700;
            color: white;

            transition: .2s;

            backdrop-filter: blur(10px);
             position: relative;
    overflow: hidden;

    border-radius: 16px;

    transition: .25s;
        }
.moonlight-btn:hover::before {
    left:120%;
}
        .moonlight-btn:hover {
            transform: translateY(-3px);
            filter: brightness(1.15);
        }

        #moonlight-v1 {
            background: linear-gradient(135deg,#2563eb,#6366f1);
        }

        #moonlight-v1-0-1 {
           background: linear-gradient(135deg,#2563eb,#6366f1);
        }
        #moonlight-v1-0-4 {
        background: linear-gradient(135deg,#9333ea,#c084fc);
        }
        #moonlight-footer {
            margin-top: 14px;
            font-size: 11px;
            color: rgba(255,255,255,.4);
        }


        .ml-spinner {
            width: 60px;
            height: 60px;
            border-radius: 50%;
            border: 3px solid rgba(255,255,255,.1);
            border-top: 3px solid #7aa2ff;
            animation: spin 1s linear infinite;
            box-shadow: 0 0 25px rgba(122,162,255,.25);
        }
.ml-text {
    font-family: "Lilita One", cursive;
    font-size: 24px;
        background: linear-gradient(90deg,#7aa2ff,#c084fc,#7aa2ff);
            background-size: 200%;
            animation: gradientMove 3s linear infinite;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
}
        .ml-sub {
            font-size: 12px;
            color: rgba(255,255,255,.5);
        }
    `;
    document.head.appendChild(style);
    const bg = document.createElement("div");
    bg.id = "moonlight-bg";
/*const moon = document.createElement("div");
moon.style.cssText = `
    position:absolute;
    width:300px;
    height:300px;
    border-radius:50%;
    top:8%;
    right:8%;
    background:
        radial-gradient(
            circle,
            rgba(255,255,255,.95),
            rgba(122,162,255,.4),
            transparent
        );
    filter:blur(20px);
    animation:moonPulse 4s ease-in-out infinite;
`;
bg.appendChild(moon);*/               // I intended to draw a moon, but I already have a background

  // star color
  const colors = [
    "#ffffff",
    "#7aa2ff",
    "#c084fc"
]; //star background
for (let i = 0; i < 150; i++) {
    const star = document.createElement("div");
    const color =
    colors[Math.floor(Math.random() * colors.length)];
    star.style.cssText = `
        position:absolute;
        width:${Math.random() * 3 + 1}px;
        height:${Math.random() * 3 + 1}px;

        border-radius:50%;

        background:${color};

        box-shadow:
            0 0 8px ${color},
            0 0 15px ${color};

        left:${Math.random() * 100}%;
        top:${Math.random() * 100}%;

        opacity:${Math.random()};

        animation:twinkle ${
            Math.random() * 3 + 2
        }s infinite;
    `;

    bg.appendChild(star);
}
    const wrapper = document.createElement("div");
    wrapper.id = "moonlight-wrapper";

    const menu = document.createElement("div");
    menu.id = "moonlight-menu";
    menu.innerHTML = `
        <div class="moonlight-header">
            <div id="moonlight-logo">🌙</div>
            <div id="moonlight-title">Lonely Moonlight</div>
           </div>
        <div id="moonlight-sub">Premium Stable Loader</div>
        <button id="moonlight-v1"     class="moonlight-btn">Lonely Moonlight V_1</button>
        <button id="moonlight-v1-0-1" class="moonlight-btn">Lonely Moonlight V_1.0.1</button>
        <button id="moonlight-v1-0-4" class="moonlight-btn">Lonely Moonlight V_1.0.4</button>
        <div id="moonlight-footer">Moonlight • Stable Build</div>
    `;
const tilt = document.createElement("div");
tilt.id = "moonlight-tilt";
tilt.appendChild(menu);
wrapper.appendChild(tilt);
document.body.appendChild(bg);
document.body.appendChild(wrapper);
tilt.addEventListener("mousemove", (e) => {
    const rect = tilt.getBoundingClientRect();

    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const rotateY =
        ((x / rect.width) - 0.5) * 18;

    const rotateX =
        ((y / rect.height) - 0.5) * -18;

    tilt.style.transform = `
        perspective(1200px)
        rotateX(${rotateX}deg)
        rotateY(${rotateY}deg)
    `;
});

tilt.addEventListener("mouseleave", () => {
    tilt.style.transform = `
        perspective(1200px)
        rotateX(0deg)
        rotateY(0deg)
    `;
});
menu.addEventListener("mouseleave", () => {
    menu.style.transform = `
        perspective(1000px)
        rotateX(0deg)
        rotateY(0deg)
    `;
});
    document.getElementById("moonlight-v1").onclick = () => {
closeMenu();
    loadVersion("v1");
};
  document.getElementById("moonlight-v1-0-1").onclick = () => {
closeMenu();
    loadVersion("v1.0.1");
};
document.getElementById("moonlight-v1-0-4").onclick = () => {
    closeMenu();
    loadVersion("v1.0.4");
};

}
//init
createMenu();
