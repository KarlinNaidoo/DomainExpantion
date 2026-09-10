/**
 * Injected into Bot Crossing. Open / New conversation talks to Domain Expantion
 * in an iframe instead of the terminal.
 */
const CHAT = "http://127.0.0.1:8766";

function panel() {
  let el = document.getElementById("de-chat-panel");
  if (el) return el;
  el = document.createElement("div");
  el.id = "de-chat-panel";
  el.style.cssText =
    "position:fixed;right:12px;bottom:12px;width:min(420px,42vw);height:min(70vh,640px);z-index:40;" +
    "display:none;flex-direction:column;border:1px solid #2c4a3a;border-radius:12px;" +
    "overflow:hidden;box-shadow:0 12px 40px rgba(0,0,0,.45);background:#0e1410;";
  el.innerHTML =
    '<div style="display:flex;align-items:center;justify-content:space-between;padding:8px 10px;background:#162016;color:#cfe8c4;font:12px/1.2 Segoe UI,sans-serif;letter-spacing:.08em;text-transform:uppercase;">Chat<button id="de-chat-close" type="button" style="background:none;border:0;color:#cfe8c4;font-size:18px;cursor:pointer">×</button></div>' +
    '<iframe id="de-chat-frame" title="Domain Expantion chat" style="flex:1;border:0;width:100%;background:#0e1410"></iframe>';
  document.body.appendChild(el);
  document.getElementById("de-chat-close").onclick = () => {
    el.style.display = "none";
  };
  return el;
}

function openChat(ref, isNew) {
  const name = (ref && ref.name) || "supervisor";
  const thread = isNew
    ? "colony-" + crypto.randomUUID()
    : "colony-" + (name === "supervisor" ? "main" : name);
  const url =
    CHAT +
    "/chat.html?thread=" +
    encodeURIComponent(thread) +
    "&agent=" +
    encodeURIComponent(name);
  const el = panel();
  document.getElementById("de-chat-frame").src = url;
  el.style.display = "flex";
}

const orig = window.fetch.bind(window);
window.fetch = async (input, init) => {
  const url = typeof input === "string" ? input : input && input.url;
  const method = (init && init.method) || (input && input.method) || "GET";
  if (method === "POST" && url && String(url).includes("/api/open")) {
    try {
      const body = JSON.parse(init?.body || "{}");
      if (body.harness === "domain-expantion") {
        openChat(body.ref || {}, false);
        return new Response(JSON.stringify({ ok: true, url: "in-page" }), {
          headers: { "Content-Type": "application/json" },
        });
      }
    } catch {
      /* fall through */
    }
  }
  if (method === "POST" && url && String(url).includes("/api/new-session")) {
    try {
      const body = JSON.parse(init?.body || "{}");
      if (!body.harness || body.harness === "domain-expantion") {
        openChat({ name: "supervisor" }, true);
        return new Response(JSON.stringify({ ok: true, url: "in-page" }), {
          headers: { "Content-Type": "application/json" },
        });
      }
    } catch {
      /* fall through */
    }
  }
  return orig(input, init);
};
