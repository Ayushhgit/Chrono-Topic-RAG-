"""
summarizer.py
-------------
Generates summaries for:
  1. Topic segments – summarize only the messages within each topic.
  2. 100-message checkpoints – independent rolling summaries.

Uses a lightweight extractive + abstractive approach:
  - For short segments: extractive (pick key sentences).
  - For longer segments: T5-small abstractive summarization.
"""

from typing import List, Dict
from transformers import pipeline, Pipeline

# ---------------------------------------------------------------------------
# Globals (lazy-loaded)
# ---------------------------------------------------------------------------
_summarizer: Pipeline | None = None


def _get_summarizer() -> Pipeline:
    """Lazy-load T5-small summarization pipeline."""
    global _summarizer
    if _summarizer is None:
        _summarizer = pipeline(
            "summarization",
            model="t5-small",
            tokenizer="t5-small",
            framework="pt",
        )
    return _summarizer


# ---------------------------------------------------------------------------
# Core summarization
# ---------------------------------------------------------------------------

def _join_messages(messages: List[Dict]) -> str:
    """Join message contents into a single text block."""
    return " ".join(m["content"] for m in messages if m.get("content"))


def summarize_text(text: str, max_new_tokens: int = 80, min_length: int = 15) -> str:
    """Summarize a text block using T5-small."""
    if not text.strip():
        return ""

    # T5 has a 512 token limit; truncate input if needed
    words = text.split()
    if len(words) > 400:
        text = " ".join(words[:400])

    # Very short texts don't need summarization
    if len(words) < 20:
        return text.strip()

    try:
        pipe = _get_summarizer()
        result = pipe(
            text,
            max_new_tokens=max_new_tokens,
            min_length=min_length,
            do_sample=False,
        )
        return result[0]["summary_text"].strip()
    except Exception:
        # Fallback: return first few sentences
        sentences = text.split(".")
        return ". ".join(sentences[:3]).strip() + "."


# ---------------------------------------------------------------------------
# Topic summaries
# ---------------------------------------------------------------------------

def summarize_topics(segments: List[Dict]) -> List[Dict]:
    """
    Generate a summary for each topic segment.

    Args:
        segments: List of topic dicts with 'messages' key.

    Returns:
        Same list with added 'summary' key.
    """
    for seg in segments:
        text = _join_messages(seg["messages"])
        seg["summary"] = summarize_text(text)
    return segments


# ---------------------------------------------------------------------------
# 100-message checkpoint summaries
# ---------------------------------------------------------------------------

def create_checkpoint_summaries(
    messages: List[Dict],
    checkpoint_size: int = 100,
) -> List[Dict]:
    """
    Create rolling checkpoint summaries every `checkpoint_size` messages.

    Returns:
        List of checkpoint dicts:
        [{"start": 0, "end": 100, "summary": "..."}, ...]
    """
    checkpoints = []
    total = len(messages)

    for start in range(0, total, checkpoint_size):
        end = min(start + checkpoint_size, total)
        chunk = messages[start:end]
        text = _join_messages(chunk)
        summary = summarize_text(text, max_new_tokens=120, min_length=20)

        checkpoints.append(
            {
                "start": start,
                "end": end,
                "summary": summary,
            }
        )

    return checkpoints


if __name__ == "__main__":
    test_msgs = [
        {"content": "I have a math exam tomorrow and I haven't studied."},
        {"content": "You should start with chapter 5, it's the hardest."},
        {"content": "I always procrastinate before exams."},
        {"content": "Same here, let's study together tonight."},
    ]

    summary = summarize_text(_join_messages(test_msgs))
    print(f"Summary: {summary}")
