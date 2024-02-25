FROM python:3.8-bullseye 

WORKDIR /app

COPY requirements-live.txt .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --no-cache-dir -r requirements-live.txt

COPY . .

EXPOSE 5000

CMD ["python", "./src/app.py"]