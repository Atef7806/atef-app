# مرحلة البناء الأولى (لبناء البيئة والتثبيت)
FROM python:3.10-alpine as builder

# تحديد مجلد العمل
WORKDIR /app

# تثبيت الأدوات المطلوبة مثل gcc و musl-dev لبناء الحزم
RUN apk add --no-cache gcc musl-dev libffi-dev

# نسخ ملف requirements.txt
COPY requirements.txt /app/requirements.txt

# تنزيل الحزم من الإنترنت وحفظها في مجلد libs داخل الحاوية
RUN pip download --no-cache-dir -r /app/requirements.txt -d /app/libs/

# مرحلة الصورة النهائية
FROM python:3.10-alpine

# تثبيت الأدوات المطلوبة لبناء الحزم
RUN apk add --no-cache gcc musl-dev libffi-dev

# نسخ الملفات من مرحلة البناء إلى الحاوية النهائية
COPY --from=builder /app /app

# نسخ جميع ملفات المشروع
COPY . /app

# تعيين مجلد العمل
WORKDIR /app

# تثبيت الحزم من ملف requirements.txt داخل الحاوية
RUN pip install --no-cache-dir -r /app/requirements.txt

# فتح البورت
EXPOSE 5000

# تشغيل التطبيق
CMD ["python", "app.py"]
