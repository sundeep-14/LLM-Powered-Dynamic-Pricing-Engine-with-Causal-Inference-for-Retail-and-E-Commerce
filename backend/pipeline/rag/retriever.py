from typing import Optional
from backend.pipeline.rag.vector_store import VectorStore, vector_store
from backend.pipeline.rag.knowledge_base import KnowledgeBase, knowledge_base
from backend.utils.logger import logger


class RAGRetriever:
    """
    Retrieves relevant context documents for LLM report generation.
    Combines vector similarity search with metadata filtering.
    """

    def __init__(self, vs: VectorStore, kb: KnowledgeBase):
        self.vector_store = vs
        self.knowledge_base = kb

    def sync_to_vector_store(self) -> int:
        """Push all knowledge base documents into the vector store."""
        docs = self.knowledge_base.get_all()
        if docs:
            self.vector_store.upsert_many(docs)
        logger.info(f"Retriever: synced {len(docs)} docs to vector store")
        return len(docs)

    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        doc_type: Optional[str] = None,
    ) -> list[dict]:
        """
        Retrieve top-N relevant documents for a query.
        Syncs KB → vector store before querying.
        """
        self.sync_to_vector_store()

        if self.vector_store.count() == 0:
            logger.warning("Retriever: vector store is empty, returning no context")
            return []

        results = self.vector_store.query(
            query_text=query,
            n_results=n_results,
            doc_type=doc_type,
        )

        logger.info(
            f"Retriever: query='{query[:50]}' "
            f"returned {len(results)} results"
        )
        return results

    def build_context_string(self, query: str, n_results: int = 5) -> str:
        """
        Retrieves documents and formats them as a context block
        ready to be injected into an LLM prompt.
        """
        results = self.retrieve(query, n_results=n_results)
        if not results:
            return "No relevant context found."

        lines = ["Relevant context:"]
        for i, r in enumerate(results, 1):
            lines.append(f"{i}. {r['content']} (relevance: {r['relevance_score']})")

        return "\n".join(lines)


# Global instance
retriever = RAGRetriever(vector_store, knowledge_base)