# -*- coding: utf-8 -*-
"""يحسب المسافات وتحليل التداخل بين مواقع محطات درب بمكة المكرمة."""
import json, math

STATIONS = [
    {"code":"MK007","name":"العمرة الجديدة","lat":21.545501760079727,"lng":39.778740694279925},
    {"code":"MK019","name":"عرفات الشرائع","lat":21.477315823386835,"lng":39.915510658283190},
    {"code":"MK017","name":"عرفات الشوقية","lat":21.382832162943180,"lng":39.787308463295240},
    {"code":"MK023","name":"بن درويش",      "lat":21.470436621349847,"lng":39.928912695783350},
    {"code":"MK002","name":"المعيصم",       "lat":21.465715391345107,"lng":39.899769312269010},
]

# معالم مرجعية ثابتة بمكة المكرمة (إحداثيات معروفة، تُستخدم للتوجيه فقط)
LANDMARKS = [
    {"name":"المسجد الحرام","lat":21.4225,"lng":39.8262,"kind":"haram"},
    {"name":"مشعر منى","lat":21.4133,"lng":39.8933,"kind":"mashaer"},
    {"name":"مشعر مزدلفة","lat":21.3897,"lng":39.9370,"kind":"mashaer"},
    {"name":"صعيد عرفات","lat":21.3547,"lng":39.9843,"kind":"mashaer"},
]

R = 6371.0088
def hav(a, b):
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dp = p2 - p1
    dl = math.radians(b["lng"] - a["lng"])
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))

def bearing(a, b):
    p1, p2 = math.radians(a["lat"]), math.radians(b["lat"])
    dl = math.radians(b["lng"] - a["lng"])
    y = math.sin(dl)*math.cos(p2)
    x = math.cos(p1)*math.sin(p2) - math.sin(p1)*math.cos(p2)*math.cos(dl)
    return (math.degrees(math.atan2(y, x)) + 360) % 360

DIRS = ["شمال","شمال شرق","شرق","جنوب شرق","جنوب","جنوب غرب","غرب","شمال غرب"]
def compass(deg): return DIRS[int((deg+22.5)//45) % 8]

# مساحة تقاطع دائرتين متساويتي نصف القطر r ومركزاهما على بعد d
def overlap_ratio(d, r):
    if d >= 2*r: return 0.0
    if d == 0: return 1.0
    x = d/(2*r)
    area = 2*r*r*math.acos(x) - (d/2)*math.sqrt(max(0.0, 4*r*r - d*d))
    return area/(math.pi*r*r)

matrix = {}
for a in STATIONS:
    for b in STATIONS:
        if a["code"] == b["code"]: continue
        matrix[f'{a["code"]}|{b["code"]}'] = round(hav(a,b), 3)

for s in STATIONS:
    others = sorted(
        ({"code":o["code"],"name":o["name"],
          "km":round(hav(s,o),2),"dir":compass(bearing(s,o))}
         for o in STATIONS if o["code"] != s["code"]),
        key=lambda x: x["km"])
    s["neighbors"] = others
    s["nearest_km"] = others[0]["km"]
    s["nearest"] = others[0]["code"]
    s["landmarks"] = [{"name":l["name"],"km":round(hav(s,l),2),
                       "dir":compass(bearing(s,l)),"kind":l["kind"]} for l in LANDMARKS]
    # نسبة تداخل نطاق الخدمة مع أقرب محطة عند أنصاف أقطار مختلفة
    s["overlap"] = {str(r): round(overlap_ratio(others[0]["km"], r)*100, 1)
                    for r in (1, 3, 5)}
    s["maps_url"] = f'https://www.google.com/maps/search/?api=1&query={s["lat"]},{s["lng"]}'

out = {"stations":STATIONS, "landmarks":LANDMARKS, "matrix":matrix,
       "city":"مكة المكرمة", "generated_for":"درب — الخريطة التنافسية للمواقع"}
with open("geo.json","w",encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)

print("مصفوفة المسافات (كم):")
codes = [s["code"] for s in STATIONS]
print("        " + "".join(f"{c:>9}" for c in codes))
for a in STATIONS:
    cells = []
    for c in codes:
        if c == a["code"]:
            cells.append("        —")
        else:
            cells.append("%9.2f" % matrix[a["code"] + "|" + c])
    print("%8s" % a["code"] + "".join(cells))
print()
for s in STATIONS:
    print(f'{s["code"]} {s["name"]}: أقرب محطة {s["nearest"]} على بعد {s["nearest_km"]} كم | '
          f'تداخل 3كم = {s["overlap"]["3"]}% | الحرم {s["landmarks"][0]["km"]} كم {s["landmarks"][0]["dir"]}')
