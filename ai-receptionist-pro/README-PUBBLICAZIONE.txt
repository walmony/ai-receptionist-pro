AI Receptionist Pro, pubblicazione rapida

1. Supabase
Crea un progetto Supabase.
Apri SQL Editor.
Incolla il contenuto di backend/supabase.sql.
Esegui.
Copia Project URL e Service Role Key.

2. Backend Render
Crea un nuovo Web Service su Render.
Collega la cartella backend.
Build command:
pip install -r requirements.txt
Start command:
uvicorn app.main:app --host 0.0.0.0 --port $PORT

Variabili Render:
OPENAI_API_KEY
OPENAI_REALTIME_MODEL=gpt-4o-realtime-preview
PUBLIC_BASE_URL=https://nome-backend.onrender.com
SUPABASE_URL
SUPABASE_SERVICE_ROLE_KEY
ADMIN_EMAIL
ADMIN_PASSWORD
DEFAULT_COMPANY_NAME
DEFAULT_NOTIFY_EMAIL

3. Frontend Vercel
Collega la cartella frontend.
Framework: Vite.
Variabile Vercel:
VITE_API_URL=https://nome-backend.onrender.com

4. Twilio
Compra o usa un numero Voice.
Nel numero, imposta webhook chiamata in arrivo:
https://nome-backend.onrender.com/twilio/incoming-call
Metodo: POST

5. Test
Chiama il numero Twilio.
L'assistente risponde in italiano.
Apri il frontend Vercel.
Accedi con ADMIN_EMAIL e ADMIN_PASSWORD.
