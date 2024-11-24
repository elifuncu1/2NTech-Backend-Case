Django Docker Setup with PostgreSQL and Redis
Bu proje, Docker Compose kullanılarak Django, PostgreSQL ve Redis altyapısını kurmayı ve çalıştırmayı kolaylaştırır.

Gereksinimler
Bu projeyi çalıştırmadan önce aşağıdaki araçların sisteminize kurulu olduğundan emin olun:

Docker
Docker Compose
Proje Yapısı
bash
Kodu kopyala
.
├── django_project/         # Django uygulaması (kaynak kodlar burada)
├── Dockerfile              # Django için Docker imajı
├── docker-compose.yml      # Servisleri tanımlayan Compose dosyası
├── requirements.txt        # Django bağımlılıklarını tanımlayan dosya
└── README.md               # Bu dosya
Kurulum ve Çalıştırma
1. Projeyi Klonlayın
bash
Kodu kopyala
git clone <repository_url>
cd <repository_name>
2. Ortam Değişkenlerini Ayarlayın
Proje kök dizininde .env dosyasını oluşturun ve aşağıdaki değişkenleri tanımlayın:

env
Kodu kopyala
# .env
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_postgres_password
POSTGRES_DB=your_database_name
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379

DJANGO_SECRET_KEY=your_secret_key
DJANGO_DEBUG=True
3. Docker İmajını Oluşturun ve Servisleri Çalıştırın
bash
Kodu kopyala
docker-compose up --build
Bu komut, aşağıdaki servisleri başlatır:

Django: Ana web uygulaması.
PostgreSQL: Django için veritabanı.
Redis: Django'nun cache ve task queue desteği için.
4. Veritabanını Migrasyonlarla Hazırlayın
Başka bir terminalde aşağıdaki komutları çalıştırın:

bash
Kodu kopyala
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
5. Uygulamayı Açın
Tarayıcınızda şu adresi ziyaret ederek uygulamanızı görüntüleyebilirsiniz:

arduino
Kodu kopyala
http://localhost:8000
6. Yönetici Paneli
Admin paneline erişmek için şu URL'yi kullanın:

bash
Kodu kopyala
http://localhost:8000/admin
7. Servisleri Durdurma
Servisleri durdurmak için:

bash
Kodu kopyala
docker-compose down
Docker Compose Dosyasının Detayları
yaml
Kodu kopyala
version: '3.9'

services:
  web:
    build:
      context: .
    container_name: django_app
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - ./django_project:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env

  db:
    image: postgres:latest
    container_name: postgres_db
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    env_file:
      - .env

  redis:
    image: redis:alpine
    container_name: redis_cache
    ports:
      - "6379:6379"

volumes:
  postgres_data:
Notlar
Bağımlılıkları Güncelleme: Python bağımlılıklarını requirements.txt dosyasına ekleyerek yönetebilirsiniz.
Veritabanı Yönetimi: PostgreSQL için herhangi bir GUI aracı (ör. pgAdmin) ile bağlantı kurabilirsiniz. Bunun için POSTGRES_HOST ve POSTGRES_PORT değerlerini kullanın.
Redis Kullanımı: Redis, Django'nun cache veya Celery gibi görev kuyruğu uygulamalarında kullanılabilir.
