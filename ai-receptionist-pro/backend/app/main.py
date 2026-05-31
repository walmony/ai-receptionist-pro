import os
from typing import Optional

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from pydantic import BaseModel

from .db import supabase_headers, supabase_rest_url

app = FastAPI(title="AI Receptionist Pro")

FRONTEND_URL = os.getenv("FRONTEND_URL", "*")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if FRONTEND_URL == "*" else [FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class AssistantIn(BaseModel):
    name: str
    business_name: Optional[str] = ""
    system_prompt: str
    language: str = "it"
    voice: str = "alloy"
    email_to: Optional[str] = ""

class FaqIn(BaseModel):
    assistant_id: str
    question: str
    answer: str

class TestChatIn(BaseModel):
    assistant_id: str
    message: str

def supabase_get(table, params=None):
    r = httpx.get(
        supabase_rest_url(table),
        headers=supabase_headers(),
        params=params or {},
        timeout=20
    )
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()

def supabase_post(table, payload):
    r = httpx.post(
        supabase_rest_url(table),
        headers=supabase_headers(),
        json=payload,
        timeout=20
    )
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()

def supabase_patch(table, row_id, payload):
    r = httpx.patch(
        supabase_rest_url(table),
        headers=supabase_headers(),
        params={"id": f"eq.{row_id}"},
        json=payload,
        timeout=20
    )
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return r.json()

def supabase_delete(table, row_id):
    r = httpx.delete(
        supabase_rest_url(table),
        headers=supabase_headers(),
        params={"id": f"eq.{row_id}"},
        timeout=20
    )
    if r.status_code >= 400:
        raise HTTPException(status_code=r.status_code, detail=r.text)
    return True

@app.get("/")
def home():
    return {"ok": True, "app": "AI Receptionist Pro", "status": "online"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/assistants")
def list_assistants():
    items = supabase_get(
        "assistants",
        {
            "select": "*",
            "order": "created_at.desc"
        }
    )
    return {"items": items}

@app.post("/assistants")
def create_assistant(data: AssistantIn):
    items = supabase_post("assistants", data.model_dump())
    return {"item": items[0] if items else None}

@app.put("/assistants/{assistant_id}")
def update_assistant(assistant_id: str, data: AssistantIn):
    items = supabase_patch("assistants", assistant_id, data.model_dump())
    return {"item": items[0] if items else None}

@app.delete("/assistants/{assistant_id}")
def delete_assistant(assistant_id: str):
    supabase_delete("assistants", assistant_id)
    return {"ok": True}

@app.get("/faqs")
def list_faqs(assistant_id: Optional[str] = None):
    params = {
        "select": "*",
        "order": "created_at.desc"
    }

    if assistant_id:
        params["assistant_id"] = f"eq.{assistant_id}"

    items = supabase_get("faqs", params)
    return {"items": items}

@app.post("/faqs")
def create_faq(data: FaqIn):
    items = supabase_post("faqs", data.model_dump())
    return {"item": items[0] if items else None}

@app.delete("/faqs/{faq_id}")
def delete_faq(faq_id: str):
    supabase_delete("faqs", faq_id)
    return {"ok": True}

@app.get("/calls")
def list_calls():
    items = supabase_get(
        "calls",
        {
            "select": "*",
            "order": "created_at.desc",
            "limit": "100"
        }
    )
    return {"items": items}

@app.post("/test-chat")
def test_chat(data: TestChatIn):
    api_key = os.getenv("OPENAI_API_KEY", "")

    if not api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY mancante su Render")

    assistants = supabase_get(
        "assistants",
        {
            "select": "*",
            "id": f"eq.{data.assistant_id}",
            "limit": "1"
        }
    )

    if not assistants:
        raise HTTPException(status_code=404, detail="Assistente non trovato")

    assistant = assistants[0]

    faqs = supabase_get(
        "faqs",
        {
            "select": "question,answer",
            "assistant_id": f"eq.{data.assistant_id}"
        }
    )

    faq_text = "\n".join([
        f"D: {x.get('question', '')}\nR: {x.get('answer', '')}"
        for x in faqs
    ])

    client = OpenAI(api_key=api_key)

    system = f"""{assistant.get("system_prompt", "")}

Usa queste FAQ quando servono:
{faq_text}

Rispondi in italiano. Sii breve, chiaro e professionale."""

    completion = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": data.message},
        ],
    )

    return {"reply": completion.choices[0].message.content}
