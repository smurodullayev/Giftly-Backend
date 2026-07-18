# Giftly Backend

Django REST Framework asosidagi marketplace + lead-generation platformasi.

## Stack

| Texnologiya | Versiya |
|---|---|
| Python | 3.11 |
| Django | 5.0.6 |
| Django REST Framework | 3.15.1 |
| JWT Auth | djangorestframework-simplejwt 5.3.1 |
| CORS | django-cors-headers 4.4.0 |
| Filtering | django-filter 24.2 |
| API Docs | drf-spectacular 0.27.2 |
| Database | PostgreSQL 16 |
| Server (prod) | Gunicorn 22.0.0 |

## Loyiha strukturasi

```
giftly-backend/
├── apps/
│   ├── users/      — User, BusinessProfile, CourierProfile
│   ├── catalog/    — Category, Occasion, Product
│   └── leads/      — Lead, Order
├── config/
│   ├── settings/
│   │   ├── base.py   — umumiy sozlamalar
│   │   ├── dev.py    — development
│   │   └── prod.py   — production
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── manage.py
```

## Sozlash (local)

1. `.env.example` → `.env` ko'chiring va qiymatlarni to'ldiring
2. Docker bilan ishga tushirish:
   ```bash
   docker-compose up --build
   ```
3. Yoki qo'lda (PostgreSQL o'rnatilgan bo'lsa):
   ```bash
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py createsuperuser
   python manage.py runserver
   ```

## API

Barcha endpointlar `/api/v1/` prefiksi bilan boshlanadi.

### Autentifikatsiya (JWT)
| Method | URL | Tavsif |
|---|---|---|
| POST | `/api/v1/auth/token/` | Login — access + refresh token olish |
| POST | `/api/v1/auth/token/refresh/` | Access tokenni yangilash |
| POST | `/api/v1/auth/token/verify/` | Token tekshirish |

### Foydalanuvchilar
| Method | URL | Tavsif |
|---|---|---|
| POST | `/api/v1/users/register/` | Ro'yxatdan o'tish |
| GET | `/api/v1/users/users/me/` | Joriy foydalanuvchi |
| POST | `/api/v1/users/users/change-password/` | Parol o'zgartirish |
| GET/PATCH | `/api/v1/users/users/{id}/` | Profil ko'rish/o'zgartirish |

### Katalog
| Method | URL | Tavsif |
|---|---|---|
| GET | `/api/v1/catalog/products/` | Mahsulotlar ro'yxati (filtr/qidiruv) |
| POST | `/api/v1/catalog/products/` | Mahsulot qo'shish (faqat business) |
| GET/PATCH/DELETE | `/api/v1/catalog/products/{id}/` | CRUD |
| GET | `/api/v1/catalog/categories/` | Kategoriyalar |
| GET | `/api/v1/catalog/occasions/` | Munosabatlar |

### Leadlar
| Method | URL | Tavsif |
|---|---|---|
| GET/POST | `/api/v1/leads/leads/` | Leadlar |
| PATCH | `/api/v1/leads/leads/{id}/update-status/` | Status yangilash (faqat business) |
| GET/POST | `/api/v1/leads/orders/` | Buyurtmalar |

### Hujjatlar
- Swagger: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI JSON: `/api/schema/`

## Rollar va ruxsatlar

| Rol | Imkoniyatlar |
|---|---|
| `user` | Mahsulotlarni ko'rish, lead yuborish |
| `business` | O'z mahsulotlarini boshqarish, leadlarni ko'rish va status yangilash |
| `courier` | O'ziga tayinlangan orderlarni ko'rish |
| `admin` | Hammasi |

## Environment o'zgaruvchilar

`.env.example` faylida barcha kerakli o'zgaruvchilar bor.
Muhim: `SECRET_KEY` hech qachon default qiymatga ega emas — majburiy.

## User preferences

- Kod va izohlar o'zbek tilida bo'lishi mumkin
- Django REST best practices qat'iy saqlanishi kerak
- Har bir o'zgarishda migratsiya fayllari ham yangilanishi kerak
