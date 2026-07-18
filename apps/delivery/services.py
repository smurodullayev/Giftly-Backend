"""
Yetkazib berish narxi hisoblash servisi.
Model va View dan alohida — qayta ishlatish uchun.
"""

from decimal import Decimal

from .models import DeliveryZone


def find_zone(destination_address: str) -> DeliveryZone | None:
    """
    Manzilga mos zonani topadi.
    Kalit so'zlar katta/kichik harfga sezgir emas.
    Birinchi mos kelgan zona (sort_order bo'yicha) qaytariladi.
    """
    address_lower = destination_address.lower()
    zones = DeliveryZone.objects.filter(is_active=True).order_by("sort_order", "name")

    for zone in zones:
        if zone.is_default:
            continue
        for keyword in zone.keywords:
            if keyword.lower() in address_lower:
                return zone

    # Hech qaysi mos kelmadi — standart zona
    return zones.filter(is_default=True).first()


def calculate_delivery(
    destination_address: str,
    weight_grams: int = 0,
    order_amount: Decimal = None,
) -> dict:
    """
    Manzil va og'irlik asosida yetkazib berish narxini hisoblaydi.

    Qaytaradi:
    {
        "zone_name": "Toshkent",
        "zone_id": 1,
        "weight_grams": 500,
        "weight_kg": 0.5,
        "base_fee": 15000,
        "per_kg_fee": 2000,
        "delivery_fee": 16000,
        "is_free": False,
        "free_above_amount": None,
    }
    """
    zone = find_zone(destination_address)

    if not zone:
        return {
            "zone_name": None,
            "zone_id": None,
            "weight_grams": weight_grams,
            "weight_kg": round(weight_grams / 1000, 3),
            "base_fee": Decimal("0"),
            "per_kg_fee": Decimal("0"),
            "delivery_fee": Decimal("0"),
            "is_free": False,
            "free_above_amount": None,
            "error": "Ushbu manzil uchun yetkazib berish zonasi topilmadi.",
        }

    fee = zone.calculate_fee(weight_grams, order_amount)
    is_free = (
        zone.free_above_amount is not None
        and order_amount is not None
        and order_amount >= zone.free_above_amount
    )

    return {
        "zone_name": zone.name,
        "zone_id": zone.pk,
        "weight_grams": weight_grams,
        "weight_kg": round(weight_grams / 1000, 3),
        "base_fee": zone.base_fee,
        "per_kg_fee": zone.per_kg_fee,
        "delivery_fee": fee,
        "is_free": is_free,
        "free_above_amount": zone.free_above_amount,
    }
