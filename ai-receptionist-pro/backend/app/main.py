import os
import json
import base64
import asyncio
from fastapi import FastAPI, WebSocket, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from dotenv import load_dotenv
import websockets
from .db import save_call, get_settings

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_REALTIME_MODEL = os.getenv("OPENAI_REALTIME_MODEL", "gpt-4o-realtime-preview")
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@demo.it")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "password")

app = FastAPI(title="AI Receptionist Pro")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"ok": True, "app": "AI Receptionist Pro", "status": "online"}

@app.post("/api/login")
async def login(request: Request):
    data = await request.json()
    if data.get("email") == ADMIN_EMAIL and data.get("password") == ADMIN_PASSWORD:
        return {"token": "demo-admin-token"}
    raise HTTPException(status_code=401, detail="Credenziali errate")

@app.get("/api/settings")
def settings():
    return get_settings()

@app.get("/api/calls")
def calls():
    return {"items": []}

@app.api_route("/twilio/incoming-call", methods=["GET", "POST"])
async def incoming_call(request: Request):
    host = PUBLIC_BASE_URL.replace("https://", "").replace("http://", "").rstrip("/")
    if not host:
        host = request.url.hostname
    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say language="it-IT" voice="Polly.Bianca">Ciao, ti passo al nostro assistente virtuale.</Say>
  <Connect>
    <Stream url="wss://{host}/media-stream" />
  </Connect>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

async def send_openai_session(openai_ws):
    settings = get_settings()
    instructions = f"""
Sei {settings.get('assistant_name')} per {settings.get('company_name')}.
{settings.get('system_prompt')}
FAQ aziendali:
{settings.get('faq')}
Regole:
- Parla in italiano.
- Frasi brevi.
- Chiedi nome e motivo della chiamata.
- Se il cliente chiede informazioni non presenti, raccogli il recapito e prometti ricontatto.
- Non dire di essere ChatGPT.
"""
    await openai_ws.send(json.dumps({
        "type": "session.update",
        "session": {
            "modalities": ["text", "audio"],
            "instructions": instructions,
            "voice": "alloy",
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "turn_detection": {"type": "server_vad"},
            "temperature": 0.7
        }
    }))

@app.websocket("/media-stream")
async def media_stream(websocket: WebSocket):
    await websocket.accept()
    if not OPENAI_API_KEY:
        await websocket.close(code=1011)
        return

    stream_sid = None
    call_sid = None
    openai_url = f"wss://api.openai.com/v1/realtime?model={OPENAI_REALTIME_MODEL}"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "OpenAI-Beta": "realtime=v1"
    }

    async with websockets.connect(openai_url, additional_headers=headers) as openai_ws:
        await send_openai_session(openai_ws)

        async def from_twilio():
            nonlocal stream_sid, call_sid
            async for message in websocket.iter_text():
                data = json.loads(message)
                event = data.get("event")
                if event == "start":
                    stream_sid = data["start"]["streamSid"]
                    call_sid = data["start"].get("callSid")
                    save_call({"call_sid": call_sid, "event_type": "start", "summary": "Chiamata iniziata"})
                elif event == "media":
                    await openai_ws.send(json.dumps({
                        "type": "input_audio_buffer.append",
                        "audio": data["media"]["payload"]
                    }))
                elif event == "stop":
                    save_call({"call_sid": call_sid, "event_type": "stop", "summary": "Chiamata terminata"})
                    break

        async def from_openai():
            async for message in openai_ws:
                data = json.loads(message)
                if data.get("type") == "response.audio.delta" and data.get("delta") and stream_sid:
                    await websocket.send_json({
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": data["delta"]}
                    })

        await asyncio.gather(from_twilio(), from_openai())
