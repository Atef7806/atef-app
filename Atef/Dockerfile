# Use official Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy all project files
COPY . .

# Move to the project directory
WORKDIR /app/Atef

# Upgrade pip and install dependencies
RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install -r requirements.txt

# Run the app
CMD ["python3", "app.py"]
