#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مولّد قوالب البريد الداخلي — محطات درب
=====================================

يبني القالب الرئيسي وكل القوالب الجاهزة من مصدر واحد، حتى تبقى الهوية
والبنية متطابقة في كل رسالة. عدّل هنا فقط، ثم شغّل:

    python3 build-templates.py

المخرجات: ملفات HTML بجانب هذا الملف، جاهزة للنسخ في نظام البريد.
"""

import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────── ألوان الهوية ───────────────────────────
AMBER, AMBER_DARK, AMBER_SOFT = "#E8760C", "#C85E05", "#FBE3C6"
BROWN, BROWN_LIGHT = "#2E1D12", "#4A3020"
PAPER, PAPER_2 = "#FBF6EF", "#F3E9DC"
INK, INK_2, INK_3 = "#2A1D14", "#6E5A48", "#9A8674"
LINE = "#E4D6C4"
GREEN, GOLD = "#1B7A4B", "#C79A3A"

# شريط النوع: (خلفية، لون العنوان، لون التصنيف)
BANDS = {
    "تقدير":   (AMBER,       "#FFFFFF", "#FFE9CE"),
    "أخبار":   (GREEN,       "#FFFFFF", "#BFE3CE"),
    "قيادة":   (BROWN_LIGHT, "#F7EEDF", "#D9B45B"),
    "مناسبة":  (GOLD,        "#2A1D14", "#6B4E14"),
}

FONT = "Tahoma,'Segoe UI',Arial,sans-serif"
FONT_LATIN = "Tahoma,Arial,sans-serif"


# ─────────────────────────── لبنات البناء ───────────────────────────
MASTER_NOTES = """
  كيف تستخدم هذا القالب:
  1) انسخ الملف كاملًا والصقه في محرر HTML داخل نظام البريد.
  2) استبدل كل حقل بين {{ }} بالقيمة الصحيحة — راجع جدول الحقول في الدليل.
  3) شريط النوع له أربعة ألوان بحسب الرسالة:
       تقدير  #E8760C  ·  أخبار وحملات  #1B7A4B
       قيادة  #4A3020  ·  مناسبة شخصية  #C79A3A  (نص داكن على الذهبي)
     غيّر لون خلية الشريط ولون نصها فقط، ولا تغيّر شيئًا آخر.
  4) صندوق الإبراز والزر اختياريان — احذف الكتلة كاملة إن لم تحتجها.
     الزر عنصر واحد لا أكثر في الرسالة الواحدة.
  5) اختبر على Outlook وGmail والجوال قبل الإرسال.

  ألوان الهوية:
  كهرماني #E8760C · كهرماني غامق #C85E05 · كهرماني فاتح #FBE3C6
  بُني #2E1D12 · بُني فاتح #4A3020 · ورقي #FBF6EF · حبري #2A1D14
  أخضر #1B7A4B · ذهبي #C79A3A
"""


def head(subject, preheader_note, notes=""):
    return f"""<!doctype html>
<html lang="ar" dir="rtl" xmlns="http://www.w3.org/1999/xhtml" xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="X-UA-Compatible" content="IE=edge">
<meta name="x-apple-disable-message-reformatting">
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
<title>{subject}</title>

<!--
  ═══════════════════════════════════════════════════════════════════
  محطات درب · البريد الداخلي · الإصدار 1.0
  مولّد من build-templates.py — لا تعدّل هذا الملف يدويًا، عدّل المولّد.

  الموضوع المقترح : {subject}
  نص المعاينة     : {preheader_note}
  ═══════════════════════════════════════════════════════════════════
{notes}-->


<!--[if mso]>
<noscript><xml><o:OfficeDocumentSettings>
  <o:AllowPNG/><o:PixelsPerInch>96</o:PixelsPerInch>
</o:OfficeDocumentSettings></xml></noscript>
<![endif]-->

<style type="text/css">
  body,table,td,a{{-webkit-text-size-adjust:100%;-ms-text-size-adjust:100%}}
  table,td{{mso-table-lspace:0pt;mso-table-rspace:0pt}}
  img{{-ms-interpolation-mode:bicubic;border:0;line-height:100%;outline:none;text-decoration:none}}
  table{{border-collapse:collapse!important}}
  body{{margin:0!important;padding:0!important;width:100%!important;height:100%!important}}
  a{{color:{AMBER_DARK}}}

  @media only screen and (max-width:620px){{
    .wrapper{{width:100%!important}}
    .px{{padding-left:20px!important;padding-right:20px!important}}
    .band-title{{font-size:21px!important;line-height:1.35!important}}
    .body-text{{font-size:16px!important;line-height:1.85!important}}
    .btn a{{display:block!important;text-align:center!important}}
  }}

  @media (prefers-color-scheme:dark){{
    .dm-bg{{background-color:#17100A!important}}
    .dm-card{{background-color:#211710!important}}
    .dm-text{{color:#F4E9DB!important}}
    .dm-muted{{color:#C7B49E!important}}
    .dm-faint{{color:#9A836C!important}}
    .dm-line{{border-color:#33241A!important}}
    .dm-box{{background-color:#3A2614!important}}
    .dm-foot{{background-color:#1E150D!important}}
  }}
  [data-ogsc] .dm-bg{{background-color:#17100A!important}}
  [data-ogsc] .dm-card{{background-color:#211710!important}}
  [data-ogsc] .dm-text{{color:#F4E9DB!important}}
  [data-ogsc] .dm-muted{{color:#C7B49E!important}}
  [data-ogsc] .dm-box{{background-color:#3A2614!important}}
</style>
</head>

<body dir="rtl" class="dm-bg" style="margin:0;padding:0;background-color:{PAPER};">
"""


def preheader(text):
    zwsp = "&#8203;" * 25
    return f"""
<!-- نص المعاينة — يظهر في صندوق الوارد فقط -->
<div style="display:none;font-size:1px;color:{PAPER};line-height:1px;max-height:0;max-width:0;opacity:0;overflow:hidden;mso-hide:all;">
  {text}
  {zwsp}
</div>

<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" class="dm-bg" style="background-color:{PAPER};">
  <tr>
    <td align="center" style="padding:24px 12px;">
      <table role="presentation" class="wrapper" width="600" cellpadding="0" cellspacing="0" border="0" style="width:600px;max-width:600px;">
"""


def masthead(unit):
    return f"""
        <!-- ١ · الترويسة -->
        <tr>
          <td align="right" bgcolor="{BROWN}" style="background-color:{BROWN};padding:20px 28px;border-radius:14px 14px 0 0;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" dir="rtl">
              <tr>
                <td align="right" width="52" style="width:52px;vertical-align:middle;">
                  <table role="presentation" cellpadding="0" cellspacing="0" border="0">
                    <tr>
                      <td align="center" bgcolor="{AMBER}" width="40" height="40" style="width:40px;height:40px;background-color:{AMBER};border-radius:11px;font-family:{FONT_LATIN};font-size:17px;font-weight:bold;color:#FFFFFF;line-height:40px;text-align:center;">د</td>
                    </tr>
                  </table>
                </td>
                <td align="right" style="vertical-align:middle;padding-right:12px;">
                  <div style="font-family:{FONT};font-size:17px;font-weight:bold;color:#F7EEDF;line-height:1.3;">محطات درب</div>
                  <div style="font-family:{FONT_LATIN};font-size:9.5px;letter-spacing:2.4px;color:#C9A876;line-height:1.5;padding-top:2px;">DARB STATIONS</div>
                </td>
                <td align="left" style="vertical-align:middle;">
                  <div style="font-family:{FONT};font-size:11px;color:#B99A76;line-height:1.5;">{unit}</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>
"""


def band(kind, label, headline):
    bg, fg, label_fg = BANDS[kind]
    return f"""
        <!-- ٢ · شريط النوع ({kind}) -->
        <tr>
          <td align="right" bgcolor="{bg}" style="background-color:{bg};padding:22px 28px;">
            <div style="font-family:{FONT_LATIN};font-size:10.5px;letter-spacing:2.6px;font-weight:bold;color:{label_fg};line-height:1.6;">{label}</div>
            <div class="band-title" style="font-family:{FONT};font-size:25px;font-weight:bold;color:{fg};line-height:1.4;padding-top:5px;">{headline}</div>
          </td>
        </tr>
"""


def _open_body(pad_top=30):
    return f"""
        <!-- ٣ · المتن -->
        <tr>
          <td align="right" bgcolor="#FFFFFF" class="dm-card px" style="background-color:#FFFFFF;padding:{pad_top}px 28px 8px 28px;">
"""


_CLOSE_BODY = """
          </td>
        </tr>
"""


def para(text, muted=False):
    if muted:
        return (f'            <p class="body-text dm-muted" style="margin:0 0 16px 0;font-family:{FONT};'
                f'font-size:15.5px;line-height:1.85;color:{INK_2};">{text}</p>\n')
    return (f'            <p class="body-text dm-text" style="margin:0 0 16px 0;font-family:{FONT};'
            f'font-size:16px;line-height:1.85;color:{INK};">{text}</p>\n')


def bullets(items):
    rows = ""
    for it in items:
        rows += f"""              <tr>
                <td align="right" width="16" style="width:16px;vertical-align:top;font-family:{FONT_LATIN};font-size:16px;line-height:1.85;color:{AMBER};">•</td>
                <td align="right" class="dm-text" style="padding-right:8px;padding-bottom:6px;font-family:{FONT};font-size:15.5px;line-height:1.8;color:{INK};">{it}</td>
              </tr>
"""
    return f"""            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" dir="rtl" style="margin-bottom:14px;">
{rows}            </table>
"""


def box(label, content):
    return f"""
        <!-- ٤ · صندوق الإبراز -->
        <tr>
          <td align="right" bgcolor="#FFFFFF" class="dm-card px" style="background-color:#FFFFFF;padding:0 28px 8px 28px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" dir="rtl">
              <tr>
                <td width="4" bgcolor="{AMBER}" style="width:4px;background-color:{AMBER};font-size:0;line-height:0;">&nbsp;</td>
                <td align="right" bgcolor="{AMBER_SOFT}" class="dm-box" style="background-color:{AMBER_SOFT};padding:16px 18px;">
                  <div style="font-family:{FONT_LATIN};font-size:10.5px;letter-spacing:2px;font-weight:bold;color:{AMBER_DARK};line-height:1.6;">{label}</div>
                  <div class="dm-text" style="font-family:{FONT};font-size:15.5px;line-height:1.8;color:{INK};padding-top:7px;">{content}</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>
"""


def button(url, label):
    return f"""
        <!-- ٥ · الزر — عنصر واحد فقط -->
        <tr>
          <td align="right" bgcolor="#FFFFFF" class="dm-card px" style="background-color:#FFFFFF;padding:22px 28px 8px 28px;">
            <table role="presentation" cellpadding="0" cellspacing="0" border="0" class="btn" dir="rtl">
              <tr>
                <td align="center" bgcolor="{AMBER}" style="background-color:{AMBER};border-radius:100px;">
                  <!--[if mso]>
                  <v:roundrect xmlns:v="urn:schemas-microsoft-com:vml" xmlns:w="urn:schemas-microsoft-com:office:word"
                    href="{url}" style="height:46px;v-text-anchor:middle;width:230px;" arcsize="50%" stroke="f" fillcolor="{AMBER}">
                    <w:anchorlock/>
                    <center style="color:#FFFFFF;font-family:{FONT_LATIN};font-size:15px;font-weight:bold;">{label}</center>
                  </v:roundrect>
                  <![endif]-->
                  <!--[if !mso]><!-- -->
                  <a href="{url}" target="_blank" rel="noopener"
                     style="display:inline-block;padding:14px 34px;font-family:{FONT};font-size:15px;font-weight:bold;color:#FFFFFF;text-decoration:none;border-radius:100px;background-color:{AMBER};">{label}</a>
                  <!--<![endif]-->
                </td>
              </tr>
            </table>
          </td>
        </tr>
"""


def signature(name, title):
    return f"""
        <!-- ٦ · التوقيع -->
        <tr>
          <td align="right" bgcolor="#FFFFFF" class="dm-card px" style="background-color:#FFFFFF;padding:24px 28px 28px 28px;">
            <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
              <tr><td class="dm-line" style="border-top:1px solid {LINE};font-size:0;line-height:0;padding-top:4px;">&nbsp;</td></tr>
            </table>
            <p class="dm-text" style="margin:16px 0 0 0;font-family:{FONT};font-size:15px;line-height:1.8;color:{INK};font-weight:bold;">{name}</p>
            <p class="dm-muted" style="margin:2px 0 0 0;font-family:{FONT};font-size:13.5px;line-height:1.7;color:{INK_2};">{title}</p>
          </td>
        </tr>
"""


FOOTER = f"""
        <!-- ٧ · التذييل -->
        <tr>
          <td align="center" bgcolor="{PAPER_2}" class="dm-foot" style="background-color:{PAPER_2};padding:20px 28px;border-radius:0 0 14px 14px;">
            <div style="font-family:{FONT};font-size:12.5px;font-weight:bold;color:{INK};line-height:1.7;">محطات درب · الاختيار الأول</div>
            <div class="dm-muted" style="font-family:{FONT};font-size:11.5px;color:{INK_2};line-height:1.9;padding-top:5px;">
              <a href="mailto:DarbHR@Darbstations.com.sa" style="color:{AMBER_DARK};text-decoration:none;">DarbHR@Darbstations.com.sa</a>
              &nbsp;·&nbsp; 920 005804
            </div>
            <div class="dm-faint" style="font-family:{FONT};font-size:10.5px;color:{INK_3};line-height:1.8;padding-top:10px;">
              وصلَتك هذي الرسالة لأنك أحد منسوبي محطات درب.<br>
              رسالة داخلية — غير مخصصة للتداول خارج الشركة.
            </div>
          </td>
        </tr>
"""

TAIL = """
      </table>
    </td>
  </tr>
</table>

</body>
</html>
"""


def render(cfg):
    out = head(cfg["subject"], cfg["preheader"], cfg.get("notes", ""))
    out += preheader(cfg["preheader"])
    out += masthead(cfg["unit"])
    out += band(cfg["band"], cfg["band_label"], cfg["headline"])
    out += _open_body()
    for blk in cfg["body"]:
        if blk[0] == "p":
            out += para(blk[1])
        elif blk[0] == "m":
            out += para(blk[1], muted=True)
        elif blk[0] == "ul":
            out += bullets(blk[1])
    out += _CLOSE_BODY
    if cfg.get("box"):
        out += box(cfg["box"][0], cfg["box"][1])
    if cfg.get("cta"):
        out += button(cfg["cta"][0], cfg["cta"][1])
    out += signature(cfg["sign"][0], cfg["sign"][1])
    out += FOOTER
    out += TAIL
    return out


# ─────────────────────────── محتوى القوالب ───────────────────────────
HR = ("إدارة الموارد البشرية", "محطات درب")
MK = ("إدارة التسويق والاتصال المؤسسي", "محطات درب")

TEMPLATES = [

    # ── القالب الرئيسي: كل الحقول مفتوحة ──
    ("00-master-template.html", {
        "subject": "{{SUBJECT}}",
        "preheader": "{{PREHEADER}}",
        "notes": MASTER_NOTES,
        "unit": "{{SENDER_UNIT}}",
        "band": "تقدير",
        "band_label": "{{BAND_LABEL}}",
        "headline": "{{HEADLINE}}",
        "body": [
            ("p", "{{FIRST_NAME}}،"),
            ("p", "{{PARAGRAPH_1}}"),
            ("m", "{{PARAGRAPH_2}}"),
        ],
        "box": ("{{BOX_LABEL}}", "{{BOX_CONTENT}}"),
        "cta": ("{{CTA_URL}}", "{{CTA_LABEL}}"),
        "sign": ("{{SIGNATURE_NAME}}", "{{SIGNATURE_TITLE}} — محطات درب"),
    }),

    # ── T-01 · ترحيب بموظف جديد ──
    ("01-welcome.html", {
        "subject": "أهلًا {{FIRST_NAME}} — أول يوم لك في درب",
        "preheader": "محطتك، مديرك، ومن تتواصل معه لأي شيء.",
        "unit": "الموارد البشرية",
        "band": "قيادة",
        "band_label": "انضمام جديد",
        "headline": "أهلًا بك في درب",
        "body": [
            ("p", "{{FIRST_NAME}}،"),
            ("p", "من اليوم أنت جزء من درب، وتحديدًا في <b>{{STATION}}</b> مع فريق {{MANAGER_NAME}}."),
            ("p", "قبل أي شيء: نحن لا نستقبلك كموظف رقم كذا. أنت من هنا فصاعدًا الوجه الذي يراه عميلنا. ما تقوله وتفعله في دقيقتين عند المضخة هو انطباع الناس عن الشركة كلها — وهذي مسؤولية نثق أنك أهل لها."),
            ("m", "خلال أسبوعين بنسألك عن انطباعك الأول، وبنسمع منك بصدق."),
        ],
        "box": ("ثلاثة أشياء تحتاجها اليوم", "مديرك المباشر: {{MANAGER_NAME}} — {{MANAGER_PHONE}}<br>ميثاق سفير درب: اقرأه ووقّعه مع مديرك<br>لأي استفسار: DarbHR@Darbstations.com.sa"),
        "cta": ("{{CTA_URL}}", "اقرأ دليل سفير درب"),
        "sign": HR,
    }),

    # ── T-02 · شكر فوري ──
    ("02-recognition.html", {
        "subject": "شكرًا {{FIRST_NAME}} — موقفك {{DAY}} في {{STATION}}",
        "preheader": "وصلَنا الخبر، ووصل للإدارة أيضًا.",
        "unit": "الموارد البشرية",
        "band": "تقدير",
        "band_label": "تقدير",
        "headline": "شكرًا {{FIRST_NAME}}",
        "body": [
            ("p", "{{FIRST_NAME}}،"),
            ("p", "وصلَنا ما حصل {{DAY}} في <b>{{STATION}}</b>."),
            ("p", "ما كان مطلوبًا منك نظاميًا، وسويته. هذا بالضبط الفرق بين موظف يؤدي مهمة وسفير يمثّل شركة."),
            ("m", "الخبر وصل لـ{{MANAGER_NAME}} وللإدارة، وانضاف لملفك المهني. شكرًا، ونعتز فيك."),
        ],
        "box": ("ما الذي حدث", "{{INCIDENT_ONE_LINE}}"),
        "cta": None,
        "sign": HR,
    }),

    # ── T-03 · نجم الشهر ──
    ("03-star-of-the-month.html", {
        "subject": "نجم درب لشهر {{MONTH}}: {{STAR_NAME}}",
        "preheader": "السبب كامل داخل الرسالة — ويستاهل.",
        "unit": "الموارد البشرية",
        "band": "تقدير",
        "band_label": "نجم الشهر",
        "headline": "نجم درب — {{MONTH}}",
        "body": [
            ("p", "زملاء درب،"),
            ("p", "نجم هذا الشهر: <b>{{STAR_NAME}}</b> — {{STAR_ROLE}}، {{STATION}}."),
            ("p", "اختير لسبب محدد لا لمجاملة:"),
            ("ul", ["{{REASON_1}}", "{{REASON_2}}", "{{REASON_3}}"]),
            ("p", "{{STAR_FIRST_NAME}}، مبروك. التكريم: {{REWARD}}، وصورتك بتكون على لوحة الشرف في {{STATION}} هذا الشهر."),
            ("m", "ولبقية الزملاء: الترشيح مفتوح دائمًا. إذا شفت زميلًا يستاهل، رشّحه عبر النموذج — دقيقة وحدة تكفي."),
        ],
        "box": None,
        "cta": ("{{CTA_URL}}", "رشّح زميلًا للشهر القادم"),
        "sign": HR,
    }),

    # ── T-04 · ذكرى الانضمام ──
    ("04-work-anniversary.html", {
        "subject": "{{YEARS}} سنوات معنا، {{FIRST_NAME}}",
        "preheader": "شكرًا على كل يوم منها.",
        "unit": "الموارد البشرية",
        "band": "مناسبة",
        "band_label": "ذكرى انضمام",
        "headline": "{{YEARS}} سنوات معنا",
        "body": [
            ("p", "{{FIRST_NAME}}،"),
            ("p", "في مثل هذا اليوم قبل {{YEARS}} سنوات باشرت العمل معنا في <b>{{FIRST_STATION}}</b>."),
            ("p", "الأرقام تختصر، لكن اللي ما تختصره هو أن الفريق تعوّد عليك، وأن عملاءنا في {{STATION}} صاروا يعرفونك بالاسم."),
            ("m", "شكرًا على {{YEARS}} سنوات، ونتطلع للقادم."),
        ],
        "box": ("منذ ذلك اليوم", "خدمت في {{STATIONS_COUNT}} من محطاتنا<br>حضرت {{TRAINING_COUNT}} برنامجًا تدريبيًا<br>وصلَك {{RECOGNITION_COUNT}} تقديرًا موثقًا"),
        "cta": None,
        "sign": HR,
    }),

    # ── T-05 · دعوة حملة محتوى ──
    ("05-advocacy-campaign.html", {
        "subject": "شارِك يومك في درب — المشاركة اختيارية",
        "preheader": "صورة أو سطرين، وأنت صاحب القرار.",
        "unit": "التسويق والاتصال",
        "band": "أخبار",
        "band_label": "حملة داخلية",
        "headline": "شارِك يومك في درب",
        "body": [
            ("p", "{{FIRST_NAME}}،"),
            ("p", "بنطلق حملة «{{CAMPAIGN_NAME}}» يوم {{DATE}}، وحبينا نبدأ منكم أنتم."),
            ("p", "الفكرة بسيطة: صورة أو سطرين عن يوم عملك في {{STATION}} — لحظة خدمة، زاوية تحبها في المحطة، أو موقف تتذكره."),
            ("p", "طريقتان للمشاركة: أرسلها على {{SUBMIT_EMAIL}}، أو انشرها بحسابك مع وسم <b>#درب_الاختيار_الأول</b>."),
            ("m", "أفضل المشاركات بننشرها على حسابات درب الرسمية باسم صاحبها، وبنكرّم ثلاثة منها."),
        ],
        "box": ("قبل ما تشارك — ثلاث نقاط", "المشاركة اختيارية تمامًا وما لها أي علاقة بتقييمك الوظيفي<br>لا تصوّر عميلًا أو لوحة سيارة دون إذنه<br>ابتعد عن مناطق التعبئة والسلامة أثناء التصوير"),
        "cta": ("{{CTA_URL}}", "أرسل مشاركتك"),
        "sign": MK,
    }),

    # ── T-06 · النشرة الداخلية ──
    ("06-internal-newsletter.html", {
        "subject": "من الطريق · {{MONTH}}: {{HEADLINE_NEWS}}",
        "preheader": "نجم الشهر، ما تغيّر، وما ينتظرنا.",
        "unit": "الموارد البشرية",
        "band": "أخبار",
        "band_label": "نشرة داخلية",
        "headline": "من الطريق · {{MONTH}}",
        "body": [
            ("p", "زملاء درب،"),
            ("p", "هذي أخبار {{MONTH}} في خمس دقائق قراءة أو أقل."),
            ("p", "<b>نجم الشهر</b><br>{{STAR_NAME}} — {{STATION}}. السبب: {{STAR_REASON}}"),
            ("p", "<b>ما أنجزناه</b>"),
            ("ul", ["{{ACHIEVEMENT_1}}", "{{ACHIEVEMENT_2}}"]),
            ("p", "<b>وجوه جديدة</b><br>انضم لنا هذا الشهر: {{NEW_JOINERS}}"),
            ("m", "<b>سؤال الشهر:</b> {{QUESTION}} — ردّ على هذي الرسالة، والإجابات تُنشر في العدد القادم بلا أسماء إذا رغبت."),
        ],
        "box": ("ما نحتاجه منكم هذا الشهر", "{{ASK_OF_THE_MONTH}}"),
        "cta": ("{{CTA_URL}}", "شارك خبرًا من محطتك"),
        "sign": HR,
    }),

    # ── T-07 · دعوة تدريب ──
    ("07-training-invitation.html", {
        "subject": "حجزنا لك مقعدًا: {{COURSE_NAME}}",
        "preheader": "{{DURATION}} · {{DATE}} · {{LOCATION}}",
        "unit": "التدريب والتطوير",
        "band": "قيادة",
        "band_label": "تدريب وتطوير",
        "headline": "حجزنا لك مقعدًا",
        "body": [
            ("p", "{{FIRST_NAME}}،"),
            ("p", "حجزنا لك مقعدًا في «<b>{{COURSE_NAME}}</b>»."),
            ("p", "ليش أنت تحديدًا؟ {{WHY_YOU}}"),
            ("p", "بعد الورشة بتقدر: {{OUTCOME_1}}، و{{OUTCOME_2}}."),
            ("m", "الموعد ما يناسبك؟ ردّ على هذي الرسالة وبندوّر لك موعدًا ثانيًا — بدون أي إجراء إداري."),
        ],
        "box": ("تفاصيل الورشة", "المدة: {{DURATION}}<br>الموعد: {{DATE}} — {{TIME}}<br>المكان: {{LOCATION}}<br>المدرّب: {{TRAINER}}"),
        "cta": ("{{CTA_URL}}", "أكّد حضورك"),
        "sign": ("إدارة التدريب والتطوير", "محطات درب"),
    }),

    # ── T-08 · تهنئة مناسبة ──
    ("08-occasion-greeting.html", {
        "subject": "{{OCCASION}} — من درب إلى بيتك",
        "preheader": "وشكرًا لمن يقف في المحطات هذي الأيام.",
        "unit": "مكتب الرئيس التنفيذي",
        "band": "قيادة",
        "band_label": "تهنئة",
        "headline": "{{OCCASION}}",
        "body": [
            ("p", "زملاء درب،"),
            ("p", "{{OCCASION_GREETING}}"),
            ("p", "وفي هذي المناسبة تحديدًا نتذكر أن الطرق ما تهدأ حين يرتاح الناس — بل تزدحم. وأن هناك من زملائنا من يقف في ورديته اليوم بينما غيره مع أهله."),
            ("p", "لكم أنتم تحديدًا: شكرًا. المحطة المفتوحة في يوم مثل هذا هي أصدق ما تقوله الشركة عن نفسها."),
            ("m", "كل عام وأنتم وعوائلكم بخير."),
        ],
        "box": None,
        "cta": None,
        "sign": ("{{CEO_NAME}}", "الرئيس التنفيذي — محطات درب"),
    }),
]


def main():
    written = []
    for filename, cfg in TEMPLATES:
        html = render(cfg)
        path = os.path.join(HERE, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        # فحص سريع: كل وسم مفتوح له إغلاق في الجداول الرئيسية
        assert html.count("<table") == html.count("</table>"), filename
        assert html.count("<tr") == html.count("</tr>"), filename
        fields = sorted(set(re.findall(r"\{\{[A-Z_0-9]+\}\}", html)))
        written.append((filename, len(html), fields))

    print("تم توليد القوالب:\n")
    for name, size, fields in written:
        print(f"  ✓ {name:32s} {size:6d} حرف · {len(fields):2d} حقل دمج")
    print(f"\nالمجموع: {len(written)} ملفًا في {HERE}")


if __name__ == "__main__":
    main()
