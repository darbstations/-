# -*- coding: utf-8 -*-
"""
يجمع المنشآت المحيطة بكل محطة من خرائط جوجل عبر Apify، ثم يكتب pois.json.

التشغيل:
    export APIFY_TOKEN=xxxxxxxx
    python3 collect_pois.py

بعد انتهائه:
    python3 build_workbook.py && python3 build_report.py

ملاحظة: يتطلب حساب Apify ضمن حد الاستخدام الشهري. عند تجاوز الحد يعيد الـ API
الخطأ "Monthly usage hard limit exceeded" ويتوقف السكربت برسالة واضحة.
"""
import json, math, os, sys, time, urllib.request, urllib.error

TOKEN = os.environ.get("APIFY_TOKEN")
ACTOR = "compass~crawler-google-places"
BASE  = "https://api.apify.com/v2"
RADIUS_KM = 5.0

# مصطلح البحث ← الفئة التي يُصنَّف تحتها
TERMS = {
    "محطة وقود":      "محطات وقود منافسة",
    "تأجير سيارات":   "تأجير السيارات",
    "حج وعمرة":       "مكاتب الحج والعمرة",
    "شركة":           "الشركات الحكومية والخاصة",
    "حكومي":          "الشركات الحكومية والخاصة",
}
CATS = ["محطات وقود منافسة", "تأجير السيارات", "مكاتب الحج والعمرة", "الشركات الحكومية والخاصة"]

GOV_HINTS = ["حكوم", "وزارة", "أمانة", "بلدية", "إمارة", "هيئة", "مصلحة", "محكمة",
             "إدارة تعليم", "مرور", "جوازات", "government", "city hall"]

R = 6371.0088
def hav(a_lat, a_lng, b_lat, b_lng):
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dp, dl = p2 - p1, math.radians(b_lng - a_lng)
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))

DIRS = ["شمال","شمال شرق","شرق","جنوب شرق","جنوب","جنوب غرب","غرب","شمال غرب"]
def bearing(a_lat, a_lng, b_lat, b_lng):
    p1, p2 = math.radians(a_lat), math.radians(b_lat)
    dl = math.radians(b_lng - a_lng)
    y = math.sin(dl)*math.cos(p2)
    x = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
    return DIRS[int(((math.degrees(math.atan2(y, x)) + 360) % 360 + 22.5)//45) % 8]

def bbox(lat, lng, km):
    dlat = km/110.574
    dlng = km/(111.320*math.cos(math.radians(lat)))
    return [[[lng-dlng, lat-dlat], [lng+dlng, lat-dlat],
             [lng+dlng, lat+dlat], [lng-dlng, lat+dlat], [lng-dlng, lat-dlat]]]

def api(path, payload=None):
    url = f"{BASE}{path}{'&' if '?' in path else '?'}token={TOKEN}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data,
        headers={"Content-Type": "application/json"}, method="POST" if data else "GET")
    try:
        return json.loads(urllib.request.urlopen(req, timeout=300).read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        if "hard limit" in body or e.code == 402:
            sys.exit("\n✖ حساب Apify تجاوز الحد الشهري للاستخدام.\n"
                     "  ارفع الحد من: https://console.apify.com/billing ثم أعد التشغيل.\n")
        sys.exit(f"✖ خطأ من Apify ({e.code}): {body[:400]}")

def scrape(station):
    """يشغّل الـ actor لمحطة واحدة ويعيد قائمة الأماكن الخام."""
    run = api(f"/acts/{ACTOR}/runs", {
        "searchStringsArray": list(TERMS),
        "customGeolocation": {"type": "Polygon",
                              "coordinates": bbox(station["lat"], station["lng"], RADIUS_KM)},
        "maxCrawledPlacesPerSearch": 40,
        "language": "ar", "countryCode": "sa", "skipClosedPlaces": True,
    })["data"]
    rid = run["id"]
    while True:                                   # انتظار انتهاء التشغيل
        st = api(f"/actor-runs/{rid}")["data"]
        if st["status"] in ("SUCCEEDED", "FAILED", "ABORTED", "TIMED-OUT"): break
        print(f"    … {st['status']}"); time.sleep(15)
    if st["status"] != "SUCCEEDED":
        print(f"    ⚠ انتهى بحالة {st['status']} — تم التخطي"); return []
    return api(f"/datasets/{st['defaultDatasetId']}/items?clean=true&limit=1000")

def classify(place, term_cat):
    """يحدّد الفئة النهائية والقطاع اعتماداً على تصنيف جوجل والاسم."""
    blob = f"{place.get('categoryName','')} {place.get('title','')}".lower()
    if term_cat == "الشركات الحكومية والخاصة":
        sector = "حكومي" if any(h in blob for h in GOV_HINTS) else "خاص"
        return term_cat, sector
    return term_cat, ""

def main():
    if not TOKEN:
        sys.exit("✖ لم يُضبط APIFY_TOKEN. نفّذ: export APIFY_TOKEN=...")
    geo = json.load(open("geo.json", encoding="utf-8"))
    out = {}
    for s in geo["stations"]:
        print(f'▸ {s["code"]} {s["name"]}')
        rec = {c: [] for c in CATS}
        seen = set()
        for place in scrape(s):
            lat, lng = place.get("location", {}).get("lat"), place.get("location", {}).get("lng")
            name = (place.get("title") or "").strip()
            if not (lat and lng and name): continue
            d = hav(s["lat"], s["lng"], lat, lng)
            if d > RADIUS_KM: continue                      # خارج النطاق الدائري
            key = (name, round(lat, 5), round(lng, 5))
            if key in seen: continue
            seen.add(key)
            term_cat = TERMS.get(place.get("searchString"), "الشركات الحكومية والخاصة")
            cat, sector = classify(place, term_cat)
            common = [place.get("address") or "", round(lat, 6), round(lng, 6),
                      round(d, 2), bearing(s["lat"], s["lng"], lat, lng),
                      place.get("phone") or "", place.get("website") or ""]
            if cat == "الشركات الحكومية والخاصة":
                rec[cat].append([name, sector, place.get("categoryName") or ""] + common + ["", ""])
            else:
                rec[cat].append([name, place.get("categoryName") or ""] + common +
                                [place.get("totalScore") or "", place.get("reviewsCount") or "", ""])
        for c in CATS: rec[c].sort(key=lambda r: r[5] if c == "الشركات الحكومية والخاصة" else r[4])
        rec["counts"] = {c: len(rec[c]) for c in CATS}
        out[s["code"]] = rec
        print("   ", " · ".join(f"{c}: {len(rec[c])}" for c in CATS))
    json.dump(out, open("pois.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\n✔ كُتب pois.json — الآن: python3 build_workbook.py && python3 build_report.py")

if __name__ == "__main__":
    main()
