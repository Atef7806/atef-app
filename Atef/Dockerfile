# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy contents
COPY . .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r Atef/requirements.txt

# Run the app using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "Atef.app:app"]
