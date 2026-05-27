from typing import Optional
from backend.pipeline.rag.retriever import RAGRetriever, retriever
from backend.pipeline.rag.knowledge_base import knowledge_base
from backend.core.config import settings
from backend.utils.helpers import utcnow_iso
from backend.utils.logger import logger


REPORT_PROMPTS = {
    "pricing_summary": (
        "Generate a concise pricing strategy report for the given product. "
        "Include: current optimal price recommendation, profit analysis, "
        "demand forecast, and competitor positioning. "
        "Be specific with numbers. Format with clear sections."
    ),
    "competitor_analysis": (
        "Generate a competitor price analysis report. "
        "Include: competitor price comparison, our price positioning, "
        "recommended price adjustments, and market opportunities. "
        "Be specific and actionable."
    ),
    "market_trend": (
        "Generate a market trend analysis report. "
        "Include: key trends affecting pricing, demand patterns, "
        "seasonal factors, and strategic recommendations. "
        "Be data-driven and forward-looking."
    ),
    "revenue_forecast": (
        "Generate a revenue forecast report based on the pricing data. "
        "Include: projected revenue at optimal price, sensitivity analysis, "
        "risk factors, and growth opportunities."
    ),
}


class LLMReportGenerator:
    """
    Generates natural language reports using RAG + LLM.

    Flow:
    1. Build context from vector store (RAG retrieval)
    2. Construct prompt with context + report type instructions
    3. Call LLM API (OpenAI or Anthropic based on config)
    4. Return structured report
    """

    def __init__(self, ret: RAGRetriever):
        self.retriever = ret

    async def generate(
        self,
        report_type: str,
        product_id: Optional[str] = None,
        extra_context: Optional[str] = None,
    ) -> dict:
        query = f"{report_type} product {product_id or 'all'}"
        context = self.retriever.build_context_string(query, n_results=6)

        instruction = REPORT_PROMPTS.get(
            report_type,
            "Generate a detailed pricing analysis report based on the context provided."
        )

        prompt = self._build_prompt(
            instruction=instruction,
            context=context,
            product_id=product_id,
            extra_context=extra_context,
        )

        logger.info(f"Generating {report_type} report for product_id={product_id}")

        try:
            report_text = await self._call_llm(prompt)
            status = "completed"
        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            report_text = self._fallback_report(report_type, product_id, context)
            status = "fallback"

        return {
            "report_type": report_type,
            "product_id": product_id,
            "content": report_text,
            "status": status,
            "context_used": context[:500] + "..." if len(context) > 500 else context,
            "generated_at": utcnow_iso(),
        }

    def _build_prompt(
        self,
        instruction: str,
        context: str,
        product_id: Optional[str],
        extra_context: Optional[str],
    ) -> str:
        parts = [
            f"You are an expert retail pricing analyst.",
            f"\n\nTask: {instruction}",
            f"\n\nContext from knowledge base:\n{context}",
        ]
        if product_id:
            parts.append(f"\n\nProduct ID: {product_id}")
        if extra_context:
            parts.append(f"\n\nAdditional context: {extra_context}")
        parts.append("\n\nGenerate a professional, data-driven report:")
        return "".join(parts)

    async def _call_llm(self, prompt: str) -> str:
        """
        Calls OpenAI or Anthropic based on which API key is configured.
        Falls back to a structured template if neither is set.
        """
        if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "skip-for-now":
            return await self._call_openai(prompt)
        elif settings.ANTHROPIC_API_KEY and settings.ANTHROPIC_API_KEY != "skip-for-now":
            return await self._call_anthropic(prompt)
        else:
            raise ValueError("No LLM API key configured")

    async def _call_openai(self, prompt: str) -> str:
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.3,
        )
        return response.choices[0].message.content

    async def _call_anthropic(self, prompt: str) -> str:
        from anthropic import AsyncAnthropic
        client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        response = await client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text

    def _fallback_report(
        self,
        report_type: str,
        product_id: Optional[str],
        context: str,
    ) -> str:
        return (
            f"# {report_type.replace('_', ' ').title()} Report\n\n"
            f"**Product:** {product_id or 'All Products'}\n"
            f"**Generated:** {utcnow_iso()}\n\n"
            f"## Available Data\n{context}\n\n"
            f"## Note\n"
            f"This is a template report. Configure OPENAI_API_KEY or "
            f"ANTHROPIC_API_KEY in your .env file to enable AI-generated reports."
        )


# Global instance
report_generator = LLMReportGenerator(retriever)