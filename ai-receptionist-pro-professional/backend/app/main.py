import os
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from .db import get_supabase

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

@app.get("/")
def home():
    return {"ok": True, "app": "AI Receptionist Pro", "status": "online"}

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/assistants")
def list_assistants():
    sb = get_supabase()
    res = sb.table("assistants").select("*").order("created_at", desc=True).execute()
    return {"items": res.data}

@app.post("/assistants")
def create_assistant(data: AssistantIn):
    sb = get_supabase()
    res = sb.table("assistants").insert(data.model_dump()).execute()
    return {"item": res.data[0] if res.data else None}

@app.put("/assistants/{assistant_id}")
def update_assistant(assistant_id: str, data: AssistantIn):
    sb = get_supabase()
    res = sb.table("assistants").update(data.model_dump()).eq("id", assistant_id).execute()
    return {"item": res.data[0] if res.data else None}

@app.delete("/assistants/{assistant_id}")
def delete_assistant(assistant_id: str):
    sb = get_supabase()
    sb.table("assistants").delete().eq("id", assistant_id).execute()
    return {"ok": True}

@app.get("/faqs")
def list_faqs(assistant_id: Optional[str] = None):
    sb = get_supabase()
    q = sb.table("faqs").select("*").order("created_at", desc=True)
    if assistant_id:
        q = q.eq("assistant_id", assistant_id)
    res = q.execute()
    return {"items": res.data}

@app.post("/faqs")
def create_faq(data: FaqIn):
    sb = get_supabase()
    res = sb.table("faqs").insert(data.model_dump()).execute()
    return {"item": res.data[0] if res.data else None}

@app.delete("/faqs/{faq_id}")
def delete_faq(faq_id: str):
    sb = get_supabase()
    sb.table("faqs").delete().eq("id", faq_id).execute()
    return {"ok": True}

@app.get("/calls")
def list_calls():
    sb = get_supabase()
    res = sb.table("calls").select("*").order("created_at", desc=True).limit(100).execute()
    return {"items": res.data}

@app.post("/test-chat")
def test_chat(data: TestChatIn):
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY mancante su Render")

    sb = get_supabase()
    assistant_res = sb.table("assistants").select("*").eq("id", data.assistant_id).limit(1).execute()
    if not assistant_res.data:
        raise HTTPException(status_code=404, detail="Assistente non trovato")
    assistant = assistant_res.data[0]

    faqs_res = sb.table("faqs").select("question,answer").eq("assistant_id", data.assistant_id).execute()
    faq_text = "\n".join([f"D: {x['question']}\nR: {x['answer']}" for x in faqs_res.data])

    client = OpenAI(api_key=api_key)
    system = f"""{assistant.get('system_prompt','')}

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
