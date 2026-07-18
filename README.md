# Giftly Backend

Django REST Framework asosidagi marketplace + lead-generation platformasi.

---

## Texnologiyalar

| Texnologiya | Versiya / izoh |
|---|---|
| Python | 3.11+ |
| Django | 4.x |
| Django REST Framework | — |
| PostgreSQL | asosiy BD |
| JWT (SimpleJWT) | stateless autentifikatsiya |
| Pillow | rasm qayta ishlash |
| django-filter | kengaytirilgan filtrlar |
| Gunicorn | production server |
| Docker + docker-compose | konteynerizatsiya |

---

## Loyiha tuzilmasi

```
config/
  settings/
    base.py        ← umumiy sozlamalar
    dev.py         ← local ishlab chiqarish
    prod.py        ← production
  urls.py          ← asosiy router
  wsgi.py

apps/
  users/           ← foydalanuvchilar, rollar, profillar
  catalog/         ← kategoriyalar, mahsulotlar, teglar
  leads/           ← leadlar, buyurtmalar
  media/           ← markazlashgan fayl yuklash
  utils/           ← upload_paths va umumiy yordamchilar
```

---

## Rollar va imkoniyatlar

### 👤 Oddiy foydalanuvchi (`user`)
- Ro'yxatdan o'tish va JWT token olish
- O'z profilini ko'rish / tahrirlash (`/users/me/`)
- Parolni o'zgartirish
- Aktiv mahsulotlarni ko'rish, filtr qilish, qidirish
- Lead yaratish (mahsulotga murojaat)
- O'z leadlarini ko'rish

### 🏢 Biznes (`business`)
- Barcha `user` imkoniyatlari
- BusinessProfile yaratish / tahrirlash
- **Mahsulot yaratish** (`POST /catalog/products/`)
- **O'z mahsulotlarini ko'rish** — aktiv va nofaol (`GET /catalog/products/`)
- **Mahsulotni tahrirlash / o'chirish** (faqat o'ziniki)
- Mahsulotiga kelgan **leadlarni ko'rish**
- **Lead statusini yangilash** (`PATCH /leads/leads/{id}/update_status/`)
  - `new` → `contacted` → `closed`
- O'z mahsulotlariga tegishli **buyurtmalarni ko'rish**
- Rasm yuklash (mahsulot rasmi, logo)

### 🚴 Kuryer (`courier`)
- CourierProfile yaratish / tahrirlash (`is_available` — mavjudlik holati)
- O'ziga tayinlangan **buyurtmalarni ko'rish**

### 🛡️ Admin (`admin`)
- Barcha foydalanuvchilar, profillar — to'liq CRUD
- Barcha mahsulotlar, kategoriyalar, teglar — to'liq CRUD
- Barcha leadlar va buyurtmalar — to'liq CRUD
- Kategoriya daraxti boshqaruvi (3 daraja)
- Foydalanuvchini `is_active=False` qilib bloklash

---

## API Endpointlar

Barcha endpointlar `/api/v1/` prefiksi bilan boshlanadi.

### Autentifikatsiya
```
POST   auth/token/           → JWT access + refresh token olish
POST   auth/token/refresh/   → access tokenni yangilash
POST   auth/token/verify/    → tokenni tekshirish
```
**Header:** `Authorization: Bearer <access_token>`
Access token: **60 daqiqa** | Refresh token: **7 kun**

---

### Foydalanuvchilar `/users/`
```
POST   users/register/              → ro'yxatdan o'tish (admin roli bloklangan)
GET    users/me/                    → o'z profili
PATCH  users/me/                    → profilni yangilash
POST   users/me/change_password/    → parolni o'zgartirish

GET    users/users/                 → ro'yxat (admin: hammasi, user: o'zi)
GET    users/users/{id}/            → profil ko'rish

GET    users/business-profiles/     → biznes profillar
POST   users/business-profiles/     → yaratish (faqat business role)
PATCH  users/business-profiles/{id}/→ tahrirlash (faqat egasi)

GET    users/courier-profiles/      → kuryer profillar
POST   users/courier-profiles/      → yaratish (faqat courier role)
PATCH  users/courier-profiles/{id}/ → tahrirlash (faqat egasi)
```

---

### Katalog `/catalog/`

#### Kategoriyalar
```
GET    catalog/categories/          → tekis ro'yxat
GET    catalog/categories/tree/     → 3-darajali daraxt (nested JSON)
POST   catalog/categories/          → yaratish (faqat admin)
PATCH  catalog/categories/{id}/     → tahrirlash (faqat admin)
DELETE catalog/categories/{id}/     → o'chirish (faqat admin)
```

**Kategoriya daraxt tuzilmasi (3 daraja):**
```
Gullar                    ← 1-daraja
  └── Atirgullar           ← 2-daraja
        └── Qizil          ← 3-daraja (eng chuqur)
Shirinliklar
  └── Desert
  └── Oriflame mahsulotlari
```

#### Mahsulotlar
```
GET    catalog/products/            → ro'yxat (filtr, qidiruv, tartiblash)
POST   catalog/products/            → yaratish (faqat business)
GET    catalog/products/{id}/       → batafsil
PATCH  catalog/products/{id}/       → tahrirlash (faqat egasi yoki admin)
DELETE catalog/products/{id}/       → o'chirish (faqat egasi yoki admin)
```

**Filtrlar:**
```
?category=1                → kategoriya ID (farzandlari ham qamrab olinadi)
?category_slug=gullar      → slug bo'yicha filtr
?occasions=2               → munosabat bo'yicha
?price_min=50000           → minimal narx
?price_max=500000          → maksimal narx
?search=atirgul            → title, description, sku, tag nomi bo'yicha
?ordering=-price           → narx (kamayish)
?ordering=created_at       → qo'shilgan vaqt (o'sish)
?ordering=stock            → qoldiq miqdori bo'yicha
```

**Mahsulot ko'p kategoriyaga tegishli bo'lishi mumkin:**
```json
{ "categories": [1, 4, 7] }
```

#### Munosabatlar va Teglar
```
GET    catalog/occasions/           → munosabatlar ro'yxati
GET    catalog/tags/                → teglar ro'yxati
```

---

### Leadlar va Buyurtmalar `/leads/`

#### Leadlar
```
GET    leads/leads/                 → ro'yxat (rol bo'yicha filtrlangan)
POST   leads/leads/                 → lead yaratish (autentifikatsiya kerak)
GET    leads/leads/{id}/            → batafsil
PATCH  leads/leads/{id}/update_status/ → status yangilash (faqat business)
```

**Lead statuslari:**
```
new → contacted → closed
```

**Kim ko'radi:**
- `user` — o'z leadlari
- `business` — mahsulotlariga kelgan leadlar
- `admin` — hammasi

#### Buyurtmalar
```
GET    leads/orders/                → ro'yxat (rol bo'yicha filtrlangan)
POST   leads/orders/                → buyurtma yaratish
GET    leads/orders/{id}/           → batafsil
PATCH  leads/orders/{id}/           → tahrirlash
```

**Buyurtma statuslari:**
```
pending → paid → in_delivery → delivered
                             ↓
                          cancelled
```

**To'lov usullari:** `cash` | `card` | `transfer` | `online`
**To'lov holati:** `unpaid` | `paid` | `refunded`

`total_amount` avtomatik hisoblanadi: `price_snapshot × qty + delivery_fee`

**Kim ko'radi:**
- `user` — o'z buyurtmalari
- `business` — mahsulotlariga tegishli buyurtmalar
- `courier` — o'ziga tayinlangan buyurtmalar
- `admin` — hammasi

---

### Media `/media/`

Barcha rasmlar (avatar, logo, mahsulot rasmi) bitta markazlashgan endpoint orqali yuklanadi.

```
POST   media/upload/                     → fayl yuklash (multipart/form-data)
GET    media/{id}/                       → fayl ma'lumoti
PATCH  media/{id}/                       → alt_text, is_primary, order
DELETE media/{id}/                       → faylni o'chirish (diskdan ham)
GET    media/for/{ct_id}/{obj_id}/       → obyektning barcha rasmlari
GET    media/content-types/              → frontend uchun content_type ID lari
```

**Yuklash misoli (mahsulot rasmi):**
```http
POST /api/v1/media/upload/
Content-Type: multipart/form-data

file=<rasm.jpg>
purpose=product_image
content_type_id=<Product CT ID>
object_id=5
is_primary=true
```

**Purpose turlari:** `user_avatar` | `business_logo` | `product_image` | `other`
**Ruxsat etilgan formatlar:** `.jpg`, `.jpeg`, `.png`, `.webp`, `.gif`
**Maksimal hajm:** 10 MB

---

## Ma'lumot modellari — muhim fieldlar

### User
| Field | Izoh |
|---|---|
| `role` | `user` / `business` / `courier` / `admin` |
| `is_verified` | admin tasdiqlagan |
| `is_active` | `False` = bloklangan (DELETE o'rniga) |
| `birth_date`, `telegram`, `bio` | qo'shimcha ma'lumot |

### Category
| Field | Izoh |
|---|---|
| `parent` | `null` = 1-daraja (root) |
| `slug` | avtomatik generatsiya |
| `icon` | kategoriya ikonkasi |
| `level` | 1 / 2 / 3 (property) |

### Product
| Field | Izoh |
|---|---|
| `categories` | M2M — ko'p kategoriyali |
| `sale_price` | chegirma narxi (ixtiyoriy) |
| `effective_price` | `sale_price ?? price` (property) |
| `is_in_stock` | `stock >= min_order_qty` (property) |
| `slug` | avtomatik generatsiya |
| `sku` | unikal mahsulot kodi |

### Order
| Field | Izoh |
|---|---|
| `price_snapshot` | buyurtma vaqtidagi narx (o'zgarmaydi) |
| `total_amount` | avtomatik: snapshot × qty + delivery_fee |
| `tracking_number` | kuryer tracking kodi |
| `estimated_delivery` | kutilayotgan yetkazib berish sanasi |
| `delivered_at` | haqiqiy yetkazib berish vaqti |

---

## Muhit sozlamalari (`.env`)

```env
SECRET_KEY=
DEBUG=True
DATABASE_URL=postgresql://user:pass@localhost:5432/giftly
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

---

## Ishga tushirish

```bash
# 1. Docker bilan (tavsiya etiladi)
docker-compose up --build

# 2. Lokal
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver

# 3. Migratsiyalar
python manage.py makemigrations
python manage.py migrate
```

---

## Qilingan ishlar (refactor tarixi)

- **JWT autentifikatsiya** — token blacklist, rotation yoqilgan
- **API versiyalash** — `/api/v1/` prefiksi
- **`apps/media`** — `GenericForeignKey` asosida markazlashgan media app; local → S3 ga o'tish faqat bitta setting
- **`apps/utils/upload_paths.py`** — barcha `upload_to` funksiyalari markazda
- **3-darajali kategoriya daraxti** — self-FK, chuqurlik validatsiyasi, `GET /categories/tree/`
- **Product → ko'p kategoriya (M2M)** — migration mavjud ma'lumotlarni avtomatik ko'chiradi
- **Read/Write serializer** — GET nested, POST/PATCH flat ID lar
- **N+1 yo'q** — barcha viewlarda `select_related` / `prefetch_related`
- **Role-based queryset** — har bir rol faqat o'ziga tegishli ma'lumotni ko'radi
- **`is_active=False`** — foydalanuvchini o'chirish o'rniga bloklash
- **Docker** — healthcheck, `depends_on: condition: service_healthy`, `.dockerignore`
- **Throttling** — anonim: 60/min, user: 300/min

---

## Keyingi qadam (hali qilinmagan)

- [ ] `BusinessProfile` / `CourierProfile` avtomatik yaratish (signal)
- [ ] Test yozish (`pytest-django`)
- [ ] `drf-spectacular` bilan Swagger UI
- [ ] S3 / Cloudinary ulash (`DEFAULT_FILE_STORAGE`)
- [ ] Celery + Redis (async vazifalar, email, bildirishnomalar)
