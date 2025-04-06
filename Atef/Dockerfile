# Use a Python base image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install dependencies
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r Atef/requirements.txt

# Expose the port (لو في Flask مثلا)
EXPOSE 5000

# Start command
CMD ["python3", "Atef/app.py"]
