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

async function resolveSid(id) {
  id = String(id || "").trim().replace(/\/+$/, "");
  let m = id.match(/(?:profiles\/)?(7656119\d{10})$/); if (m) return m[1];
  m = id.match(/(?:id\/)?([A-Za-z0-9_-]{2,32})$/); if (!m) return null;
  try {
    const r = await fetch(`https://steamcommunity.com/id/${m[1]}/?xml=1`, { headers: { "User-Agent": "Mozilla/5.0" } });
    const x = await r.text(); const s = x.match(/<steamID64>(\d{17})<\/steamID64>/); return s ? s[1] : null;
  } catch { return null }
}

async function inventory(env, sid) {
  const key = "inv2:" + sid;
  if (env.KV) { const c = await env.KV.get(key, "json"); if (c && c.items) return c }
  let names = [], items = [], priv = false, err = null;
  try {
    const H = { "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/130 Safari/537.36", "Accept": "application/json", "Referer": `https://steamcommunity.com/profiles/${sid}/inventory` };
    let r = await fetch(`https://steamcommunity.com/inventory/${sid}/730/2?l=english&count=2000`, { headers: H });
    for (let k = 0; k < 2 && r.status === 429; k++) { await new Promise(x => setTimeout(x, 800 * (k + 1))); r = await fetch(`https://steamcommunity.com/inventory/${sid}/730/2?l=english&count=${k ? 500 : 1000}`, { headers: H }) }
    if (r.status === 403 || r.status === 401) priv = true;
    else if (!r.ok) err = "steam " + r.status;
    else {
      const j = await r.json();
      if (!j || j.success === false) priv = true;
      else {
        const cnt = {}; for (const a of (j.assets || [])) cnt[a.classid + "_" + a.instanceid] = (cnt[a.classid + "_" + a.instanceid] || 0) + 1;
        const m = new Map();
        for (const d of (j.descriptions || [])) { if (!d.marketable && !/\s\|\s/.test(d.market_hash_name || "")) continue; /* скины в трейд-бане: marketable=0, но это всё равно скины */ m.set(d.market_hash_name, (m.get(d.market_hash_name) || 0) + (cnt[d.classid + "_" + d.instanceid] || 1)) }
        names = [...m.keys()]; items = [...m.entries()];
      }
    }
  } catch (e) { err = String(e) }
  const out = { names, items, private: priv, error: err, t: Date.now() };
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

/* ---------- розыгрыши ---------- */
const GW_DEFAULT = [{
  id: "g1", title: "3 скина за вход через Steam", starts: Date.parse("2026-10-21T17:00:00Z"), ends: Date.parse("2026-11-08T17:00:00Z"), status: "active", code: "",
  items: [
    { n: "AK-47 | Nouveau Rouge", w: "WW", f: 0.4292, st: false },
    { n: "M4A1-S | Emphorosaur-S", w: "MW", f: 0.1002, st: true },
    { n: "Desert Eagle | Serpent Strike", w: "MW", f: 0.0700, st: false }
  ],
  winners: []
}];
async function gwAll(env) { const v = env.KV ? await env.KV.get("gw:all", "json") : null; return Array.isArray(v) ? v : GW_DEFAULT }
async function gwSave(env, list) { await env.KV.put("gw:all", JSON.stringify(list)) }
const gwPublic = (g, count) => ({ id: g.id, title: g.title, starts: g.starts, ends: g.ends, status: g.status, items: g.items, hasCode: !!g.code, count: count || 0,
  winners: (g.winners || []).map(w => ({ i: w.i, sid: w.sid, n: w.n, a: w.a, at: w.at })) });
const gwActive = g => g.status !== "ended" && Date.now() < g.ends && Date.now() >= (g.starts || 0);
const TW_RE = /^[A-Za-z0-9_]{3,25}$/;
const twNorm = v => String(v || "").trim().replace(/^@/, "").replace(/^(https?:\/\/)?(www\.|m\.)?twitch\.tv\//i, "").replace(/[/?#].*$/, "");
const TRADE_RE = /^https:\/\/steamcommunity\.com\/tradeoffer\/new\/\?partner=(\d+)&token=([A-Za-z0-9_-]{6,16})$/;
async function gwCount(env, id) { return +((await env.KV.get("gwn:" + id)) || 0) }
async function gwEntries(env, id) {
  const out = []; let cursor;
  do { const r = await env.KV.list({ prefix: "gwe:" + id + ":", cursor }); for (const k of r.keys) { const v = await env.KV.get(k.name, "json"); if (v) out.push(v) } cursor = r.list_complete ? null : r.cursor } while (cursor);
  return out;
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

    /* история цен (ветка history в GitHub), с кешем */
    if (p.startsWith("/hist/")) {
      const f = p.slice(6); if (!/^(meta|\d{2})\.json$/.test(f)) return json({ error: "nf" }, 404);
      const cache = caches.default, ck = new Request("https://hist.cache/" + f);
      let r = await cache.match(ck);
      if (!r) {
        const g = await fetch("https://raw.githubusercontent.com/viv1spr/skin-set/history/" + f, { cf: { cacheTtl: 600 } });
        if (!g.ok) return json({ error: "upstream " + g.status }, 502);
        r = new Response(await g.text(), { headers: { ...cors, "Content-Type": "application/json", "Cache-Control": "public, max-age=1800" } });
        await cache.put(ck, r.clone());
      }
      return r;
    }
    /* матчи CS2 из PandaScore (токен — секрет PANDASCORE), с кешем: /matches?type=running|upcoming|past */
    if (p === "/matches") {
      const type = ["running", "upcoming", "past"].includes(u.searchParams.get("type")) ? u.searchParams.get("type") : "upcoming";
      if (!env.PANDASCORE) return json({ error: "notoken", list: [] });
      const ttl = type === "running" ? 45 : 300;
      const cache = caches.default, ck = new Request("https://matches.cache/" + type);
      let r = await cache.match(ck);
      if (!r) {
        const q = type === "past" ? "per_page=60&sort=-end_at" : type === "upcoming" ? "per_page=80&sort=begin_at" : "per_page=50";
        const g = await fetch(`https://api.pandascore.co/csgo/matches/${type}?${q}`, { headers: { Authorization: "Bearer " + env.PANDASCORE, Accept: "application/json" } });
        if (!g.ok) return json({ error: "upstream " + g.status, list: [] }, 502);
        const raw = await g.json();
        const list = raw.map(m => ({
          id: m.id, name: m.name, st: m.status, b: m.begin_at, e: m.end_at, bo: m.number_of_games, w: m.winner_id,
          t: (m.opponents || []).map(o => o.opponent).filter(Boolean).map(o => ({ id: o.id, n: o.name, a: o.acronym, i: o.image_url, c: o.location })),
          s: (m.results || []).map(x => ({ id: x.team_id, s: x.score })),
          l: m.league ? { n: m.league.name, i: m.league.image_url } : null, se: m.serie ? m.serie.full_name : "", tu: m.tournament ? m.tournament.name : "", tier: (m.tournament && m.tournament.tier) || (m.serie && m.serie.tier) || "",
          tv: (m.streams_list || []).filter(x => x.raw_url).map(x => ({ u: x.raw_url, lg: x.language, m: !!x.main, o: !!x.official }))
        }));
        r = new Response(JSON.stringify({ list, t: Date.now() }), { headers: { ...cors, "Content-Type": "application/json", "Cache-Control": "public, max-age=" + ttl } });
        await cache.put(ck, r.clone());
      }
      return r;
    }
    /* публичный инвентарь любого профиля: /invp?id=<steamid64|vanity|ссылка> */
    if (p === "/invp") {
      const sid = await resolveSid(u.searchParams.get("id")); if (!sid) return json({ error: "profile" }, 404);
      const [inv, pr] = await Promise.all([inventory(env, sid), steamProfile(sid)]);
      return json({ ...inv, sid, n: pr.n, a: pr.a });
    }

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


    /* розыгрыши: публичный список */
    if (p === "/gw") {
      const list = await gwAll(env); const out = [];
      for (const g of list) out.push(gwPublic(g, env.KV ? await gwCount(env, g.id) : 0));
      return json({ list: out, now: Date.now() }, 200, { "Cache-Control": "public, max-age=20" });
    }
    /* мои участия */
    if (p === "/gw/me") {
      const t = await readToken(env, u.searchParams.get("t")); if (!t) return json({ error: "auth" }, 401);
      const list = await gwAll(env); const mine = {};
      for (const g of list) { const e = await env.KV.get("gwe:" + g.id + ":" + t.sid, "json"); if (e) mine[g.id] = { tk: e.tk, code: !!e.code, trade: e.trade, tw: e.tw || "" } }
      return json({ mine });
    }
    /* участвовать: POST {t,id,trade,code} */
    if (p === "/gw/enter" && req.method === "POST") {
      const b = await req.json().catch(() => ({}));
      const t = await readToken(env, b.t); if (!t) return json({ error: "auth" }, 401);
      const list = await gwAll(env); const g = list.find(x => x.id === b.id);
      if (!g) return json({ error: "nogw" }, 404);
      if (!gwActive(g)) return json({ error: "ended" }, 400);
      const trade = String(b.trade || "").trim(); const m = trade.match(TRADE_RE);
      if (!m) return json({ error: "trade" }, 400);
      if ((BigInt(m[1]) + 76561197960265728n).toString() !== String(t.sid)) return json({ error: "tradeOwner" }, 400);
      const tw = twNorm(b.tw); if (!TW_RE.test(tw)) return json({ error: "tw" }, 400);
      const key = "gwe:" + g.id + ":" + t.sid; const old = await env.KV.get(key, "json");
      const codeOk = !!(g.code && String(b.code || "").trim().toLowerCase() === String(g.code).trim().toLowerCase());
      if (b.code && g.code && !codeOk && !(old && old.code)) return json({ error: "code" }, 400);
      const e = { sid: t.sid, n: t.n, a: t.a, trade, tw, code: codeOk || !!(old && old.code), t: old ? old.t : Date.now() };
      e.tk = 1 + (e.code ? 1 : 0);
      await env.KV.put(key, JSON.stringify(e));
      if (!old) await env.KV.put("gwn:" + g.id, String((await gwCount(env, g.id)) + 1));
      return json({ ok: true, tk: e.tk, code: e.code, count: await gwCount(env, g.id) });
    }
    /* админка: розыгрыши */
    if (p === "/api/gw") {
      if (!isAdmin(req, env)) return json({ error: "Неверный ключ админки" }, 401);
      if (req.method === "GET") {
        const list = await gwAll(env); const out = [];
        for (const g of list) { const es = await gwEntries(env, g.id); out.push({ ...g, count: es.length, entries: es.sort((a, b) => a.t - b.t) }) }
        return json({ list: out });
      }
      if (req.method === "POST") {
        const b = await req.json().catch(() => ({}));
        if (!Array.isArray(b.list)) return json({ error: "list" }, 400);
        const cur = await gwAll(env);
        const clean = b.list.map(g => ({ id: String(g.id || "").replace(/[^a-z0-9_-]/gi, "").slice(0, 24) || ("g" + Date.now()), title: String(g.title || "").slice(0, 120),
          starts: +g.starts || Date.now(), ends: +g.ends || Date.now() + 7 * 864e5, status: g.status === "ended" ? "ended" : "active", code: String(g.code || "").slice(0, 40),
          items: (g.items || []).slice(0, 10).map(i => ({ n: String(i.n || "").slice(0, 80), w: String(i.w || "").slice(0, 2), f: i.f === "" || i.f == null ? null : +i.f, st: !!i.st })),
          winners: (cur.find(x => x.id === g.id) || {}).winners || [] }));
        await gwSave(env, clean); return json({ ok: true });
      }
    }
    if (p === "/api/gw/draw" && req.method === "POST") {
      if (!isAdmin(req, env)) return json({ error: "Неверный ключ админки" }, 401);
      const b = await req.json().catch(() => ({})); const list = await gwAll(env); const g = list.find(x => x.id === b.id);
      if (!g) return json({ error: "nogw" }, 404);
      const item = +b.item || 0; g.winners = (g.winners || []).filter(w => w.i !== item);
      const taken = new Set(g.winners.map(w => w.sid));
      const pool = (await gwEntries(env, g.id)).filter(e => !taken.has(e.sid));
      if (!pool.length) return json({ error: "Нет участников" }, 400);
      const tot = pool.reduce((a, e) => a + (e.tk || 1), 0);
      const rnd = new Uint32Array(1); crypto.getRandomValues(rnd); let x = rnd[0] / 2 ** 32 * tot, win = pool[0];
      for (const e of pool) { x -= (e.tk || 1); if (x < 0) { win = e; break } }
      g.winners.push({ i: item, sid: win.sid, n: win.n, a: win.a, trade: win.trade, tw: win.tw || "", at: Date.now() });
      await gwSave(env, list);
      return json({ winner: win, pool: pool.map(e => ({ n: e.n, a: e.a })) });
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
