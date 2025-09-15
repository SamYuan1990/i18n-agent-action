# دليل مستخدم خادم MCP للتدويل (i18n)

## معلومات الصورة
- **اسم الصورة**: `ghcr.io/samyuan1990/i18n-agent-action:mcp`
- **الصورة الأساسية**: Python 3.12
- **دليل العمل**: `/app`

## الوصف
هذا خادم بروتوكول سياق النموذج (MCP) مصمم لمهام التدويل (i18n)، يوفر وظائف متعلقة بالترجمة مع دعم لنماذج ONNX المخصصة.

## البدء السريع

### سحب الصورة
```bash
docker pull ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### تشغيل الحاوية
```bash
docker run -p 8080:8080 -e api_key="YOUR_API_KEY" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

### تكوين متغيرات البيئة
- `api_key`: (مطلوب) مفتاح API لخدمة الترجمة
- `encoder`: (اختياري) مسار ملف نموذج ONNX للمُشفر (الافتراضي: `/tmp/base-encoder.onnx`)
- `decoder`: (اختياري) مسار ملف نموذج ONNX لفك التشفير (الافتراضي: `/tmp/base-decoder.onnx`)
- `tokens`: (اختياري) مسار ملف نموذج ONNX للرموز (الافتراضي: `/tmp/base-tokens.onnx`)

مثال مع نماذج مخصصة:
```bash
docker run -p 8080:8080 \
  -e api_key="your-translation-api-key" \
  -e encoder="/app/models/custom-encoder.onnx" \
  -e decoder="/app/models/custom-decoder.onnx" \
  -e tokens="/app/models/custom-tokens.onnx" \
  ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## تحميل نماذج ONNX المخصصة
يمكنك تحميل ملفات نماذج ONNX الخاصة بك إلى الحاوية باستخدام أحجام Docker:

```bash
docker run -p 8080:8080 \
  -e api_key="your-api-key" \
  -v /path/to/your/models:/app/models \
  -e encoder="/app/models/your-encoder.onnx" \
  -e decoder="/app/models/your-decoder.onnx" \
  -e tokens="/app/models/your-tokens.onnx" \
  ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## تكوين المنفذ
- المنفذ المعروض افتراضيًا: **8080**
- يمكنك ضبط تعيين منفذ المضيف:
  ```bash
  docker run -p 3000:8080 [...] # يعين منفذ المضيف 3000 إلى منفذ الحاوية 8080
  ```

## هيكل المشروع
- يستخدم Poetry لإدارة التبعيات
- الكود المصدري موجود في دليل `/app` داخل الحاوية
- يثبت تلقائيًا جميع التبعيات الإضافية (بما في ذلك تبعيات التطوير)

## التكوين المخصص
لتخصيص إضافي:

1. **تحميل ملفات التكوين**:
   ```bash
   docker run -v /path/to/your/config.yaml:/app/config.yaml [...]
   ```

2. **استخدام متغيرات البيئة**:
   ```bash
   docker run -e api_key="your-key" -e OTHER_VAR="value" [...]
   ```

## استخدام التطوير
إذا كنت بحاجة إلى تعديل الكود أو التطوير:

```bash
# استنساخ الكود المصدري
git clone <your-repo>
cd <repo-directory>

# استخدام Docker Compose (موصى به)
# أو استخدام docker run مع تحميل الكود المحلي
docker run -p 8080:8080 -v $(pwd):/app -e api_key="your-key" ghcr.io/samyuan1990/i18n-agent-action:mcp
```

## فحص الصحة
بعد بدء الخادم، يمكنك التحقق من حالته عن طريق الوصول إلى:
```bash
curl http://localhost:8080/health
```

## ملاحظات
1. تأكد من توفير متغير بيئة `api_key` صالح
2. تقوم الحاوية بإزالة ملف config.yaml الافتراضي تلقائيًا عند البدء
3. للتكوين المستمر، قم بتحميل
ملفات التكوين الخارجية
4. للنماذج المخصصة، قم بتحميل ملفات ONNX الخاصة بك وتعيين متغيرات البيئة المناسبة

## الدعم والملاحظات
إذا واجهت مشكلات أو تحتاج إلى دعم، يرجى تقديم مشكلة من خلال مستودع المشروع أو الاتصال بالمسؤول.