"""
data_loader.py
--------------
Loads conversation CSV and flattens all messages into a single
chronologically-ordered sequence.

Expected CSV format:
  - Each row represents one day's conversation.
  - A column (configurable) contains the conversation text for that day.
  - Messages within a day are separated by newlines.
"""

import pandas as pd
import re
from typing import List, Dict
from pathlib import Path


def load_csv(file_path: str, text_column: str | None = None) -> pd.DataFrame:
    """Load a CSV file into a DataFrame."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")
    df = pd.read_csv(file_path)
    return df


def _detect_text_column(df: pd.DataFrame) -> str:
    """Auto-detect the column containing conversation text."""
    # Priority: look for columns with common names
    candidates = ["conversation", "text", "message", "messages", "content", "chat"]
    for col in df.columns:
        if col.strip().lower() in candidates:
            return col
    # Fallback: pick the column with the longest average string length
    str_cols = df.select_dtypes(include=["object"]).columns
    if len(str_cols) == 0:
        raise ValueError("No text columns found in CSV.")
    avg_lengths = {col: df[col].astype(str).str.len().mean() for col in str_cols}
    return max(avg_lengths, key=avg_lengths.get)


def _parse_messages_from_text(text: str) -> List[Dict[str, str]]:
    """
    Parse individual messages from a conversation text block.
    Handles formats like:
      - "User: message"
      - "Bot: message"
      - Plain newline-separated messages
    """
    if not isinstance(text, str) or not text.strip():
        return []

    messages = []
    lines = text.strip().split("\n")

    # Try to detect "Speaker: message" pattern
    speaker_pattern = re.compile(r"^([A-Za-z0-9_\s]+?):\s*(.+)$")

    for line in lines:
        line = line.strip()
        if not line:
            continue

        match = speaker_pattern.match(line)
        if match:
            speaker = match.group(1).strip()
            content = match.group(2).strip()
            messages.append({"speaker": speaker, "content": content})
        else:
            messages.append({"speaker": "unknown", "content": line})

    return messages


def flatten_messages(
    file_path: str,
    text_column: str | None = None,
    date_column: str | None = None,
) -> List[Dict]:
    """
    Load CSV and flatten all messages into a single chronological sequence.

    Returns:
        List of dicts: [{"index": 0, "speaker": "...", "content": "...", "day": 0}, ...]
    """
    df = load_csv(file_path)

    # Detect text column
    if text_column is None:
        text_column = _detect_text_column(df)

    # Sort by date if date column exists
    if date_column and date_column in df.columns:
        df = df.sort_values(by=date_column).reset_index(drop=True)

    all_messages: List[Dict] = []
    global_index = 0

    for day_idx, row in df.iterrows():
        day_text = row[text_column]
        day_messages = _parse_messages_from_text(str(day_text))

        for msg in day_messages:
            all_messages.append(
                {
                    "index": global_index,
                    "speaker": msg["speaker"],
                    "content": msg["content"],
                    "day": int(day_idx),
                }
            )
            global_index += 1

    return all_messages


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python data_loader.py <csv_path>")
        sys.exit(1)

    messages = flatten_messages(sys.argv[1])
    print(f"Loaded {len(messages)} messages")
    for m in messages[:5]:
        print(f"  [{m['index']}] {m['speaker']}: {m['content'][:80]}")
