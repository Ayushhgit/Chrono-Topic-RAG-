"""
topic_segmentation.py
---------------------
Detects topic changes dynamically using semantic similarity between
consecutive messages. Uses sentence-transformers embeddings.

Optimized for large datasets (100K+ messages):
  - Batched embedding with progress logging
  - Vectorized cosine similarity (no per-pair loop)
  - Configurable max_messages cap
"""

import sys
import numpy as np
from typing import List, Dict, Tuple
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity


# ---------------------------------------------------------------------------
# Globals (lazy-loaded)
# ---------------------------------------------------------------------------
_model: SentenceTransformer | None = None
_model_name = "all-MiniLM-L6-v2"


def _get_model() -> SentenceTransformer:
    """Lazy-load the embedding model."""
    global _model
    if _model is None:
        print(f"  Loading embedding model: {_model_name} ...")
        _model = SentenceTransformer(_model_name)
        print(f"  Model loaded.")
    return _model


# ---------------------------------------------------------------------------
# Embedding helpers
# ---------------------------------------------------------------------------

def embed_texts(texts: List[str], batch_size: int = 256) -> np.ndarray:
    """Embed a list of texts with progress logging for large inputs."""
    model = _get_model()
    total = len(texts)

    if total <= 1000:
        # Small dataset — encode in one shot
        return np.array(model.encode(texts, batch_size=batch_size, show_progress_bar=False))

    # Large dataset — encode in chunks with progress
    all_embeddings = []
    for start in range(0, total, batch_size):
        end = min(start + batch_size, total)
        batch = texts[start:end]
        embs = model.encode(batch, batch_size=batch_size, show_progress_bar=False)
        all_embeddings.append(embs)

        done = min(end, total)
        pct = done / total * 100
        print(f"\r  Embedding: {done}/{total} ({pct:.1f}%)", end="", flush=True)

    print()  # newline after progress
    return np.vstack(all_embeddings)


# ---------------------------------------------------------------------------
# Topic segmentation
# ---------------------------------------------------------------------------

def detect_topic_changes(
    messages: List[Dict],
    threshold: float = 0.35,
    min_segment_size: int = 5,
    max_messages: int = 10000,
) -> Tuple[List[Dict], np.ndarray]:
    """
    Detect topic boundaries using cosine similarity between consecutive
    message embeddings.

    For very large datasets (>max_messages), we uniformly sample messages
    to keep processing time reasonable, then map boundaries back.

    Args:
        messages: List of message dicts with 'content' key.
        threshold: Similarity below this -> new topic.
        min_segment_size: Minimum messages per topic to avoid micro-segments.
        max_messages: Cap for full embedding. If exceeded, sample down.

    Returns:
        Tuple of (segments list, embeddings array)
    """
    if not messages:
        return [], np.array([])

    total = len(messages)
    sampled = False
    sample_indices = None

    # If dataset is too large, sample uniformly
    if total > max_messages:
        print(f"  Dataset has {total} messages, sampling {max_messages} for topic detection...")
        sample_indices = np.linspace(0, total - 1, max_messages, dtype=int)
        working_messages = [messages[i] for i in sample_indices]
        sampled = True
    else:
        working_messages = messages

    texts = [m["content"] for m in working_messages]
    print(f"  Embedding {len(texts)} messages...")
    embeddings = embed_texts(texts)

    # Vectorized consecutive cosine similarity
    print("  Computing topic boundaries...")
    # Normalize embeddings for fast cosine sim
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1  # avoid division by zero
    normed = embeddings / norms
    # Dot product of consecutive pairs = cosine similarity
    similarities = np.sum(normed[:-1] * normed[1:], axis=1)

    # Detect boundaries
    boundaries = [0]
    since_last = 0

    for i, sim in enumerate(similarities):
        since_last += 1
        if sim < threshold and since_last >= min_segment_size:
            boundaries.append(i + 1)
            since_last = 0

    # Map boundaries back to original indices if sampled
    if sampled:
        boundaries = [int(sample_indices[b]) for b in boundaries]
        # Build segments using original message indices
        segments = []
        for seg_idx in range(len(boundaries)):
            start = boundaries[seg_idx]
            end = boundaries[seg_idx + 1] - 1 if seg_idx + 1 < len(boundaries) else total - 1
            segment_messages = messages[start:end + 1]
            segments.append({
                "topic_id": seg_idx + 1,
                "start_index": start,
                "end_index": end,
                "messages": segment_messages,
            })

        # For RAG, we still need all-message embeddings but we can do it lazily
        # Return the sampled embeddings for now; full embeddings built separately
        print(f"  Embedding ALL {total} messages for RAG index...")
        full_embeddings = embed_texts([m["content"] for m in messages])
    else:
        full_embeddings = embeddings
        segments = []
        for seg_idx in range(len(boundaries)):
            start = boundaries[seg_idx]
            end = boundaries[seg_idx + 1] - 1 if seg_idx + 1 < len(boundaries) else len(working_messages) - 1
            segment_messages = working_messages[start:end + 1]
            segments.append({
                "topic_id": seg_idx + 1,
                "start_index": start,
                "end_index": end,
                "messages": segment_messages,
            })

    print(f"  -> {len(segments)} topics detected")
    return segments, full_embeddings


if __name__ == "__main__":
    test_msgs = [
        {"content": "Hey, did you study for the math exam?"},
        {"content": "Yeah, I did chapter 5 and 6 last night."},
        {"content": "The quadratic formula is so confusing."},
        {"content": "I know right, I keep mixing up the signs."},
        {"content": "Anyway, did you see the new Marvel movie?"},
        {"content": "Oh yeah! It was amazing, the VFX were insane."},
        {"content": "The post-credits scene blew my mind."},
        {"content": "I need to go grocery shopping tomorrow."},
        {"content": "Me too, I'm out of milk and bread."},
    ]

    segments, _ = detect_topic_changes(test_msgs, threshold=0.35)
    for seg in segments:
        print(f"Topic {seg['topic_id']}: messages {seg['start_index']}-{seg['end_index']}")
        for m in seg["messages"]:
            print(f"  - {m['content']}")
