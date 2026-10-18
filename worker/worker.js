/*
 * Skinset worker (Cloudflare Workers)
 * — вход через Steam (OpenID 2.0), профиль и инвентарь CS2
 * — трекинговые ссылки и их статистика для админки
 *
 * Привязки (Settings → Variables):
 *   KV         — KV namespace (Bindings → KV namespace, имя переменной KV)
 *   SECRET     — любая длинная случайная строка (Secret)
 *   ADMIN_KEY  — пароль для админки, раздел «Ссылки» (Secret)
 */
const SITE = "https://skin-set.com";
const ALLOWED = [/^https:\/\/(www\.)?skin-set\.com(\/|$)/, /^http:\/\/localhost(:\d+)?(\/|$)/];
const OPENID = "https://steamcommunity.com/openid/login";

const cors = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Headers": "Authorization, Content-Type", "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS" };
const json = (d, s = 200, h = {}) => new Response(JSON.stringify(d), { status: s, headers: { "Content-Type": "application/json; charset=utf-8", ...cors, ...h } });
const b64u = buf => btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
const ub64 = s => decodeURIComponent(escape(atob(s.replace(/-/g, "+").replace(/_/g, "/"))));
const okReturn = r => r && ALLOWED.some(x => x.test(r));

async function hmac(secret, data) {
  const k = await crypto.subtle.importKey("raw", new TextEncoder().encode(secret), { name: "HMAC", hash: "SHA-256" }, false, ["sign"]);
  return b64u(await crypto.subtle.sign("HMAC", k, new TextEncoder().encode(data)));
}
async function makeToken(env, p) {
  const body = btoa(unescape(encodeURIComponent(JSON.stringify(p)))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  return body + "." + await hmac(env.SECRET, body);
}
async function readToken(env, t) {
  if (!t || !t.includes(".")) return null;
  const [body, sig] = t.split(".");
  if (await hmac(env.SECRET, body) !== sig) return null;
  try { const p = JSON.parse(ub64(body)); return p.exp > Date.now() / 1000 ? p : null } catch { return null }
}

async function steamProfile(sid) {
  try {
    const r = await fetch(`https://steamcommunity.com/profiles/${sid}/?xml=1`, { headers: { "User-Agent": "Mozilla/5.0" } });
    const x = await r.text();
    const tag = n => { const m = x.match(new RegExp(`<${n}>(?:<!\\[CDATA\\[)?([\\s\\S]*?)(?:\\]\\]>)?</${n}>`)); return m ? m[1].trim() : "" };
    return { n: tag("steamID").slice(0, 32) || "Steam", a: tag("avatarMedium") };
  } catch { return { n: "Steam", a: "" } }
}

async function inventory(env, sid) {
  const key = "inv:" + sid;
  if (env.KV) { const c = await env.KV.get(key, "json"); if (c) return c }
  let names = [], priv = false, err = null;
  try {
    const r = await fetch(`https://steamcommunity.com/inventory/${sid}/730/2?l=english&count=2000`, { headers: { "User-Agent": "Mozilla/5.0", "Accept": "application/json" } });
    if (r.status === 403 || r.status === 401) priv = true;
    else if (!r.ok) err = "steam " + r.status;
    else {
      const j = await r.json();
      if (!j || j.success === false) priv = true;
      else names = [...new Set((j.descriptions || []).filter(d => d.marketable).map(d => d.market_hash_name))];
    }
  } catch (e) { err = String(e) }
  const out = { names, private: priv, error: err, t: Date.now() };
  if (env.KV && !err) await env.KV.put(key, JSON.stringify(out), { expirationTtl: 900 });
  return out;
}

/* ---------- ссылки ---------- */
const day = () => new Date(Date.now() + 3 * 3600e3).toISOString().slice(0, 10); // МСК
const cleanCode = c => String(c || "").toLowerCase().replace(/[^a-z0-9_-]/g, "").slice(0, 32);
async function getLink(env, code) { return env.KV ? await env.KV.get("link:" + code, "json") : null }
async function listLinks(env) {
  const out = []; let cursor;
  do { const r = await env.KV.list({ prefix: "link:", cursor }); for (const k of r.keys) { const v = await env.KV.get(k.name, "json"); if (v) out.push(v) } cursor = r.list_complete ? null : r.cursor } while (cursor);
  return out.sort((a, b) => b.created - a.created);
}
async function hit(env, code, ev) {
  const l = await getLink(env, code); if (!l) return false;
  const d = day(); l.d = l.d || {}; l.d[d] = l.d[d] || { v: 0, b: 0, p: 0 };
  l[ev] = (l[ev] || 0) + 1; l.d[d][ev] = (l.d[d][ev] || 0) + 1;
  const keep = Object.keys(l.d).sort().slice(-90); l.d = Object.fromEntries(keep.map(k => [k, l.d[k]]));
  await env.KV.put("link:" + code, JSON.stringify(l)); return true;
}
const isAdmin = (req, env) => env.ADMIN_KEY && (req.headers.get("Authorization") || "") === "Bearer " + env.ADMIN_KEY;

export default {
  async fetch(req, env) {
    const u = new URL(req.url), p = u.pathname;
    if (req.method === "OPTIONS") return new Response(null, { headers: cors });

    if (p === "/" || p === "/health") return json({ ok: true, kv: !!env.KV, secret: !!env.SECRET, admin: !!env.ADMIN_KEY });

    /* вход: /login?r=https://skin-set.com/... */
    if (p === "/login") {
      const r = u.searchParams.get("r") || SITE + "/";
      if (!okReturn(r)) return new Response("bad return url", { status: 400 });
      const q = new URLSearchParams({
        "openid.ns": "http://specs.openid.net/auth/2.0", "openid.mode": "checkid_setup",
        "openid.return_to": `${u.origin}/callback?r=${encodeURIComponent(r)}`, "openid.realm": u.origin,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select", "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select"
      });
      return Response.redirect(OPENID + "?" + q, 302);
    }

    if (p === "/callback") {
      const r = u.searchParams.get("r") || SITE + "/";
      if (!okReturn(r) || !env.SECRET) return new Response("bad request", { status: 400 });
      const back = (frag) => Response.redirect(r.split("#")[0] + "#" + frag, 302);
      if (u.searchParams.get("openid.mode") !== "id_res") return back("steam=cancel");
      const rt = u.searchParams.get("openid.return_to") || "";
      if (!rt.startsWith(u.origin + "/callback")) return back("steam=error");
      const body = new URLSearchParams();
      for (const [k, v] of u.searchParams) if (k.startsWith("openid.")) body.set(k, v);
      body.set("openid.mode", "check_authentication");
      const vr = await fetch(OPENID, { method: "POST", body, headers: { "Content-Type": "application/x-www-form-urlencoded" } });
      const vt = await vr.text();
      const m = (u.searchParams.get("openid.claimed_id") || "").match(/^https:\/\/steamcommunity\.com\/openid\/id\/(\d{17})$/);
      if (!/is_valid\s*:\s*true/.test(vt) || !m) return back("steam=error");
      const sid = m[1]; const pr = await steamProfile(sid);
      if (env.KV) {
        const k = "user:" + sid; const o = (await env.KV.get(k, "json")) || { sid, first: Date.now(), c: 0 };
        o.n = pr.n; o.a = pr.a; o.last = Date.now(); o.c = (o.c || 0) + 1; await env.KV.put(k, JSON.stringify(o));
        const dk = "logins:" + day(); await env.KV.put(dk, String(+((await env.KV.get(dk)) || 0) + 1), { expirationTtl: 100 * 86400 });
      }
      const tok = await makeToken(env, { sid, n: pr.n, a: pr.a, exp: Math.floor(Date.now() / 1000) + 30 * 86400 });
      return back("steam=" + tok);
    }

    if (p === "/me") { const t = await readToken(env, u.searchParams.get("t")); return t ? json({ sid: t.sid, n: t.n, a: t.a }) : json({ error: "auth" }, 401) }

    if (p === "/inv") {
      const t = await readToken(env, u.searchParams.get("t")); if (!t) return json({ error: "auth" }, 401);
      return json(await inventory(env, t.sid));
    }

    /* счётчик: /hit?l=CODE&e=v|b|p */
    if (p === "/hit") {
      const code = cleanCode(u.searchParams.get("l")), e = u.searchParams.get("e");
      if (env.KV && code && ["v", "b", "p"].includes(e)) await hit(env, code, e);
      return new Response(null, { status: 204, headers: cors });
    }

    /* короткая ссылка: /l/CODE → сайт */
    if (p.startsWith("/l/")) {
      const code = cleanCode(p.slice(3)); const l = env.KV && code ? await getLink(env, code) : null;
      const dest = new URL(l && l.path ? l.path : "/", SITE); if (l) dest.searchParams.set("l", code);
      return Response.redirect(dest.toString(), 302);
    }

    /* временная диагностика инвентаря */
    if (p === "/api/invdbg") {
      if (!isAdmin(req, env)) return json({ error: "auth" }, 401);
      const sid = u.searchParams.get("sid"); const out = {};
      const vars = {
        c2000: `https://steamcommunity.com/inventory/${sid}/730/2?l=english&count=2000`,
        c500: `https://steamcommunity.com/inventory/${sid}/730/2?l=english&count=500`,
        c75: `https://steamcommunity.com/inventory/${sid}/730/2?count=75`,
        bare: `https://steamcommunity.com/inventory/${sid}/730/2`,
        legacy: `https://steamcommunity.com/profiles/${sid}/inventory/json/730/2`
      };
      for (const [k, url] of Object.entries(vars)) { try { const r = await fetch(url, { headers: { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36", "Accept": "application/json", "Referer": `https://steamcommunity.com/profiles/${sid}/inventory` } }); const t = await r.text(); out[k] = r.status + " " + t.slice(0, 80) } catch (e) { out[k] = String(e) } }
      return json(out);
    }

    /* админка: статистика входов через Steam */
    if (p === "/api/users") {
      if (!isAdmin(req, env)) return json({ error: "Неверный ключ админки" }, 401);
      const users = []; let cursor;
      do { const r = await env.KV.list({ prefix: "user:", cursor }); for (const k of r.keys) { const v = await env.KV.get(k.name, "json"); if (v) users.push(v) } cursor = r.list_complete ? null : r.cursor } while (cursor);
      const days = {}; for (let i = 0; i < 30; i++) { const d = new Date(Date.now() + 3 * 3600e3 - i * 864e5).toISOString().slice(0, 10); days[d] = +((await env.KV.get("logins:" + d)) || 0) }
      return json({ users: users.sort((a, b) => b.last - a.last), days });
    }

    /* админка */
    if (p === "/api/links") {
      if (!isAdmin(req, env)) return json({ error: "Неверный ключ админки" }, 401);
      if (!env.KV) return json({ error: "KV не подключён" }, 500);
      if (req.method === "GET") return json({ links: await listLinks(env) });
      if (req.method === "POST") {
        const b = await req.json().catch(() => ({})); const code = cleanCode(b.code);
        if (!code) return json({ error: "Код: латиница, цифры, - и _" }, 400);
        const old = await getLink(env, code);
        let path = String(b.path || "/").trim(); if (!path.startsWith("/")) path = "/" + path;
        const l = old ? { ...old, name: String(b.name || old.name).slice(0, 80), path } : { code, name: String(b.name || code).slice(0, 80), path, created: Date.now(), v: 0, b: 0, p: 0, d: {} };
        await env.KV.put("link:" + code, JSON.stringify(l)); return json({ link: l });
      }
      if (req.method === "DELETE") { const code = cleanCode(u.searchParams.get("code")); await env.KV.delete("link:" + code); return json({ ok: true }) }
    }
    return json({ error: "not found" }, 404);
  }
};
