"""
main.py – FastAPI backend for the Conversation Analysis RAG System.

Endpoints:
  POST /upload       – Upload a CSV file and process it
  POST /chat         – Chat with the RAG system
  GET  /persona      – Get extracted persona
  GET  /topics       – Get detected topics
  GET  /checkpoints  – Get 100-message checkpoint summaries
  GET  /health       – Health check
"""

import os
import json
import shutil
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from data_loader import flatten_messages
from topic_segmentation import detect_topic_changes
from summarizer import summarize_topics, create_checkpoint_summaries
from rag import RAGSystem
from persona import extract_persona

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Conversation Analysis RAG System",
    description="RAG-based conversation analysis with topic segmentation and persona extraction",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Global state
# ---------------------------------------------------------------------------
DATA_DIR = Path("./data")
DATA_DIR.mkdir(exist_ok=True)

rag_system = RAGSystem()
persona_data: dict = {}
topics_data: list = []
checkpoints_data: list = []
messages_data: list = []
is_processed = False


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class ChatRequest(BaseModel):
    query: str


class ChatResponse(BaseModel):
    response: str
    retrieved_topics: list = []
    retrieved_messages: list = []


# ---------------------------------------------------------------------------
# Processing pipeline
# ---------------------------------------------------------------------------
def process_csv(file_path: str):
    """Run the full processing pipeline on a CSV file."""
    global rag_system, persona_data, topics_data
    global checkpoints_data, messages_data, is_processed
    import time

    t0 = time.time()

    print("[1/5] Loading and flattening messages...")
    messages = flatten_messages(file_path)
    messages_data = messages
    print(f"  -> {len(messages)} messages loaded ({time.time()-t0:.1f}s)")

    if not messages:
        raise ValueError("No messages found in the CSV file.")

    print("[2/5] Detecting topic changes (this is the slow step)...")
    t1 = time.time()
    segments, embeddings = detect_topic_changes(messages, threshold=0.35)
    print(f"  Topic detection done ({time.time()-t1:.1f}s)")

    print("[3/5] Generating topic summaries...")
    t2 = time.time()
    # Cap summaries: only summarize up to 200 topics to avoid T5 taking forever
    if len(segments) > 200:
        print(f"  {len(segments)} topics found, summarizing first 200...")
        segments_to_summarize = segments[:200]
        segments_to_summarize = summarize_topics(segments_to_summarize)
        # Give remaining topics a placeholder summary
        for seg in segments[200:]:
            msgs = seg.get("messages", [])
            seg["summary"] = " ".join(m["content"] for m in msgs[:3])[:150] + "..."
        segments[:200] = segments_to_summarize
    else:
        segments = summarize_topics(segments)
    topics_data = segments
    print(f"  Summaries done ({time.time()-t2:.1f}s)")

    print("[4/5] Creating checkpoint summaries...")
    t3 = time.time()
    # For very large datasets, use larger checkpoint size
    ckpt_size = 100 if len(messages) < 5000 else 500
    checkpoints = create_checkpoint_summaries(messages, checkpoint_size=ckpt_size)
    checkpoints_data = checkpoints
    print(f"  -> {len(checkpoints)} checkpoints created ({time.time()-t3:.1f}s)")

    print("[5/5] Extracting persona and building RAG index...")
    t4 = time.time()
    persona_data = extract_persona(messages)

    rag_system = RAGSystem()
    rag_system.index_messages(messages, embeddings)
    rag_system.index_topics(segments)
    rag_system.index_checkpoints(checkpoints)

    is_processed = True
    total = time.time() - t0
    print(f"[OK] Processing complete! Total time: {total:.1f}s")


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.get("/health")
def health_check():
    return {"status": "ok", "processed": is_processed}


@app.post("/upload")
async def upload_csv(file: UploadFile = File(...)):
    """Upload and process a CSV file."""
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are accepted.")

    save_path = DATA_DIR / file.filename
    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        process_csv(str(save_path))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")

    return {
        "message": "File processed successfully",
        "total_messages": len(messages_data),
        "total_topics": len(topics_data),
        "total_checkpoints": len(checkpoints_data),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Chat with the RAG system."""
    if not is_processed:
        raise HTTPException(
            status_code=400,
            detail="No data processed yet. Please upload a CSV file first.",
        )

    result = rag_system.generate_answer(
        query=request.query,
        persona=persona_data,
        top_k_topics=3,
        top_k_messages=5,
    )

    return ChatResponse(
        response=result["response"],
        retrieved_topics=result["retrieved_topics"],
        retrieved_messages=result["retrieved_messages"],
    )


@app.get("/persona")
def get_persona():
    """Get extracted user persona."""
    if not is_processed:
        raise HTTPException(status_code=400, detail="No data processed yet.")
    return persona_data


@app.get("/topics")
def get_topics():
    """Get detected topic segments."""
    if not is_processed:
        raise HTTPException(status_code=400, detail="No data processed yet.")
    # Strip messages from response to keep it lightweight
    return [
        {
            "topic_id": t["topic_id"],
            "start_index": t["start_index"],
            "end_index": t["end_index"],
            "summary": t.get("summary", ""),
        }
        for t in topics_data
    ]


@app.get("/checkpoints")
def get_checkpoints():
    """Get 100-message checkpoint summaries."""
    if not is_processed:
        raise HTTPException(status_code=400, detail="No data processed yet.")
    return checkpoints_data


# ---------------------------------------------------------------------------
# Auto-process if a default CSV exists
# ---------------------------------------------------------------------------
@app.on_event("startup")
def startup_event():
    """Auto-process data/conversations.csv if it exists."""
    default_csv = DATA_DIR / "conversations.csv"
    if default_csv.exists():
        print(f"Found default CSV: {default_csv}")
        try:
            process_csv(str(default_csv))
        except Exception as e:
            print(f"Warning: Failed to auto-process {default_csv}: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
