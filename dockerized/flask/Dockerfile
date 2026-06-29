FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN apt-get update && apt-get install -y procps iputils-ping curl && rm -rf /var/lib/apt/lists/*

RUN pip install flask psutil

EXPOSE 5000

CMD ["python", "app.py"]
