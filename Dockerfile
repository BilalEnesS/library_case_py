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

# Startup script'ini kopyala ve çalıştırılabilir yap
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Port'u expose et
EXPOSE 8000

# Startup script'ini çalıştır
CMD ["/start.sh"]