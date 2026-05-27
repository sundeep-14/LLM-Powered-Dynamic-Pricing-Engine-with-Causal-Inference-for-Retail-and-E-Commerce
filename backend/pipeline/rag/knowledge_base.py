from dataclasses import dataclass, field
from typing import Optional
from backend.utils.helpers import generate_uuid, utcnow_iso
from backend.utils.logger import logger


@dataclass
class KnowledgeDocument:
    """A single document stored in the knowledge base."""
    id: str
    content: str
    doc_type: str          # "pricing_rule" | "product" | "competitor" | "market_trend"
    metadata: dict = field(default_factory=dict)
    created_at: str = field(default_factory=utcnow_iso)


class KnowledgeBase:
    """
    Manages the collection of documents available for RAG retrieval.
    Documents are added from product data, pricing history,
    competitor data, and market trends.
    """

    def __init__(self):
        self._documents: dict[str, KnowledgeDocument] = {}

    def add_document(
        self,
        content: str,
        doc_type: str,
        metadata: Optional[dict] = None,
        doc_id: Optional[str] = None,
    ) -> KnowledgeDocument:
        doc_id = doc_id or generate_uuid()
        doc = KnowledgeDocument(
            id=doc_id,
            content=content,
            doc_type=doc_type,
            metadata=metadata or {},
        )
        self._documents[doc_id] = doc
        logger.debug(f"Knowledge base: added doc id={doc_id} type={doc_type}")
        return doc

    def add_pricing_context(self, product_id: str, optimization_result: dict) -> KnowledgeDocument:
        content = (
            f"Product {product_id} pricing optimization result: "
            f"optimal price={optimization_result.get('optimal_price')}, "
            f"expected profit={optimization_result.get('expected_profit')}, "
            f"expected demand={optimization_result.get('expected_demand')}, "
            f"margin={optimization_result.get('expected_margin_pct')}%, "
            f"convergence={optimization_result.get('convergence')}."
        )
        return self.add_document(
            content=content,
            doc_type="pricing_rule",
            metadata={"product_id": product_id, **optimization_result},
        )

    def add_competitor_context(self, product_id: str, competitors: list) -> KnowledgeDocument:
        if not competitors:
            content = f"No competitor data available for product {product_id}."
        else:
            prices = [c.get("price", 0) for c in competitors]
            avg = sum(prices) / len(prices)
            content = (
                f"Competitor analysis for product {product_id}: "
                f"{len(competitors)} competitors tracked. "
                f"Average competitor price={avg:.2f}, "
                f"min={min(prices):.2f}, max={max(prices):.2f}."
            )
        return self.add_document(
            content=content,
            doc_type="competitor",
            metadata={"product_id": product_id},
        )

    def add_market_trend(self, trend: str, category: str = "general") -> KnowledgeDocument:
        return self.add_document(
            content=trend,
            doc_type="market_trend",
            metadata={"category": category},
        )

    def get_all(self, doc_type: Optional[str] = None) -> list[KnowledgeDocument]:
        docs = list(self._documents.values())
        if doc_type:
            docs = [d for d in docs if d.doc_type == doc_type]
        return docs

    def get_by_id(self, doc_id: str) -> Optional[KnowledgeDocument]:
        return self._documents.get(doc_id)

    def clear(self):
        self._documents.clear()

    def __len__(self):
        return len(self._documents)


# Global instance
knowledge_base = KnowledgeBase()