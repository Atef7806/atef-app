# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy contents
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r Atef/requirements.txt  # ✅ ده صح لأن الملف داخل مجلد Atef

# Run the app
CMD ["python", "Atef/app.py"]  # ✅ برضو عدل المسار لو app.py جوه Atef
