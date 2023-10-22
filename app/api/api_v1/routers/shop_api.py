from fastapi import APIRouter

from app.api.api_v1.routers.shop import (category, order, payment_method,
                                         product, shop, shop_telegram)

router = APIRouter(prefix='/shop', tags=['Shop'])

router.include_router(shop.router)
router.include_router(product.router)
router.include_router(category.router)
router.include_router(order.router)
router.include_router(payment_method.router)

router.include_router(shop_telegram.router)
