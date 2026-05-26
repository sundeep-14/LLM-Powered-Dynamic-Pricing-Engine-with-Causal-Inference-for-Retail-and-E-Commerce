from typing import Optional
from fastapi import HTTPException, status
from backend.utils.helpers import generate_uuid, utcnow_iso
from backend.utils.logger import logger

# ── In-memory store (swap for async DB calls when feature/database lands) ─────
_products: dict[str, dict] = {}


class ProductService:

    async def create(self, data: dict, created_by: str) -> dict:
        product_id = generate_uuid()
        product = {
            "id": product_id,
            "name": data["name"],
            "sku": data["sku"],
            "category": data.get("category", ""),
            "base_price": data["base_price"],
            "current_price": data["base_price"],
            "stock": data.get("stock", 0),
            "is_active": True,
            "created_by": created_by,
            "created_at": utcnow_iso(),
            "updated_at": utcnow_iso(),
        }
        _products[product_id] = product
        logger.info(f"Product created: {data['name']} (id={product_id})")
        return product

    async def get_all(self, skip: int = 0, limit: int = 20) -> list:
        items = list(_products.values())
        return items[skip: skip + limit]

    async def get_by_id(self, product_id: str) -> dict:
        product = _products.get(product_id)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
        return product

    async def update(self, product_id: str, data: dict) -> dict:
        product = await self.get_by_id(product_id)
        product.update({k: v for k, v in data.items() if v is not None})
        product["updated_at"] = utcnow_iso()
        logger.info(f"Product updated: id={product_id}")
        return product

    async def delete(self, product_id: str) -> None:
        await self.get_by_id(product_id)
        del _products[product_id]
        logger.info(f"Product deleted: id={product_id}")


product_service = ProductService()