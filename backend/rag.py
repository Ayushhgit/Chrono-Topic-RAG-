"""
rag.py
------
Dual-layer Retrieval-Augmented Generation system.

Layer A: Topic-level retrieval
  - Embed topic summaries
  - Retrieve top-k relevant topics for a query

Layer B: Message-level retrieval
  - Embed all individual messages
  - Retrieve top-k relevant messages for a query

Answer generation:
  - Combine retrieved topic summaries + messages
  - Generate answer grounded ONLY in retrieved data
"""

import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics.pairwise import cosine_similarity

from topic_segmentation import embed_texts


class RAGSystem:
    """Dual-layer retrieval-augmented generation system."""

    def __init__(self):
        self.messages: List[Dict] = []
        self.message_embeddings: np.ndarray | None = None

        self.topics: List[Dict] = []
        self.topic_summary_embeddings: np.ndarray | None = None

        self.checkpoints: List[Dict] = []

    # ------------------------------------------------------------------
    # Index building
    # ------------------------------------------------------------------

    def index_messages(self, messages: List[Dict], embeddings: np.ndarray):
        """Store messages and their pre-computed embeddings."""
        self.messages = messages
        self.message_embeddings = embeddings

    def index_topics(self, topics: List[Dict]):
        """Embed topic summaries and store them."""
        self.topics = topics
        summaries = [t.get("summary", "") for t in topics]
        if summaries:
            self.topic_summary_embeddings = embed_texts(summaries)

    def index_checkpoints(self, checkpoints: List[Dict]):
        """Store checkpoint summaries."""
        self.checkpoints = checkpoints

    # ------------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------------

    def retrieve_topics(self, query: str, top_k: int = 3) -> List[Dict]:
        """Retrieve top-k relevant topic segments for a query."""
        if self.topic_summary_embeddings is None or len(self.topics) == 0:
            return []

        query_emb = embed_texts([query])
        sims = cosine_similarity(query_emb, self.topic_summary_embeddings)[0]

        top_indices = np.argsort(sims)[::-1][:top_k]
        results = []
        for idx in top_indices:
            topic = self.topics[idx].copy()
            topic["relevance_score"] = float(sims[idx])
            # Don't send full messages list in response
            topic.pop("messages", None)
            results.append(topic)
        return results

    def retrieve_messages(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve top-k relevant individual messages for a query."""
        if self.message_embeddings is None or len(self.messages) == 0:
            return []

        query_emb = embed_texts([query])
        sims = cosine_similarity(query_emb, self.message_embeddings)[0]

        top_indices = np.argsort(sims)[::-1][:top_k]
        results = []
        for idx in top_indices:
            msg = self.messages[idx].copy()
            msg["relevance_score"] = float(sims[idx])
            results.append(msg)
        return results

    # ------------------------------------------------------------------
    # Answer generation
    # ------------------------------------------------------------------

    def generate_answer(
        self,
        query: str,
        persona: Dict | None = None,
        top_k_topics: int = 3,
        top_k_messages: int = 5,
    ) -> Dict:
        """
        Generate an answer using dual-layer retrieval.

        1. Retrieve relevant topic summaries.
        2. Retrieve relevant individual messages.
        3. Combine context and generate a grounded answer.

        Args:
            query: User's question.
            persona: Optional persona dict to include in context.
            top_k_topics: Number of topics to retrieve.
            top_k_messages: Number of messages to retrieve.

        Returns:
            Dict with 'response', 'retrieved_topics', 'retrieved_messages'.
        """
        retrieved_topics = self.retrieve_topics(query, top_k_topics)
        retrieved_messages = self.retrieve_messages(query, top_k_messages)

        # Build context
        context_parts = []

        if retrieved_topics:
            context_parts.append("=== Relevant Topic Summaries ===")
            for t in retrieved_topics:
                context_parts.append(
                    f"Topic {t['topic_id']} (messages {t['start_index']}-{t['end_index']}): "
                    f"{t.get('summary', 'N/A')}"
                )

        if retrieved_messages:
            context_parts.append("\n=== Relevant Messages ===")
            for m in retrieved_messages:
                context_parts.append(
                    f"[{m['speaker']}] (msg #{m['index']}): {m['content']}"
                )

        if persona:
            context_parts.append("\n=== User Persona ===")
            for key, values in persona.items():
                if values:
                    context_parts.append(f"{key}: {', '.join(values)}")

        context = "\n".join(context_parts)

        # Generate answer grounded in context
        answer = self._synthesize_answer(query, context, persona)

        return {
            "response": answer,
            "retrieved_topics": retrieved_topics,
            "retrieved_messages": retrieved_messages,
        }

    def _synthesize_answer(
        self,
        query: str,
        context: str,
        persona: Dict | None = None,
    ) -> str:
        """
        Synthesize an answer from retrieved context.
        Uses rule-based synthesis (no external LLM API).
        """
        query_lower = query.lower()

        # Persona-related queries
        persona_keywords = [
            "person", "personality", "kind of person", "who is",
            "habits", "habit", "routine", "sleep", "eat", "food",
            "talk", "speak", "communicate", "style", "tone",
            "emoji", "formal", "informal", "traits", "trait",
        ]

        is_persona_query = any(kw in query_lower for kw in persona_keywords)

        if is_persona_query and persona:
            return self._format_persona_answer(query_lower, persona, context)

        # General RAG answer
        return self._format_rag_answer(query, context)

    def _format_persona_answer(
        self, query: str, persona: Dict, context: str
    ) -> str:
        """Format an answer for persona-related queries."""
        parts = []

        if "habit" in query or "routine" in query or "sleep" in query or "food" in query:
            habits = persona.get("habits", [])
            if habits:
                parts.append("Based on the conversations, here are the user's habits:")
                for h in habits:
                    parts.append(f"  • {h}")
            else:
                parts.append("No clear habitual patterns were detected in the conversations.")

        elif "talk" in query or "communicate" in query or "style" in query or "tone" in query:
            style = persona.get("communication_style", [])
            if style:
                parts.append("Here's how this user communicates:")
                for s in style:
                    parts.append(f"  • {s}")
            else:
                parts.append("Not enough data to determine communication style.")

        elif "person" in query or "personality" in query or "trait" in query:
            # Give a comprehensive persona overview
            parts.append("Based on conversation analysis, here's the user profile:\n")

            traits = persona.get("personality_traits", [])
            if traits:
                parts.append("**Personality Traits:**")
                for t in traits:
                    parts.append(f"  • {t}")

            facts = persona.get("personal_facts", [])
            if facts:
                parts.append("\n**Personal Facts:**")
                for f in facts:
                    parts.append(f"  • {f}")

            habits = persona.get("habits", [])
            if habits:
                parts.append("\n**Habits:**")
                for h in habits:
                    parts.append(f"  • {h}")

            style = persona.get("communication_style", [])
            if style:
                parts.append("\n**Communication Style:**")
                for s in style:
                    parts.append(f"  • {s}")

        if not parts:
            # Fallback: show everything
            parts.append("Here's what we know about this user:\n")
            for key, values in persona.items():
                if values:
                    parts.append(f"**{key.replace('_', ' ').title()}:**")
                    for v in values:
                        parts.append(f"  • {v}")

        # Add supporting evidence from retrieved messages
        parts.append("\n\n*This analysis is based on patterns found across multiple messages in the conversation data.*")

        return "\n".join(parts)

    def _format_rag_answer(self, query: str, context: str) -> str:
        """Format a general RAG answer from retrieved context."""
        if not context.strip():
            return "I couldn't find relevant information in the conversation data to answer your question."

        parts = [
            f"Based on the conversation data, here's what I found relevant to your question:\n",
        ]

        # Parse context and present it nicely
        lines = context.split("\n")
        for line in lines:
            if line.startswith("==="):
                parts.append(f"\n**{line.replace('=', '').strip()}**")
            elif line.strip():
                parts.append(line)

        parts.append(
            "\n\n*This answer is grounded entirely in the retrieved conversation data.*"
        )
        return "\n".join(parts)
