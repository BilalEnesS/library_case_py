# Temel Python imajını kullan
FROM python:3.9-slim

# Betiğin çalışması için postgresql-client kuruyoruz (psql komutu için)
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

# Çalışma dizinini ayarla
WORKDIR /code

# Önce bekleme betiğini kopyala ve çalıştırılabilir yap
COPY wait-for-postgres.sh /wait-for-postgres.sh
RUN chmod +x /wait-for-postgres.sh

# Bağımlılıkları kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama kodunu kopyala
COPY ./app /code/app