const {
  Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType,
  Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle,
  LevelFormat, PageNumber, Footer, Header, PageBreak,
} = require('docx');
const fs = require('fs');

const FONT = 'Arial';
const NAVY = '1F3A5F', GOLD = 'B58B3C', GREY = '5A5A5A';
const HEADFILL = '1F3A5F', ROWFILL = 'F2EFE9', WARNFILL = 'FBEEE6';

/* ‏— كل فقرة ثنائية الاتجاه وكل مقطع نصّي RTL: بدونهما ينقلب ترتيب
     الأرقام والنقاط في نهاية السطر داخل Word — */
function run(t, o = {}) {
  return new TextRun({
    text: String(t), rightToLeft: true, font: FONT,
    size: o.size || 22, bold: !!o.bold, italics: !!o.italics, color: o.color,
  });
}
function P(t, o = {}) {
  return new Paragraph({
    bidirectional: true,
    alignment: o.align || AlignmentType.BOTH,
    spacing: { before: o.before || 0, after: o.after === undefined ? 120 : o.after, line: o.line || 300 },
    children: Array.isArray(t) ? t : [run(t, o)],
  });
}
function H1(t) {
  return new Paragraph({
    bidirectional: true, heading: HeadingLevel.HEADING_1, alignment: AlignmentType.RIGHT,
    spacing: { before: 340, after: 160 },
    border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: GOLD, space: 6 } },
    children: [run(t, { bold: true, size: 30, color: NAVY })],
  });
}
function H2(t) {
  return new Paragraph({
    bidirectional: true, heading: HeadingLevel.HEADING_2, alignment: AlignmentType.RIGHT,
    spacing: { before: 240, after: 100 },
    children: [run(t, { bold: true, size: 25, color: NAVY })],
  });
}
function BUL(t) {
  return new Paragraph({
    bidirectional: true, alignment: AlignmentType.BOTH,
    numbering: { reference: 'bul', level: 0 },
    spacing: { after: 80, line: 300 },
    children: Array.isArray(t) ? t : [run(t)],
  });
}
function cell(children, o = {}) {
  return new TableCell({
    width: { size: o.w, type: WidthType.DXA },
    shading: o.fill ? { type: ShadingType.CLEAR, fill: o.fill, color: 'auto' } : undefined,
    margins: { top: 70, bottom: 70, left: 100, right: 100 },
    verticalAlign: 'center',
    children,
  });
}
function tcell(text, o = {}) {
  return cell([new Paragraph({
    bidirectional: true, alignment: o.align || AlignmentType.RIGHT,
    spacing: { after: 0, line: 260 },
    children: [run(text, { bold: o.bold, size: o.size || 21, color: o.color })],
  })], o);
}
function table(widths, rows) {
  return new Table({
    visuallyRightToLeft: true,
    columnWidths: widths,
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    borders: {
      top: { style: BorderStyle.SINGLE, size: 4, color: 'C9C2B6' },
      bottom: { style: BorderStyle.SINGLE, size: 4, color: 'C9C2B6' },
      left: { style: BorderStyle.SINGLE, size: 4, color: 'C9C2B6' },
      right: { style: BorderStyle.SINGLE, size: 4, color: 'C9C2B6' },
      insideHorizontal: { style: BorderStyle.SINGLE, size: 4, color: 'D8D2C7' },
      insideVertical: { style: BorderStyle.SINGLE, size: 4, color: 'D8D2C7' },
    },
    rows,
  });
}
function headRow(labels, widths) {
  return new TableRow({
    tableHeader: true,
    children: labels.map((l, i) => tcell(l, {
      w: widths[i], fill: HEADFILL, bold: true, color: 'FFFFFF', align: AlignmentType.CENTER,
    })),
  });
}
function row(cells, widths, o = {}) {
  return new TableRow({
    children: cells.map((c, i) => {
      const v = (typeof c === 'object' && c !== null) ? c : { t: c };
      return tcell(v.t, {
        w: widths[i], fill: v.fill || o.fill, bold: v.bold || o.bold,
        color: v.color, align: v.align || o.align,
      });
    }),
  });
}
function spacer(h) { return new Paragraph({ bidirectional: true, spacing: { after: h || 120 }, children: [] }); }

const body = [];

/* الترويسة */
body.push(new Paragraph({
  bidirectional: true, alignment: AlignmentType.CENTER, spacing: { after: 40 },
  children: [run('شركة درب لمحطات الوقود', { bold: true, size: 24, color: GOLD })],
}));
body.push(new Paragraph({
  bidirectional: true, alignment: AlignmentType.CENTER, spacing: { after: 60 },
  children: [run('الوصف الوظيفي ومؤشرات الأداء', { bold: true, size: 40, color: NAVY })],
}));
body.push(new Paragraph({
  bidirectional: true, alignment: AlignmentType.CENTER, spacing: { after: 200 },
  border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: GOLD, space: 8 } },
  children: [run('أخصائي مبيعات خارجية وشراكات أساطيل — محطات مكة', { bold: true, size: 28, color: GREY })],
}));

/* ١ */
body.push(H1('١ · بطاقة الوظيفة'));
{
  const w = [2200, 7438];
  body.push(table(w, [
    row([{ t: 'المسمّى الوظيفي', bold: true, fill: ROWFILL }, 'أخصائي مبيعات خارجية وشراكات أساطيل'], w),
    row([{ t: 'الإدارة', bold: true, fill: ROWFILL }, 'إدارة التشغيل والمبيعات'], w),
    row([{ t: 'يتبع مباشرة', bold: true, fill: ROWFILL }, 'مدير التشغيل / مدير المبيعات'], w),
    row([{ t: 'نطاق العمل', bold: true, fill: ROWFILL }, 'خمس محطات في مكة المكرمة: العمرة النورية MK007 · عرفات الشوقية MK017 · المعيصم MK002 · بن درويش MK023 · عرفات الشرايع MK019'], w),
    row([{ t: 'طبيعة العمل', bold: true, fill: ROWFILL }, 'ميداني بنسبة تقارب ٧٠٪ — زيارات للمنشآت المحيطة بالمحطات، مع مكتب لإتمام التعاقدات والتوثيق'], w),
    row([{ t: 'عدد المرؤوسين', bold: true, fill: ROWFILL }, 'لا يوجد — دور فردي مساهم'], w),
    row([{ t: 'تاريخ الإصدار', bold: true, fill: ROWFILL }, 'أكتوبر ٢٠٢٦ — مبني على بيانات المنصّة للفترة يناير ← يوليو ٢٠٢٦'], w),
  ]));
}

/* ٢ */
body.push(H1('٢ · الغرض من الوظيفة'));
body.push(P('تحويل حركة المرور العابرة إلى استهلاك متعاقَد عليه ومتكرّر، عبر بناء محفظة عقود تعبئة أساطيل وشراكات مع المنشآت المحيطة بالمحطات، وتضييق الفجوة بين المبيعات المتحققة والموازنة المعتمدة في المحطات المتأخرة — مع توثيق كل نشاط بيعي داخل منصّة التحليل والخطط التشغيلية.'));

/* ٣ */
body.push(H1('٣ · سياق الدور — ما تقوله بيانات المنصّة'));
body.push(P('يُبنى هذا الوصف على الأرقام الفعلية المسجّلة في المنصّة للفترة يناير ← يوليو ٢٠٢٦، لا على وصف عام لوظيفة مبيعات. الوحدة لترات لأن المستهدفات في ملف Sales Analysis 2026 موضوعة بالّلتر:'));
{
  const w = [2050, 1720, 1620, 1620, 880, 1748];
  body.push(table(w, [
    headRow(['المحطة', 'الموازنة التراكمية (لتر)', 'المتحقق (لتر)', 'الفجوة (لتر)', 'التحقيق', 'منشآت مرصودة حولها'], w),
    row([{ t: 'المعيصم MK002', bold: true }, '11,089,866', '3,845,844', { t: '−7,244,022', color: 'B23B3B', bold: true }, { t: '٣٥٪', color: 'B23B3B', bold: true, align: AlignmentType.CENTER }, { t: '٤', align: AlignmentType.CENTER }], w, { fill: WARNFILL }),
    row([{ t: 'عرفات الشرايع MK019', bold: true }, '6,215,114', '2,163,863', { t: '−4,051,251', color: 'B23B3B', bold: true }, { t: '٣٥٪', color: 'B23B3B', bold: true, align: AlignmentType.CENTER }, { t: '٧', align: AlignmentType.CENTER }], w, { fill: WARNFILL }),
    row([{ t: 'العمرة النورية MK007', bold: true }, '29,091,868', '27,650,578', '−1,441,290', { t: '٩٥٪', align: AlignmentType.CENTER }, { t: '١٠', align: AlignmentType.CENTER }], w),
    row([{ t: 'بن درويش MK023', bold: true }, '3,504,727', '3,353,894', '−150,833', { t: '٩٦٪', align: AlignmentType.CENTER }, { t: '٩', align: AlignmentType.CENTER }], w),
    row([{ t: 'عرفات الشوقية MK017', bold: true }, '5,315,284', '5,438,441', { t: '+123,157', color: '2E7D4F' }, { t: '١٠٢٪', color: '2E7D4F', bold: true, align: AlignmentType.CENTER }, { t: '٨', align: AlignmentType.CENTER }], w),
    row([{ t: 'الإجمالي', bold: true, fill: ROWFILL }, { t: '55,216,859', bold: true, fill: ROWFILL }, { t: '42,452,620', bold: true, fill: ROWFILL }, { t: '−12,764,239', bold: true, fill: ROWFILL }, { t: '٧٧٪', bold: true, fill: ROWFILL, align: AlignmentType.CENTER }, { t: '٣٨', bold: true, fill: ROWFILL, align: AlignmentType.CENTER }], w),
  ]));
}
body.push(spacer(100));
body.push(P([run('ما يقابل الفجوة بالريال: ', { bold: true }), run('متوسط سعر البيع في يوليو ٢٠٢٦ هو ٢٫١٥ ريالًا للتر (١٢٫٧٤ مليون ريال ÷ ٥٫٩١ مليون لتر)، فالفجوة التراكمية البالغة ١٢٫٧٦ مليون لتر تعادل نحو ٢٧٫٥ مليون ريال، ومنها ٢٥٫٥ مليون ريال في MK002 و MK019 وحدهما.', {})], { after: 150 }));
body.push(H2('ثلاث حقائق تُشكّل هذا الدور'));
body.push(BUL([run('٣٨ منشأة مرصودة حول المحطات الخمس، ', {}), run('٢٦ منها لديها رقم تواصل، وكلّها ما زالت بحالة «محتمل»', { bold: true }), run(' — أي لم يبدأ التواصل مع أيّ منها. مخزون جاهز لم يُلمَس بعد.', {})]));
body.push(BUL([run('الفئة الأكبر هي مكاتب تأجير السيارات (١٦ من ٣٨)', { bold: true }), run(' — أساطيل تعبّئ يوميًا، وهي أعلى قيمة تعاقدية لكل ساعة عمل ميدانية. تليها الشركات ذات السيارات التشغيلية، ثم المدارس والنقل المدرسي.', {})]));
body.push(BUL([run('المحطتان الأضعف هما الأقل تغطية', { bold: true }), run(' — MK002 حولها ٤ منشآت مرصودة فقط مقابل فجوة ٧٫٢٤ مليون لتر. لذلك فإن نصف هذه الوظيفة توسيع قاعدة العملاء ميدانيًا، لا إغلاق قائمة جاهزة.', {})]));

/* ٤ */
body.push(H1('٤ · المسؤوليات والمهام'));
body.push(H2('٤٫١ تطوير محفظة عملاء الأساطيل — الثقل الأكبر'));
body.push(BUL('التواصل مع المنشآت المرصودة في تبويب «الشركاء الخارجيون» داخل المنصّة، بدءًا بالـ٢٦ منشأة التي لديها أرقام تواصل، وتحديث حالة كلٍّ منها أولًا بأول: محتمل ← تم التواصل ← مفاوضات ← متعاقد ← مرفوض، مع تسجيل سبب الرفض.'));
body.push(BUL('تنفيذ مسح ميداني أسبوعي لتوسيع قاعدة العملاء المحتملين، بأولوية قصوى لمحيط MK002 و MK019 لأن المرصود حولهما لا يكفي لسدّ الفجوة.'));
body.push(BUL('التفاوض على عقود التعبئة وإبرامها: خصم الكميات، الفاتورة الموحّدة الشهرية، بطاقة السائق، السقف الائتماني، ومدّة العقد وشروط تجديده.'));
body.push(BUL('متابعة العملاء المتعاقدين شهريًا للتأكد من استمرار الاستهلاك، ومعالجة أسباب التراجع قبل أن يتحوّل إلى فقدان للعميل.'));

body.push(H2('٤٫٢ الشراكات داخل المحطة'));
body.push(BUL('استقطاب شركاء يشغّلون مساحات داخل المحطة ويجلبون حركة مرور مستقلة عن الوقود، والتفاوض على شروط الشراكة ومقابلها.'));
body.push(BUL('تسجيل كل شراكة في نموذج «الشراكة» بالمنصّة كاملةً: نوع الشريك (داخلي/خارجي) · اسم الشريك · مدة الشراكة · شروطها · المستهدفات الرقمية والميدانية ومستهدفات الوصول.'));
body.push(BUL('قياس أثر كل شراكة على مبيعات المحطة بعد ٣٠ و ٩٠ يومًا، والتوصية بالتجديد أو الإنهاء بناءً على الأثر المقيس.'));

body.push(H2('٤٫٣ تنفيذ الحملات والتوزيعات ميدانيًا'));
body.push(BUL('تشغيل حملات تشجيع المبيعات الأسبوعية على أرض المحطة، وتنفيذ التوزيعات المعتمدة (مناديل · فواحات · خدمة مسح السيارات من قِبل العمال) وفق الميزانية المسجّلة لكل حملة.'));
body.push(BUL('قياس أثر الحملة على مبيعات الفترة المستهدفة من اليوم تحديدًا — لا على مبيعات الشهر ككل — باستخدام جدول الفترات في المنصّة.'));
body.push(BUL('رفع توصية بعد كل حملة: تُكرَّر · تُعدَّل · تُوقَف، مدعومة بالأرقام.'));

body.push(H2('٤٫٤ التوثيق في المنصّة — شرط أساسي لا إضافة'));
body.push(P([run('كل زيارة، وكل عقد، وكل حملة، وكل تغيّر في حالة عميل، تُسجَّل في المنصّة يوم حدوثها. ', {}), run('العمل غير المسجَّل يُعتبر غير منفَّذ لأغراض تقييم الأداء وصرف العمولة.', { bold: true, color: 'B23B3B' })], { after: 100 }));

body.push(H2('٤٫٥ التغذية الراجعة الميدانية'));
body.push(BUL('رصد أسعار المنافسين وعروضهم وخدماتهم حول كل محطة، ورفع تقرير شهري بالمستجدات.'));
body.push(BUL('رفع تقرير الصفقات الخاسرة موضّحًا سبب الرفض في كل حالة (السعر · الموقع · الخدمة · ارتباط قائم بمنافس).'));
body.push(BUL('نقل ملاحظات العملاء عن الخدمة والصيانة والنظافة إلى إدارة التشغيل.'));

/* ٥ */
body.push(new Paragraph({ bidirectional: true, children: [new PageBreak()] }));
body.push(H1('٥ · مؤشرات الأداء (KPIs)'));
body.push(P('تُقاس شهريًا وتُجمَّع ربع سنويًا. مصدر التحقق الأساسي لجميع المؤشرات هو منصّة المحطات الخمس، ما لم يُذكر خلاف ذلك.'));
{
  const w = [2200, 3700, 2100, 1638];
  body.push(table(w, [
    headRow(['المؤشر', 'طريقة القياس ومصدر التحقق', 'المستهدف الشهري', 'الوزن'], w),
    row(['قيمة الاستهلاك المتعاقَد عليه',
      'مجموع مبيعات العملاء المتعاقدين الفعلية خلال الشهر — من تقرير المبيعات، لا من قيمة العقد الموقّع',
      { t: '≥ 60,000 ر.س — نحو 27,900 لتر', bold: true }, { t: '٣٠٪', align: AlignmentType.CENTER, bold: true }], w),
    row(['عقود الأساطيل المُبرمة',
      'عدد العقود الموقّعة والمفعّلة خلال الشهر — تبويب الشركاء الخارجيين، حالة «متعاقد»',
      { t: '٣ عقود', bold: true }, { t: '٢٠٪', align: AlignmentType.CENTER, bold: true }], w, { fill: ROWFILL }),
    row(['منشآت جديدة مضافة للقاعدة',
      'عدد المنشآت المضافة بالمسح الميداني — على أن تكون ٥ منها على الأقل في محيط MK002 و MK019',
      { t: '٨ منشآت', bold: true }, { t: '١٥٪', align: AlignmentType.CENTER, bold: true }], w),
    row(['الزيارات الميدانية الموثّقة',
      'عدد الزيارات المسجّلة باسم المنشأة وتاريخ الزيارة ونتيجتها — بمعدّل ١٠ زيارات أسبوعيًا',
      { t: '٤٠ زيارة', bold: true }, { t: '١٠٪', align: AlignmentType.CENTER, bold: true }], w, { fill: ROWFILL }),
    row(['معدل التحويل',
      'عدد العقود المُبرمة ÷ عدد المنشآت التي جرى التواصل معها فعليًا خلال الشهر',
      { t: '≥ ١٥٪', bold: true }, { t: '١٠٪', align: AlignmentType.CENTER, bold: true }], w),
    row(['الشراكات داخل المحطة',
      'عدد الشراكات الجديدة المسجّلة في نموذج الشراكة بالمنصّة',
      { t: 'شراكة واحدة', bold: true }, { t: '٥٪', align: AlignmentType.CENTER, bold: true }], w, { fill: ROWFILL }),
    row(['الحملات والتوزيعات المنفَّذة والمقيسة',
      'عدد الحملات التي نُفّذت ورُفع لها قياس أثر على مبيعات الفترة المستهدفة',
      { t: 'حملتان', bold: true }, { t: '٥٪', align: AlignmentType.CENTER, bold: true }], w),
    row(['اكتمال التسجيل في المنصّة',
      'نسبة الأنشطة الموثّقة في يوم حدوثها إلى إجمالي الأنشطة المنفّذة',
      { t: '١٠٠٪', bold: true }, { t: '٥٪', align: AlignmentType.CENTER, bold: true }], w, { fill: ROWFILL }),
    row([{ t: 'الإجمالي', bold: true, fill: HEADFILL, color: 'FFFFFF' },
      { t: '', fill: HEADFILL }, { t: '', fill: HEADFILL },
      { t: '١٠٠٪', bold: true, fill: HEADFILL, color: 'FFFFFF', align: AlignmentType.CENTER }], w),
  ]));
}
body.push(spacer(180));
body.push(H2('مؤشر تراكمي سنوي'));
body.push(P([run('تغطية القاعدة المرصودة: ', { bold: true }), run('التواصل مع ١٠٠٪ من المنشآت المرصودة البالغ عددها ٣٨ منشأة خلال أول ٩٠ يومًا، وتحديث حالة كلٍّ منها في المنصّة. يُقاس مرّة واحدة عند نهاية فترة التجربة ويُعدّ شرطًا لاجتيازها.', {})]));

body.push(H2('سلّم تقييم الأداء'));
{
  const w = [2400, 3400, 3838];
  body.push(table(w, [
    headRow(['المستوى', 'نسبة تحقيق المؤشرات الموزونة', 'الأثر'], w),
    row([{ t: 'متميّز', bold: true, color: '2E7D4F' }, '١٢٠٪ فأعلى', 'عمولة تصاعدية + ترشيح للمكافأة السنوية'], w),
    row([{ t: 'متجاوز', bold: true, color: '2E7D4F' }, 'من ١٠٠٪ إلى أقل من ١٢٠٪', 'العمولة كاملة'], w, { fill: ROWFILL }),
    row([{ t: 'مطابق', bold: true }, 'من ٨٥٪ إلى أقل من ١٠٠٪', 'العمولة بنسبة التحقيق'], w),
    row([{ t: 'دون المستوى', bold: true, color: 'B23B3B' }, 'من ٧٠٪ إلى أقل من ٨٥٪', 'خطة تحسين أداء لمدة ٦٠ يومًا'], w, { fill: ROWFILL }),
    row([{ t: 'غير مقبول', bold: true, color: 'B23B3B' }, 'أقل من ٧٠٪', 'مراجعة استمرار الدور'], w),
  ]));
}

/* ٦ */
body.push(H1('٦ · تدرّج المستهدفات في أول ٩٠ يومًا'));
body.push(P('لا يوجد في أول شهر قاعدة عملاء تكفي لبناء مستهدف إيراد عادل، لذلك تبدأ المستهدفات بالتغطية ثم تنتقل إلى الإيراد:'));
{
  const w = [1600, 2680, 2680, 2678];
  body.push(table(w, [
    headRow(['المؤشر', 'الشهر الأول', 'الشهر الثاني', 'الشهر الثالث'], w),
    row([{ t: 'التركيز', bold: true }, 'التغطية والتعرّف', 'أول إغلاقات', 'بناء المحفظة'], w, { fill: ROWFILL }),
    row([{ t: 'الزيارات', bold: true }, '٤٠ زيارة', '٤٠ زيارة', '٤٠ زيارة'], w),
    row([{ t: 'التواصل', bold: true }, 'الـ٢٦ منشأة ذات الأرقام كاملةً', 'استكمال الـ١٢ الباقية + الجديد', 'الجديد كاملًا'], w, { fill: ROWFILL }),
    row([{ t: 'منشآت جديدة', bold: true }, '≥ ١١ في محيط MK002 (لرفع المرصود من ٤ إلى ١٥)', '٨ منشآت', '٨ منشآت'], w),
    row([{ t: 'العقود', bold: true }, '—', 'عقدان', '٣ عقود'], w, { fill: ROWFILL }),
    row([{ t: 'الشراكات', bold: true }, '—', 'شراكة واحدة داخل المحطة', 'شراكة واحدة'], w),
    row([{ t: 'الاستهلاك المتعاقَد', bold: true }, '—', '≥ 40,000 ر.س', { t: '≥ 150,000 ر.س تراكمي', bold: true }], w, { fill: ROWFILL }),
  ]));
}

/* ٧ */
body.push(H1('٧ · توزيع وقت العمل على المحطات'));
body.push(P('التوزيع مرجّح نحو الفجوة لا نحو الحجم — المحطتان الأقوى تُدارَان حفاظًا لا إنقاذًا:'));
{
  const w = [3400, 1700, 4538];
  body.push(table(w, [
    headRow(['المحطة / المحطات', 'نسبة الوقت', 'الغاية'], w),
    row([{ t: 'MK002 المعيصم + MK019 الشرايع', bold: true }, { t: '٦٠٪', align: AlignmentType.CENTER, bold: true }, 'توسيع القاعدة من الصفر تقريبًا ثم الإغلاق — هنا الفجوة الأكبر وأقل تغطية'], w, { fill: WARNFILL }),
    row([{ t: 'MK007 العمرة النورية', bold: true }, { t: '٢٥٪', align: AlignmentType.CENTER, bold: true }, 'أعلى حجم مبيعات وأقرب محطة إلى إغلاق فجوتها — أسرع عائد على الجهد'], w),
    row([{ t: 'MK023 + MK017', bold: true }, { t: '١٥٪', align: AlignmentType.CENTER, bold: true }, 'حفاظ على العملاء القائمين ومنع تسرّبهم للمنافسين'], w, { fill: ROWFILL }),
  ]));
}

/* ٨ */
body.push(H1('٨ · المؤهلات والمتطلبات'));
body.push(H2('مطلوبة'));
body.push(BUL('من سنتين إلى أربع سنوات خبرة في المبيعات الميدانية بين الشركات (B2B).'));
body.push(BUL('رخصة قيادة سارية وسيارة خاصة (أو بدل مواصلات معتمد).'));
body.push(BUL('معرفة جغرافية عملية بمكة المكرمة — أحياء المعيصم والشرايع والشوقية والعزيزية تحديدًا.'));
body.push(BUL('إجادة استخدام الحاسب على مستوى إدخال البيانات في المنصّة والعمل على الجداول.'));
body.push(BUL('اللغة العربية بطلاقة تحدّثًا وكتابة.'));
body.push(H2('مفضّلة'));
body.push(BUL('خبرة سابقة في قطاع الأساطيل أو تأجير السيارات أو النقل أو الخدمات اللوجستية.'));
body.push(BUL('شبكة علاقات قائمة مع مكاتب التأجير وشركات النقل في مكة.'));
body.push(BUL('الإلمام باللغة الإنجليزية.'));
body.push(H2('الجدارات السلوكية'));
body.push(BUL('الانضباط في التوثيق — الدور يقوم على سجلّ دقيق لا على ذاكرة شخصية.'));
body.push(BUL('احتمال الرفض المتكرر ومواصلة الطَّرق: معدل تحويل ١٥٪ يعني ٨٥٪ رفضًا.'));
body.push(BUL('الاستقلالية في تنظيم اليوم الميداني دون إشراف لصيق.'));
body.push(BUL('النزاهة في نقل الأرقام والوعود التي تُعطى للعملاء.'));

/* ٩ */
body.push(H1('٩ · هيكل التعويض المقترح'));
body.push(P([run('راتب أساسي ثابت + عمولة على الاستهلاك المتحقق فعليًا، لا على قيمة العقد الموقَّع.', { bold: true })], { after: 100 }));
body.push(P('تُصرف العمولة على اللترات المستهلَكة شهريًا من العملاء المتعاقدين. هذا الربط يمنع صيد العقود الورقية التي لا تُترجم إلى مبيعات، ويجعل مصلحة الموظف في بقاء العميل واستمرار تعبئته لا في ضمّه مرّة واحدة.'));
body.push(BUL('بدل مواصلات أو سيارة شركة، وبدل اتصال.'));
body.push(BUL('فترة تجربة ثلاثة أشهر، معيار اجتيازها هو تحقيق مستهدفات الجدول في القسم السادس.'));
body.push(BUL('مراجعة الأهداف والعمولة كل ستة أشهر مع تغيّر قاعدة العملاء وحجمها.'));

/* ١٠ */
body.push(H1('١٠ · الصلاحيات والأدوات'));
{
  const w = [3000, 6638];
  body.push(table(w, [
    row([{ t: 'صلاحية التسعير', bold: true, fill: ROWFILL }, 'يقترح ولا يقرّ — كل خصم كميات يُعتمد من مدير المبيعات قبل الالتزام به أمام العميل'], w),
    row([{ t: 'صلاحية التعاقد', bold: true, fill: ROWFILL }, 'يفاوض ويجهّز العقد، والتوقيع النهائي لصاحب الصلاحية في الشركة'], w),
    row([{ t: 'الميزانيات', bold: true, fill: ROWFILL }, 'يصرف ضمن ميزانية الحملة المعتمدة والمسجّلة في المنصّة فقط'], w),
    row([{ t: 'الأدوات', bold: true, fill: ROWFILL }, 'حساب على منصّة المحطات الخمس · جهاز محمول للتسجيل الميداني · مواد تعريفية ومطبوعات · عيّنات مواد التوزيع'], w),
  ]));
}

/* ١١ */
body.push(H1('١١ · ما لا يشمله الدور'));
body.push(BUL('تشغيل المحطة أو الإشراف على العمالة فيها.'));
body.push(BUL('اعتماد الأسعار أو الخصومات.'));
body.push(BUL('التحصيل المالي ومتابعة الذمم — تُحال إلى الإدارة المالية.'));
body.push(BUL('الصيانة أو الشؤون الفنية للمحطة.'));

/* ١٢ */
body.push(H1('١٢ · ملاحظتان على واقعية المستهدفات'));
body.push(P([run('أولًا: فجوة الـ١١٫٣ مليون لتر في MK002 و MK019 — نحو ٢٥٫٥ مليون ريال — لا يغلقها موظف مبيعات. ', { bold: true }), run('في MK002 الفجوة الشهرية ١٬١٩٢٬٤٢٧ لترًا، ومتوسط التعبئة ٢٠٫٧ لترًا للزيارة، فالوصول إلى الموازنة يستلزم نحو ٥٧٬٥٠٠ زيارة إضافية شهريًا مقابل ١٨٬١٠٧ زيارة فعلية — أي أكثر من أربعة أمثال الحركة الحالية. هذه فجوة موقع وحركة مرور لا فجوة جهد بيعي. يستطيع الدور اقتطاع ما بين ١٠٪ و ١٥٪ منها بعقود الأساطيل، والباقي يحتاج قرارًا تشغيليًا مختلفًا: مراجعة الموازنة نفسها، أو تدخّلًا في المنتج والخدمة والموقع.', {})]));
body.push(P([run('ثانيًا: لا تُحمَّل مستهدفات الإيراد على أول ربع. ', { bold: true }), run('قاعدة العملاء المرصودة اليوم أصغر من أن تُبنى عليها مستهدفات إيراد عادلة، لذلك يبدأ القياس بحجم القاعدة والتغطية، وينتقل إلى الإيراد المتعاقَد عليه من الربع الثاني فصاعدًا. تحميل الدور بمستهدف إيراد كامل من الشهر الأول يُنتج إمّا عقودًا وهمية وإمّا استقالة مبكرة.', {})]));

body.push(spacer(200));
body.push(new Paragraph({
  bidirectional: true, alignment: AlignmentType.CENTER,
  border: { top: { style: BorderStyle.SINGLE, size: 6, color: GOLD, space: 8 } },
  spacing: { before: 200 },
  children: [run('جميع الأرقام الواردة في هذا المستند مستخرجة من منصّة تحليل المحطات الخمس — الفترة يناير ← يوليو ٢٠٢٦. وحدة المستهدفات والمتحقق لترات.', { size: 19, color: GREY, italics: true })],
}));

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 22 } } } },
  numbering: {
    config: [{
      reference: 'bul',
      levels: [{
        level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.RIGHT,
        style: { paragraph: { indent: { right: 360, hanging: 240 } } },
      }],
    }],
  },
  sections: [{
    properties: {
      page: { size: { width: 11906, height: 16838 }, margin: { top: 1134, bottom: 1134, left: 1134, right: 1134 } },
    },
    headers: {
      default: new Header({ children: [new Paragraph({
        bidirectional: true, alignment: AlignmentType.RIGHT, spacing: { after: 60 },
        border: { bottom: { style: BorderStyle.SINGLE, size: 4, color: 'D8D2C7', space: 4 } },
        children: [run('درب — الوصف الوظيفي: أخصائي مبيعات خارجية وشراكات أساطيل', { size: 18, color: GREY })],
      })] }),
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        bidirectional: true, alignment: AlignmentType.CENTER,
        children: [new TextRun({ children: ['صفحة ', PageNumber.CURRENT, ' من ', PageNumber.TOTAL_PAGES],
          rightToLeft: true, font: FONT, size: 18, color: GREY })],
      })] }),
    },
    children: body,
  }],
});

Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2], b); console.log('written', b.length); });
