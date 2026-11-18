// Прокси инвентаря Steam для skin-set.com (Vercel, не Cloudflare: у Cloudflare Steam режет запросы 429).
// GET /api/inv?sid=7656119XXXXXXXXXX → { items:[[market_hash_name,count]], private, error }
const ORIG = /^https:\/\/(www\.)?skin-set\.com$|^http:\/\/localhost(:\d+)?$/;
const UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0 Safari/537.36";

module.exports = async (req, res) => {
  const o = req.headers.origin || "";
  if (ORIG.test(o)) res.setHeader("Access-Control-Allow-Origin", o);
  res.setHeader("Vary", "Origin");
  if (req.method === "OPTIONS") return res.status(204).end();
  const sid = String((req.query && req.query.sid) || "");
  if (!/^7656119\d{10}$/.test(sid)) return res.status(400).json({ error: "sid" });
  const H = { "User-Agent": UA, "Accept": "application/json", "Accept-Language": "en-US,en;q=0.9", "Referer": `https://steamcommunity.com/profiles/${sid}/inventory` };
  let r, st = 0;
  for (let k = 0; k < 3; k++) {
    r = await fetch(`https://steamcommunity.com/inventory/${sid}/730/2?l=english&count=${k ? 1000 : 2000}`, { headers: H });
    st = r.status;
    if (st !== 429) break;
    await new Promise(x => setTimeout(x, 700 * (k + 1)));
  }
  if (st === 403 || st === 401) { const t = await r.text().catch(() => ""); return res.status(200).json({ items: [], private: true, error: null, dbg: { st, body: t.slice(0, 160) } }) }
  if (!r.ok) return res.status(200).json({ items: [], private: false, error: "steam " + st });
  const txt = await r.text(); let j = null; try { j = JSON.parse(txt) } catch (e) {}
  if (!j || j.success === false) return res.status(200).json({ items: [], private: true, error: null, dbg: { st, body: txt.slice(0, 160) } });
  const cnt = {}; for (const a of (j.assets || [])) { const k = a.classid + "_" + a.instanceid; cnt[k] = (cnt[k] || 0) + 1 }
  const m = new Map();
  for (const d of (j.descriptions || [])) {
    const n = d.market_hash_name || ""; if (!n) continue;
    if (!d.marketable && !/\s\|\s/.test(n)) continue;
    m.set(n, (m.get(n) || 0) + (cnt[d.classid + "_" + d.instanceid] || 1));
  }
  res.setHeader("Cache-Control", "public, s-maxage=600, stale-while-revalidate=300");
  return res.status(200).json({ items: [...m.entries()], private: false, error: null, total: j.total_inventory_count || 0 });
};
