FROM python:3.8-bullseye 

WORKDIR /app

COPY requirements-live.txt .

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONPATH=/app/src

RUN pip install --no-cache-dir -r requirements-live.txt

COPY . .

CMD ["python", "./src/main.py"]
# CMD ["python", "-c", "import sys; print(sys.path)"]
