from fastapi import APIRouter

from app.api.api_v1.routers.shop import (category, order, payment,
                                         payment_method, product,
                                         shipment_method, shop, shop_telegram,
                                         table, dashboard)

router = APIRouter(prefix='/shop', tags=[])

router.include_router(shop.router)
router.include_router(product.router)
router.include_router(category.router)
router.include_router(order.router)
router.include_router(payment_method.router)
router.include_router(shipment_method.router)
router.include_router(payment.router)
router.include_router(table.router)
router.include_router(dashboard.router)

router.include_router(shop_telegram.router)
