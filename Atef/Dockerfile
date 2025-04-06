# Use an official Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all files into the container
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip
RUN pip install -r Atef/requirements.txt

# Expose port (if needed, e.g. 5000)
EXPOSE 5000

# Start the app (مثال لو Flask)
CMD ["python", "Atef/app.py"]
