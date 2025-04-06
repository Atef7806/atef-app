# استخدم صورة رسمية فيها Python
FROM python:3.10-slim

# تحديد مجلد العمل داخل الحاوية
WORKDIR /app

# نسخ ملفات المشروع للحاوية
COPY . .

# تثبيت المتطلبات
RUN pip install --upgrade pip
RUN pip install -r Atef/requirements.txt

# فتح البورت (لو بتستخدم Flask مثلًا)
EXPOSE 5000

# الأمر لتشغيل التطبيق
CMD ["python", "Atef/app.py"]
