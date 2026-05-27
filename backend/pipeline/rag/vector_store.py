from typing import Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from backend.pipeline.rag.knowledge_base import KnowledgeDocument
from backend.utils.logger import logger


class VectorStore:
    """
    ChromaDB-backed vector store for semantic document retrieval.
    Uses sentence-transformers for embeddings (runs locally, no API needed).
    """

    def __init__(self, collection_name: str = "pricing_knowledge"):
        self.collection_name = collection_name
        self._client = None
        self._collection = None

    def _get_collection(self):
        if self._collection is None:
            self._client = chromadb.Client(
                ChromaSettings(anonymized_telemetry=False)
            )
            self._collection = self._client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            logger.info(f"VectorStore: collection '{self.collection_name}' ready")
        return self._collection

    def upsert(self, doc: KnowledgeDocument) -> None:
        collection = self._get_collection()
        collection.upsert(
            ids=[doc.id],
            documents=[doc.content],
            metadatas=[{
                "doc_type": doc.doc_type,
                "created_at": doc.created_at,
                **{k: str(v) for k, v in doc.metadata.items()},
            }],
        )
        logger.debug(f"VectorStore: upserted doc id={doc.id}")

    def upsert_many(self, docs: list[KnowledgeDocument]) -> None:
        if not docs:
            return
        collection = self._get_collection()
        collection.upsert(
            ids=[d.id for d in docs],
            documents=[d.content for d in docs],
            metadatas=[{
                "doc_type": d.doc_type,
                "created_at": d.created_at,
                **{k: str(v) for k, v in d.metadata.items()},
            } for d in docs],
        )
        logger.info(f"VectorStore: upserted {len(docs)} documents")

    def query(
        self,
        query_text: str,
        n_results: int = 5,
        doc_type: Optional[str] = None,
    ) -> list[dict]:
        """
        Semantic search over stored documents.
        Returns list of {content, metadata, distance} dicts.
        """
        collection = self._get_collection()
        where = {"doc_type": doc_type} if doc_type else None

        results = collection.query(
            query_texts=[query_text],
            n_results=min(n_results, max(collection.count(), 1)),
            where=where,
        )

        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        distances = results.get("distances", [[]])[0]

        return [
            {
                "content": doc,
                "metadata": meta,
                "relevance_score": round(1 - dist, 4),
            }
            for doc, meta, dist in zip(documents, metadatas, distances)
        ]

    def delete(self, doc_id: str) -> None:
        self._get_collection().delete(ids=[doc_id])

    def count(self) -> int:
        return self._get_collection().count()


# Global instance
vector_store = VectorStore()