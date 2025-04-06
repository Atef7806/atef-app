FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r Atef/requirements.txt

CMD ["python", "Atef/app.py"]
