---
name: Giftly project conventions
description: Key architectural decisions and conventions for the Giftly Django REST backend
---

# Giftly conventions

## Authentication
JWT (djangorestframework-simplejwt), NOT DRF Token or Session auth.
Endpoints: `/api/v1/auth/token/`, `/api/v1/auth/token/refresh/`, `/api/v1/auth/token/verify/`
Token blacklist is enabled (ROTATE_REFRESH_TOKENS=True, BLACKLIST_AFTER_ROTATION=True).

**Why:** JWT is stateless and better suited for API-only backends; token blacklist prevents token reuse after logout/rotation.

## API versioning
All app endpoints are under `/api/v1/`. Auth endpoints also under `/api/v1/auth/`.

**Why:** Allows breaking changes in future without breaking existing clients.

## Role system
Four roles: `user`, `business`, `courier`, `admin`. Stored as `User.role` CharField.
Custom permission classes live in `apps/<app>/permissions.py`.

**How to apply:** Never allow role elevation via registration (RegisterSerializer blocks `role=admin`). Admin access requires `is_staff=True` OR `role=admin`.

## Queryset scoping (security)
Every ViewSet `get_queryset()` must scope results by role:
- admin/is_staff → all
- business → own objects only
- courier → assigned orders only
- user → own objects only

**Why:** Without scoping, any authenticated user can read other users' data.

## No DELETE on User
`UserViewSet` uses `http_method_names = ["get", "patch", "head", "options"]` — no DELETE.
Deactivate users with `is_active=False` instead.

## Read/Write serializers on Product
`ProductReadSerializer` — nested category/occasions for GET.
`ProductWriteSerializer` — flat IDs for POST/PATCH, business auto-set from request.user.

## select_related/prefetch_related required
All ViewSet querysets must use select_related/prefetch_related to avoid N+1 queries.

## Migrations convention
Model field changes always get a new migration file (0002_, 0003_ etc).
Do NOT squash initial migrations since they may already be applied in production.
