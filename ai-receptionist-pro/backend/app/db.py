import os
from datetime import datetime, timezone
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

_client: Client | None = None


def db() -> Client | None:
    global _client
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return None
    if _client is None:
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _client


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def save_call(event: dict) -> None:
    client = db()
    if not client:
        print("Supabase non configurato. Evento:", event)
        return
    payload = {"created_at": now_iso(), **event}
    client.table("calls").insert(payload).execute()


def get_settings() -> dict:
    client = db()
    defaults = {
        "assistant_name": os.getenv("DEFAULT_ASSISTANT_NAME", "AI Receptionist Pro"),
        "company_name": os.getenv("DEFAULT_COMPANY_NAME", "La tua azienda"),
        "notify_email": os.getenv("DEFAULT_NOTIFY_EMAIL", ""),
        "system_prompt": "Rispondi come receptionist telefonico. Parla in italiano. Sii breve. Raccogli nome, motivo della chiamata, telefono ed email. Se serve, proponi un appuntamento. Non inventare informazioni.",
        "faq": "Orari: dal lunedì al venerdì, 9:00-18:00. Indirizzo: da configurare."
    }
    if not client:
        return defaults
    res = client.table("settings").select("*").limit(1).execute()
    if res.data:
        return {**defaults, **res.data[0]}
    client.table("settings").insert(defaults).execute()
    return defaults
