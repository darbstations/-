# -*- coding: utf-8 -*-
"""ملف حملة خدمات السيارات وحدها، من ملفها هي.

تُحذف الحملات الثماني الأخرى من البذرة، ويُعطى الملف مفتاح حفظ خاصًا به حتى
لا يلمس سجلّها الكامل في الرابط الآخر مهما فعلت هنا. ويُزال وضع الاستعادة
القسرية: البذرة تملأ متصفحًا فارغًا فقط.

وفي طريقنا صُلّح خطآن في هذه النسخة: صفحتا الملخّص والخطة كانتا تعرضان ما نزل
مع الملف حتى أول تعديل، وتصدير HTML كان يلتقط أول وسم أنماط في الصفحة — وداخل
الرابط يكون أول وسم هو أنماط المضيف لا أنماط الملف.
"""
import json
import re

SRC = 'hers7.html'
KEEP = 'CMP-2026-03'
OUT = '/home/user/-/darb-carwash-campaign.html'
ART = '/home/user/-/darb-carwash-campaign-artifact.html'

s = open(SRC, encoding='utf-8').read()
n = 0


def sub(old, new, why):
    global s, n
    assert old in s, 'missing: ' + why
    s = s.replace(old, new, 1)
    n += 1


def empty_div(html, div_id):
    """يفرّغ حاوية يملؤها الجافاسكربت، بعدّ الوسوم المتداخلة لا بالتخمين."""
    m = re.search(r'<div id="%s"[^>]*>' % re.escape(div_id), html)
    assert m, 'container not found: ' + div_id
    i, depth = m.end(), 1
    for t in re.finditer(r'</?div\b', html[m.end():]):
        depth += 1 if t.group(0) == '<div' else -1
        if depth == 0:
            i = m.end() + t.start()
            break
    else:
        raise AssertionError('unbalanced: ' + div_id)
    return html[:m.end()] + html[i:], i - m.end()


# ---------------------------------------------------- ١ · الحملة وحدها
i = s.index('var SEED = ') + len('var SEED = ')
seed, end = json.JSONDecoder().raw_decode(s[i:])
keep = [c for c in seed if c['code'] == KEEP]
assert len(keep) == 1, 'campaign not found'
s = s[:i] + json.dumps(keep, ensure_ascii=False) + s[i + end:]
n += 1

# ---------------------------------------------------- ٢ · لا استعادة قسرية
sub('var SEEDFORCE=true;\n', '', 'SEEDFORCE declaration')
sub("""    } else if(typeof SEEDFORCE!=='undefined' && SEEDFORCE){
      /* استعادة مطلوبة: نحتفظ بالموجود جانبًا ثم نضع حملاتك مكانه */
      try{ localStorage.setItem(KEY+'-backup', JSON.stringify(campaigns)); }catch(e){}
      campaigns=JSON.parse(JSON.stringify(SEED));
      persist();
      setTimeout(function(){
        say('رجّعنا حملاتك التسع من ملفك. النسخة السابقة محفوظة — اضغط «تراجع» لإرجاعها.',
            14000, 'تراجع', function(){
          try{
            var bk=localStorage.getItem(KEY+'-backup');
            if(bk){ campaigns=JSON.parse(bk); persist(); render(); renderSummary(); renderWash();
                    say('رجعت النسخة السابقة.',6000); }
          }catch(e){}
        });
      }, 600);
    }
""", '    }\n', 'SEEDFORCE branch')

# ------------------------------------- ٣ · حفظ مستقل لا يمسّ السجل الكامل
sub("var KEY='darb-campaigns-v1';", "var KEY='darb-carwash-campaign-v1';", 'KEY')
sub("var WKEY='darb-wash-plan-v1';", "var WKEY='darb-carwash-plan-v1';", 'WKEY')

# --------------------------- ٤ · الصفحات الثلاث تُرسم عند الفتح لا عند أول تعديل
sub("""  render();
  setPartners([]);""",
    """  render(); renderSummary(); renderWash();
  setPartners([]);""", 'boot render')

# ------------- ٥ · التصدير يلتقط أنماط الملف لا أنماط المضيف حول الرابط
sub('<style>', '<style id="darbcss">', 'style id')
sub("    var st=document.querySelector('style');",
    """    var st=document.getElementById('darbcss');
    if(!st){                       /* احتياط: ابحث عن الورقة الحقيقية لا أول وسم */
      var all=document.querySelectorAll('style');
      for(var q=0;q<all.length;q++)
        if((all[q].textContent||'').indexOf('.kpis')>=0){ st=all[q]; break; }
      if(!st && all.length) st=all[all.length-1];
    }""", 'export stylesheet')

# ------------------------------------------ ٦ · لا يبقى أثر للحملات الأخرى
for box in ['sumTable', 'wTable', 'list']:
    s, cut = empty_div(s, box)
    print('  emptied #%-9s %7d chars' % (box, cut))
    n += 1

sub('<title>درب · إدارة الحملات التسويقية</title>',
    '<title>حملة خدمات السيارات</title>', 'title')

# اسم التنزيل يميّزه عن ملف السجل الكامل (والجذر بالإنجليزية شرط للتنزيل)
before = s.count('darb-campaigns.html')
assert before >= 5, 'export filename occurrences: %d' % before
s = s.replace('darb-campaigns.html', 'darb-carwash-campaign.html')
n += before

# الأرقام في الترويسة يكتبها الجافاسكربت؛ لا نترك أرقام التسع حملات تومض
s, k = re.subn(r'(<div class="v" id="k[A-Za-z]+">)[^<]*(</div>)', r'\1—\2', s)
n += k

open(OUT, 'w', encoding='utf-8').write(s)

# ------------------------------------------------------- نسخة الرابط
art = s
for frag in ['<!doctype html>\n', '<html lang="ar" dir="rtl">\n', '<head>\n',
             '<meta charset="utf-8">\n',
             '<meta name="viewport" content="width=device-width, initial-scale=1">\n',
             '</head>\n', '<body>\n', '\n</body>', '\n</html>']:
    assert frag in art, 'wrapper fragment missing: ' + repr(frag)
    art = art.replace(frag, '', 1)
# المضيف يوفّر html/head/body، فنضبط اللغة والاتجاه من داخل الصفحة
art = art.replace('<style id="darbcss">',
                  '<script>document.documentElement.lang="ar";'
                  'document.documentElement.dir="rtl";</script>\n<style id="darbcss">', 1)
open(ART, 'w', encoding='utf-8').write(art)

print('\npatches: %d' % n)
print('campaign kept: %s — %s' % (keep[0]['code'], keep[0]['name']))
print('stations: %s | partners: %d' % (keep[0]['stations'], len(keep[0]['partners'])))
print('page %d KB   artifact %d KB   (was %d KB)'
      % (len(s) // 1024, len(art) // 1024, len(open(SRC, encoding='utf-8').read()) // 1024))
