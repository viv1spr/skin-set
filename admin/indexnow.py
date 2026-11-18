"""IndexNow: отправляет все URL из sitemap в Яндекс и Bing (ключ — файл aa57cab556b81a481966a349c541c4c2.txt в корне сайта).
Запуск: python3 admin/indexnow.py [--changed N]  (по умолчанию все URL)"""
import json, os, re, sys, urllib.request
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
KEY = "aa57cab556b81a481966a349c541c4c2"
urls = []
for f in ("sitemap.xml", "sitemap-skins.xml"):
    urls += re.findall(r"<loc>([^<]+)</loc>", open(os.path.join(ROOT, f), encoding="utf-8").read())
urls = list(dict.fromkeys(u for u in urls if u.startswith("https://skin-set.com/")))
print(len(urls), "urls")
for ep in ("https://yandex.com/indexnow", "https://api.indexnow.org/indexnow"):
    for i in range(0, len(urls), 9000):
        body = json.dumps({"host": "skin-set.com", "key": KEY, "keyLocation": f"https://skin-set.com/{KEY}.txt", "urlList": urls[i:i + 9000]}).encode()
        req = urllib.request.Request(ep, data=body, headers={"Content-Type": "application/json; charset=utf-8"})
        try:
            r = urllib.request.urlopen(req, timeout=60); print(ep, i, r.status)
        except urllib.error.HTTPError as e:
            print(ep, i, e.code, e.read()[:200])
        except Exception as e:
            print(ep, i, "ERR", e)
