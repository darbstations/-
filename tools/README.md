# توليد نسخة PDF من الكراسة

الكراسة مصدرها `station-site-advantages.html`. لتوليد PDF بعد أي تعديل:

```bash
cd tools
npm i @fontsource/noto-sans-arabic @fontsource/cairo playwright-core
node build-dossier-pdf.js        # ينتج ../darb-station-dossier.pdf
```

يعتمد على Chromium المثبّت مسبقًا في `/opt/pw-browsers`.
الخطوط تُضمَّن داخل الملف كـ base64 حتى يظهر النص العربي بشكل صحيح دون الاعتماد على خطوط النظام.
