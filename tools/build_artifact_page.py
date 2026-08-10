# -*- coding: utf-8 -*-
"""يحوّل التقرير إلى صفحة صالحة للنشر كرابط حيّ (Artifact).

منصّة النشر تضع المحتوى داخل هيكل جاهز `<!doctype html><head></head><body>`،
فلا يصحّ أن يحمل الملف وسوم `html/head/body` الخاصة به. هذا السكربت يفكّ
المستند إلى: أنماطه ثم محتواه، ويضيف سطرًا يعيد ضبط اتجاه الصفحة ولغتها
ومعرّف الوثيقة على العنصر الجذر بعد التحميل.

لا يمسّ التصميم ولا المحتوى — التغيير كله في الغلاف.

    python3 tools/build_artifact_page.py [ملف-المصدر] [ملف-المخرَج]
"""
import re, os, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(BASE, "darb-five-stations-analysis.html")
OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(BASE, "dist", "darb-report-live.html")
os.makedirs(os.path.dirname(OUT), exist_ok=True)

doc = open(SRC, encoding="utf-8").read()

head = re.search(r"<head[^>]*>(.*?)</head>", doc, re.S).group(1)
body = re.search(r"<body[^>]*>(.*?)</body>", doc, re.S).group(1)

#  ما لا مكان له داخل <body>: العنوان والوسوم الوصفية — المنصّة تتكفّل بهما
head = re.sub(r"<title>.*?</title>", "", head, flags=re.S)
head = re.sub(r"<meta[^>]*>", "", head)

BOOT = """<script>
/* ‏الصفحة تُحقن داخل هيكل المنصّة، فنعيد للعنصر الجذر لغته واتجاهه ومعرّفه */
(function(){
  var r=document.documentElement;
  r.setAttribute('lang','ar'); r.setAttribute('dir','rtl');
  if(!r.dataset.docid)r.dataset.docid='darb-5st-live';
})();
</script>
<style>
/* ‏تصميم التقرير أحادي السمة (هوية درب)، فنثبّت الأرضية والحقول على الفاتح
   حتى لا يستعير شيء منها سمة المستعرض الداكنة */
:root{color-scheme:light}
html,body{background:#F7F4EF}
</style>
"""

#  التنزيل داخل صفحة منشورة يمرّ عبر قدرة المنصّة لا عبر رابط Blob
DOWNLOAD_SHIM = """
<script>
/* ‏زر «تنزيل نسخة HTML» في الصفحة المنشورة: رابط Blob لا يعمل داخل إطار
   المنصّة، فنعترض الضغطة قبل معالجها الأصلي ونستعمل قدرة التنزيل. */
(function(){
  document.addEventListener('click',function(e){
    var b=e.target.closest&&e.target.closest('#edSave');
    if(!b)return;
    var dl=window.claude&&window.claude.downloads;
    if(!dl||!dl.save)return;                 /* خارج المنصّة: يعمل الأصلي */
    e.preventDefault(); e.stopImmediatePropagation();
    var d=document.documentElement.cloneNode(true);
    ['#edbar','#bdbar','#planmodal'].forEach(function(sel){
      var n=d.querySelector(sel); if(n)n.remove();
    });
    d.querySelectorAll('[data-builder]').forEach(function(n){n.remove();});
    d.querySelectorAll('[data-bddrag]').forEach(function(n){n.removeAttribute('data-bddrag');});
    d.querySelectorAll('[contenteditable]').forEach(function(n){n.removeAttribute('contenteditable');});
    d.classList.remove('editing');
    d.dataset.docid='darb-5st-'+Math.random().toString(36).slice(2,10);
    var stat=document.getElementById('edStat');
    var say=function(t){ if(stat)stat.textContent=t; };
    var html='<!DOCTYPE html>\\n'+d.outerHTML;
    say('…يجري التنزيل');
    /* ‏امتداد html من المجموعة الموسّعة وقد لا يكون مفعّلًا في هذا العرض،
       فنعيد المحاولة باسم نصّي يُعاد تسميته يدويًا بدل أن يفشل صامتًا */
    dl.save({filename:'darb-five-stations-analysis.html',data:html})
      .then(function(){ say('✓ تم التنزيل'); })
      .catch(function(err){
        var c=err&&err.code;
        if(c==='rejected_extension'||c==='extension_not_enabled'){
          dl.save({filename:'darb-five-stations-analysis.html.txt',data:html})
            .then(function(){ say('✓ نُزِّل باسم .txt — غيّر الامتداد إلى .html'); })
            .catch(function(e2){ say(e2&&e2.code==='declined'?'أُلغي التنزيل':'تعذّر التنزيل'); });
          return;
        }
        say(c==='declined'?'أُلغي التنزيل'
            :c==='too_large'?'الملف أكبر من الحد المسموح'
            :c==='rate_limited'?'أعد المحاولة بعد لحظة'
            :'تعذّر التنزيل — نزّل الملف من المحادثة');
      });
  },true);
})();
</script>
"""

open(OUT, "w", encoding="utf-8").write(BOOT + head + body + DOWNLOAD_SHIM)
print("تم ·", OUT, "·", round(os.path.getsize(OUT) / 1024), "KB")
