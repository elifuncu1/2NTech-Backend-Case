# Python 3.10 base image
FROM python:3.10-slim

# Çalışma dizinini ayarlayın
WORKDIR /app

# Gereksinimler dosyasını konteynıra kopyalayın
COPY requirements.txt /app/

# Gereksinimleri yükleyin
RUN pip install --no-cache-dir -r requirements.txt

# Django projesini kopyalayın
COPY . /app/

# Uygulama başlatma komutu
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
