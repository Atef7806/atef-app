# Use official Python image
FROM python:3.10-slim

# Set work directory
WORKDIR /app

# Copy all project files
COPY . .

# Install dependencies from correct path
RUN pip install --upgrade pip
RUN pip install -r Atef1/Atef/requirements.txt

# Run the app
CMD ["python", "Atef1/Atef/app.py"]
