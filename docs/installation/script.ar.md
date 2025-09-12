# تشغيل كبرنامج نصي

## تثبيت التبعيات

```bash
uv sync
# أو استخدم pip
pip install --no-cache-dir .
```

## تعيين مفتاح API

```bash
export api_key={your_key}
```

## تشغيل

```bash
python3 run main.py {i18n_config_file} {docs_directory} {reserved_words,comma_separated} {optional_file_list}
```

## مثال

```bash
# ترجمة وثائق المشروع بالكامل (kepler ككلمة محجوزة)
python3 run main.py mkdocs.yml docs kepler

# استخدام كلمات رئيسية محجوزة متعددة لترجمة ملفات محددة
python3 run main.py mkdocs.yml docs kepler,kepler-model-server,pod /workspace/docs/index.md

# مثال أمر Python محدد
python3 main.py /Users/yuanyi/OpenSource/kepler-doc/mkdocs.yml /Users/yuanyi/OpenSource/kepler-doc/docs kepler,kepler-model-server,pod
```