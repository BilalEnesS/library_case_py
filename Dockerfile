# Temel Python imajını kullan
FROM python:3.9-slim

# Çalışma dizinini ayarla
WORKDIR /code

# Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY ./app /code/app
COPY ./templates /code/templates

# Port'u expose et
EXPOSE 8000

# Uygulamayı başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]