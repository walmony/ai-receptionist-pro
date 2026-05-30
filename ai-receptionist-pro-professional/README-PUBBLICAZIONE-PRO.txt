AI Receptionist Pro, versione professionale iniziale

Questa versione sostituisce la demo.

Contiene:
- Backend FastAPI compatibile con Render
- Frontend React Vite compatibile con Vercel
- Dashboard amministratore
- Gestione assistenti
- Gestione FAQ
- Storico chiamate
- Test AI testuale con OpenAI

Percorsi corretti:

Render
Root Directory:
ai-receptionist-pro/backend

Build Command:
pip install -r requirements.txt

Start Command:
uvicorn app.main:app --host 0.0.0.0 --port $PORT

Environment Variables Render:
PYTHON_VERSION=3.11.9
SUPABASE_URL=https://vkdsqgyrxgfufxxehsjf.supabase.co
SUPABASE_SERVICE_KEY=la tua chiave segreta completa
OPENAI_API_KEY=la tua chiave OpenAI completa
FRONTEND_URL=https://il-tuo-url-vercel.vercel.app

Vercel
Root Directory:
ai-receptionist-pro/frontend

Environment Variables Vercel:
VITE_API_URL=https://ai-receptionist-pro-backend.onrender.com

Nota importante:
Il login della dashboard è temporaneo.
Accetta qualsiasi email e password non vuote.
Nella prossima versione va collegato a Supabase Auth.
